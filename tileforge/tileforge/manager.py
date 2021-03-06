import os
import sys
import logging
import time
from collections import deque
from datetime import datetime, timedelta
from threading import Thread
from multiprocessing import Pool
from socket import gethostname

from tileforge.generator import init, run

from tileforge.utils.layer import grid
from tileforge.utils.vector import vector
from tileforge.utils.mail import send_email
from tileforge.utils.retry import dump
from tileforge.utils.file import mkdir

logger = logging.getLogger(__name__)

class Manager(object):
    def __init__(self, layer, cache, bbox=None, levels=None, tiles=None,
                 threads=1, metadata={}, dry_run=False):
        self.metadata = metadata
        self.layer = layer
        self.bbox = bbox
        self.levels = levels
        self.fatal = False
        self.poolsize = threads
        self.duration = {'render': 0.0, 'post-proc': 0.0, 'save': 0.0}

        self.success_count = 0
        self.failures = deque()

        self.tiles = tiles or self.init_grid()
        
        if dry_run:
            logger.info("tiles to be generated: %d" % len([t for t in self.tiles]))
            sys.exit()
            
        self.pool = Pool(self.poolsize, init, (self.layer, cache))
        self.results = self.pool.imap_unordered(run, self.tiles)
        self.pool.close()

        # stats
        stats_dir = self.metadata.get("stats_dir", "/tmp/tileforge/stats")
        stats_interval = float(self.metadata.get("stats_interval", "2"))
        self.stats = Thread(target=self.write_status, args=(stats_dir, stats_interval))

        # errors
        self.error_dir = self.metadata.get("error_dir", "/tmp/tileforge/errors")
        if mkdir(self.error_dir):
            self.error_logs = open(os.path.join(self.error_dir, self.layer.name + ".txt"), 'a')
            self.error_logs.truncate(0)
        else:
            raise Exception("can't write errors to '%s'"%self.error_dir)

        # self.error_threshold = int(self.metadata.get("errors_generatemin", "10"));
        # self.error_ratio = int(self.metadata.get("errors_succesratio", "1000"))

    def init_grid(self):
        connection = self.layer.metadata.get("connection")
        data = self.layer.metadata.get("data")
        if connection and data:
            logger.info("generating from postgis query")
            return vector(self.layer, self.bbox, self.levels, connection, data)
        else:
            logger.info("generating all tiles")
            return grid(self.layer, self.bbox, self.levels)

    def start(self):
        self.stats.start()
        self.started_at = time.time()

    def join(self):
        for status, coords, result in self.results:
            if status:
                self.success_handler(coords, durations=result)
            else:
                self.error_handler(coords, message=result)

        self.pool.join()

        self.stats.join()
        self.stopped_at = time.time()
        self.error_logs.close()
        self.send_notification_email()
        return len(self.failures) == 0

    def success_handler(self, coords, durations):
        self.success_count += 1
        str_coords = "(x: %04d, y: %04d, z: %02d)"%coords
        str_durations = "(render: %.3fs, post-proc: %.3fs, save: %.3fs)"%durations
        logger.info("'%s': generated tile: %s %s"%(self.layer.name, str_coords, str_durations))
        self.duration['render'] += durations[0]
        self.duration['post-proc'] += durations[1]
        self.duration['save'] += durations[2]

    def error_handler(self, coords, fatal=False, message=None):
        if not self.fatal:
            self.fatal = fatal
            # FIXME: check max errors
            now = datetime.fromtimestamp(int(time.time()))
            if self.fatal:
                self.error_logs.write("(FATAL ERROR) === %s ===\n%s\n"%(now, message))
                self.abort()
            else:
                # normal error
                str_coords = "(x: %04d, y: %04d, z: %02d)"%coords
                logger.info("can't generate %s (%s)"%(str_coords,message))
                self.error_logs.write("%s === %s ===\n%s\n"%(str_coords, now, message))
                self.error_logs.flush()
                self.failures.append(coords)

    def running(self):
        return [p for p in self.pool._pool if p.is_alive()]

    def write_status(self, dirname, interval):
        if not mkdir(dirname):
            logger.warning("can't write stats to '%s'"%dirname)
            return

        filename = os.path.join(dirname, self.layer.name)
        while True:
            values = "%d:%d:%d"%(self.success_count, len(self.failures),
                                 len(self.running()))
            stats = open(filename, 'w')
            stats.write(values)
            stats.close()
            if self.running():
                time.sleep(interval)
            else:
                # no more generators are running
                return

    def abort(self):
        self.pool.terminate()

    def send_notification_email(self):
        attachements = []
        body_text  = "started at: %s\n"%(datetime.fromtimestamp(int(self.started_at)))
        body_text += "ended at: %s\n"%(datetime.fromtimestamp(int(self.stopped_at)))

        times_stats  = "%d threads have generate %d tiles in %s (%.1f tiles/s)"
        times_stats %= (self.poolsize,
                       self.success_count,
                       timedelta(seconds=int(self.stopped_at-self.started_at)),
                       self.success_count/(self.stopped_at-self.started_at))
        logger.info(times_stats)
        body_text += times_stats + "\n"

        if self.success_count > 0:
            times_stats  = "average time: render = %.3fs, post-proc = %.3fs, save = %.3fs"
            times_stats %= (self.duration['render'] / self.success_count,
                          self.duration['post-proc'] / self.success_count,
                          self.duration['save'] / self.success_count)
            logger.info(times_stats)
            body_text += times_stats + "\n\n"

        body_text += "Uses metatiling: %s\n"%(self.layer.metaTile)
        body_text += "WMTS dimension: %s\n"%(self.layer.metadata.get("dimension", "n/a"))
        body_text += "WMTS matrix set: %s\n"%(self.layer.metadata.get("matrix_set", "n/a"))
        body_text += "bounding box: %s\n"%(str(self.bbox))
        body_text += "levels: %s\n"%(str(self.levels))

        if len(self.failures) or self.fatal:
            logger.info("errors saved to %s"%self.error_logs.name)
            if not self.fatal:
                tiles = os.path.join(self.error_dir, self.layer.name + "." + str(int(time.time()))  + ".retry")
                logger.info("retry file saved to %s"%tiles)

                #dump(self.layer, [item.get("item") for item in self.failures], open(tiles, 'w'))
                dump(self.layer, self.failures, open(tiles, 'w'))
                attachements.append(tiles)

            subject = self.metadata.get("mail_subject_error",
                                        "error while generating layer '%layer' on host '%host'")
            # fixme: display cmd line to retry
            body_text += "\n\nErrors list:\n\n%s"%open(self.error_logs.name).read()
        else:
            subject = self.metadata.get("mail_subject_success",
                                        "all tiles generated for layer '%layer' on host '%host'")
            body_text += "\n\nWithout any errors!"
        if self.metadata.get("mail_to"):
            mail_to = [mail.strip() for mail in self.metadata.get("mail_to").split(",")]
            send_email(to=mail_to, sender=self.metadata.get("mail_from", "tileforge@camptocamp.com"),
                       subject=subject.replace('%layer', self.layer.name).replace('%host', gethostname()),
                       body_text=body_text, files=attachements,
                       server=self.metadata.get("mail_server_host", "localhost"),
                       port=int(self.metadata.get("mail_server_port", "25")))
            logger.info("notification e-mail sent to %s"%mail_to)
        else:
            logger.warning("no 'mail_to' option found. no e-mail sent.")
