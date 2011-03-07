import logging
import os
import sys
from optparse import OptionParser

from TileCache import Service

from tileforge import __version__
from tileforge.manager import Manager

from tileforge.utils.retry import load
from tileforge.utils.wmts import wmts_capabilities

logger = logging.getLogger(__name__)

def main():
    usage = "%prog [OPTIONS] LAYERNAME [ZOOM_START ZOOM_STOP]"
    parser = OptionParser(usage=usage, version="%prog " + __version__)
    parser.add_option("-c", "--config", default="tilecache.cfg",
                      help="path to configuration file")
    parser.add_option("-b","--bbox",
                      help="restrict to specified bounding box")
    parser.add_option("-t","--threads", type="int", default=5,
                      help="number of concurrent threads to run (defaults is 5)")

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

    if options.retry is not None:
        layername, tiles = load(open(options.retry, 'r'))
        bbox = levels = None
    else:
        tiles = None
        if len(args) >= 1:
            layername = args[0]
        else:
            parser.error("missing LAYERNAME argument")

    if not os.access(options.config, os.R_OK):
        parser.error("can't read config file '%s'"%options.config)

    service = Service.load(options.config)
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
                      metadata=service.metadata)
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


