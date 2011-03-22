"""TileCache.Layer utility functions
"""
from math import ceil

__ALL__ = ["grid"]

def grid(layer, bbox=None, levels=None, use_buffer=False):
    if not bbox:
        bbox = layer.bbox

    if not levels:
        levels = (0, len(layer.resolutions))

    for z in range(*levels):
        xbuffer, ybuffer = metabuffer_size(layer, z) if use_buffer else (0, 0)
        minx, miny = exact_cell(layer, bbox[0] - xbuffer, bbox[1] - ybuffer, z)
        maxx, maxy = exact_cell(layer, bbox[2] + xbuffer, bbox[3] + ybuffer, z)
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                yield (x, y, z)

def exact_cell(layer, x, y, z):
    """
    Return the cell index exactly under the x and y coordinates at the given zoom level.
    If the coordinates are outside the layer extent, the closest cell is returned
    (the first or last cell index)
    """
    res = layer.resolutions[z]
    px = (x - layer.bbox[0]) / res
    py = (y - layer.bbox[1]) / res

    xindex = int(px) / layer.size[0]
    yindex = int(py) / layer.size[1]

    maxx, maxy = tuple([int(ceil(m)) for m in layer.grid(z)])
    if xindex < 0:
        xindex = 0
    elif xindex > maxx:
        xindex = maxx

    if yindex < 0:
        yindex = 0
    elif yindex > maxy:
        yindex = maxy

    return xindex, yindex

def metabuffer_size(layer, z):
    """ return the metabuffer size for a resolution index """
    if not layer.metaTile:
        return (0, 0)
    else:
        return layer.resolutions[z] * float(layer.metaBuffer[0]), \
               layer.resolutions[z] * float(layer.metaBuffer[1])
