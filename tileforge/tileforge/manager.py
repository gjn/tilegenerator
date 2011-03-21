import os
import logging
import time
from datetime import datetime, timedelta
from threading import Thread
from socket import gethostname

from tileforge.generator import Generator

from tileforge.utils.list import TodoList
from tileforge.utils.layer import grid
from tileforge.utils.vector import vector
from tileforge.utils.mail import send_email
from tileforge.utils.retry import dump
from tileforge.utils.file import mkdir

logger = logging.getLogger(__name__)

class Manager(object):
    def __init__(self, layer, cache, bbox=None, levels=None, tiles=None,
                 threads=1, metadata={}):
        self.metadata = metadata
        self.generators = []
        self.layer = layer
        self.fatal = False

        if tiles:
            self.tiles = TodoList(tiles)
        else:
            self.tiles = TodoList(self.init_grid(layer, bbox, levels))

        for thread in range(threads):
            generator = Generator(layer, cache,
                                  tiles=self.tiles,
                                  on_failure=self.error_handler,
                                  on_success=self.success_handler)
            self.generators.append(generator)

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

        self.error_threshold = int(self.metadata.get("errors_generatemin", "10"));
        self.error_ratio = int(self.metadata.get("errors_succesratio", "1000"))

    def init_grid(self, layer, bbox, levels):
        connection = layer.metadata.get("connection")
        data = layer.metadata.get("data")
        if connection and data:
            logger.info("generating from postgis query")
            return vector(layer, bbox, levels, connection, data)
        else:
            logger.info("generating all tiles")
            return grid(layer, bbox, levels)

    def start(self):
        [g.start() for g in self.generators]
        self.stats.start()
        self.started_at = time.time()

    def join(self):
        [g.join() for g in self.generators]
        self.stats.join()
        self.stopped_at = time.time()
        self.error_logs.close()
        self.send_notification_email()
        return len(self.tiles.failure) == 0

    def success_handler(self, tile, durations=None, *args, **kwargs):
        coords = (tile.x, tile.y, tile.z)
        self.tiles.task_done(coords)
        logger.info("generated tile: (x: %04d, y: %04d, z: %02d) duration: (render: %.3fs, post-proc: %.3fs, save: %.3fs)"%(coords + durations))

    def error_handler(self, tile, fatal=False, message=None, *args, **kwargs):
        if not self.fatal:
            self.fatal = fatal
            # self.fatal = fatal or self.tiles.success_count + self.tiles.failure_count > self.error_threshold \
            #     and self.tiles.success_count / self.tiles.failure_count < self.error_ratio
            now = datetime.fromtimestamp(int(time.time()))
            if self.fatal:
                self.error_logs.write("(FATAL ERROR) === %s ===\n%s\n"%(now, message))
                self.abort()
            else:
                # normal error
                coords = (tile.x, tile.y, tile.z)
                logger.info("can't generated (%04d, %04d, %02d)"%(coords))
                self.error_logs.write("(%04d, %04d, %02d) === %s ===\n%s\n"%(coords + (now, message)))
                self.error_logs.flush()

                self.tiles.task_done(coords, errors=True)

    def running(self):
        return [thread for thread in self.generators if thread.isAlive()]

    def write_status(self, dirname, interval):
        if not mkdir(dirname):
            logger.warning("can't write stats to '%s'"%dirname)
            return

        filename = os.path.join(dirname, self.layer.name)
        while True:
            values = "%d:%d:%d"%(self.tiles.success_count, self.tiles.failure_count,
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
        [g.stop() for g in self.generators]

    def send_notification_email(self):
        attachements = []
        body_text  = "started at: %s\n"%(datetime.fromtimestamp(int(self.started_at)))
        body_text += "ended at: %s\n"%(datetime.fromtimestamp(int(self.stopped_at)))
        body_text += "%d threads have generate %d tiles in %s (%.1f tiles/s)"
        body_text %= (len(self.generators), 
                       self.tiles.success_count, 
                       timedelta(seconds=int(self.stopped_at-self.started_at)),
                       self.tiles.success_count/(self.stopped_at-self.started_at))
        
        if len(self.tiles.failure) or self.fatal:
            logger.info("errors saved to %s"%self.error_logs.name)
            if not self.fatal:
                tiles = os.path.join(self.error_dir, self.layer.name + ".retry")
                logger.info("retry file saved to %s"%tiles)

                dump(self.layer, [item.get("item") for item in self.tiles.failure], open(tiles, 'w'))
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
            send_email(to=mail_to, sender=self.metadata.get("mail_from", "tileforge@example.com"),
                       subject=subject.replace('%layer', self.layer.name).replace('%host', gethostname()),
                       body_text=body_text, files=attachements,
                       server=self.metadata.get("mail_server_host", "localhost"),
                       port=int(self.metadata.get("mail_server_port", "25")))
            logger.info("notification e-mail sent to %s"%mail_to)
        else:
            logger.warning("no 'mail_to' option found. no e-mail sent.")
