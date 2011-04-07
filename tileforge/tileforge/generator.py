import time
import logging
from TileCache.Layer import Tile
from tileforge.utils.file import run as run_external

__ALL__ = ['init', 'all']

layer = None
cache = None
logger = logging.getLogger(__name__)

def init(l, c):
    global layer, cache
    layer = l
    cache = c

def run(coords):
    try:
        tile = Tile(layer, *coords)
        times = []
        image, duration = render(layer, tile)
        times.append(duration)

        image, duration = image_postproc(layer, tile, image)
        times.append(duration)

        duration = save(cache, tile, image)
        times.append(duration)

        return True, coords, tuple(times)
    except Exception, e:
        return False, coords, str(e)

def render(layer, tile):
    start = time.time()
    image = layer.render(tile)
    return image, time.time() - start

def image_postproc(layer, tile, image):
    postproc = layer.metadata.get("image_postproc")
    if postproc is not None:
        start = time.time()
        image = run_external(image, postproc)
        return image, time.time() - start
    else:
        return image, 0.0

def save(cache, tile, image):
    start = time.time()
    cache.set(tile, image)
    return time.time() - start

