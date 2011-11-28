import logging
import os
import sys
import ConfigParser
from multiprocessing import cpu_count
from optparse import OptionParser

from TileCache import Service

from tileforge import __version__
from tileforge.manager import Manager

from tileforge.utils.retry import load
from tileforge.utils.wmts import wmts_capabilities

logger = logging.getLogger(__name__)

def main():
    default_threads = cpu_count()
    usage = "%prog [OPTIONS] LAYERNAME [ZOOM_START ZOOM_STOP]"
    parser = OptionParser(usage=usage, version="%prog " + __version__)
    parser.add_option("-c", "--config", default="tilecache.cfg",
                      help="path to configuration file")
    parser.add_option("-b","--bbox",
                      help="restrict to specified bounding box")
    parser.add_option("-t","--threads", type="int", default=default_threads,
                      help="number of concurrent threads to run (defaults is %d)"%default_threads)

    parser.add_option("-d", "--dry_run",
                      action="store_true", dest="dry_run", default=False)

    parser.add_option("-r","--retry",
                      help="retry to generated tiles from RETRY file")

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="make lots of noise")

    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not os.access(options.config, os.R_OK):
        parser.error("can't read config file '%s'"%options.config)


    # attenpt to get the extends option in the metadata section
    config = ConfigParser.ConfigParser()
    config.read(options.config)
    if config.has_option('metadata', 'extends'):
        files = config.get('metadata', 'extends').split()
        files = [os.path.join(os.path.dirname(options.config), path) for path in files]
        options.config = files + [options.config]
    else:
        options.config = [options.config]

    service = Service.load(*options.config)

    if options.retry is not None:
        layername, tiles = load(open(options.retry, 'r'), service)
        bbox = levels = None
    else:
        tiles = None
        if len(args) >= 1:
            layername = args[0]
        else:
            parser.error("missing LAYERNAME argument")

    layer = service.layers.get(layername)

    if "exception" in service.metadata:
        parser.error(str(service.metadata.get("exception")))

    if layer is None:
        parser.error("can't find layer '%s' in '%s'"%(layername, options.config))

    if not tiles:
        if options.bbox:
            bbox = tuple(float(i) for i in options.bbox.split(","))
        else:
            bbox = layer.bbox

        if len(args) == 3:
            levels = tuple((int(args[1]), int(args[2])))
        else:
            levels = (0, len(layer.resolutions))

    manager = Manager(layer, service.cache, bbox=bbox, levels=levels,
                      tiles=tiles, threads=options.threads,
                      metadata=service.metadata, dry_run=options.dry_run)
    manager.start()
    if manager.join():
        if "wmts_capabilites_path" in service.metadata:
            if not hasattr(service.cache, "write"):
                logger.warning("can't save WMTS capabilities: not supported by the cache")
                sys.exit(1)
            else:
                data = wmts_capabilities(service.layers.values(), service.metadata)
                path = service.metadata["wmts_capabilites_path"]
                service.cache.write(data, path)
                logger.info("WMTS capabilities saved to '%s'"%path)
                sys.exit(0)
    else:
        sys.exit(1)


