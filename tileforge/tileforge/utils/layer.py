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
        shift = layer.yshift(z) if hasattr(layer, 'yshift') else 0.0
        xbuffer, ybuffer = metabuffer_size(layer, z) if use_buffer else (0, 0)
        minx, miny = exact_cell(layer, bbox[0] - xbuffer, (bbox[1] - ybuffer) + shift, z)
        maxx, maxy = exact_cell(layer, bbox[2] + xbuffer, (bbox[3] + ybuffer) + shift, z)

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

    width  = int(ceil(((layer.bbox[2] - layer.bbox[0]) / layer.size[0]) / layer.resolutions[z]))
    height = int(ceil(((layer.bbox[3] - layer.bbox[1]) / layer.size[1]) / layer.resolutions[z]))
    if xindex < 0:
        xindex = 0
    elif xindex >= width:
        xindex = width - 1

    if yindex < 0:
        yindex = 0
    elif yindex >= height:
        yindex = height - 1

    return xindex, yindex

def metabuffer_size(layer, z):
    """ return the metabuffer size for a resolution index """
    if not layer.metaTile:
        return (0, 0)
    else:
        return layer.resolutions[z] * float(layer.metaBuffer[0]), \
               layer.resolutions[z] * float(layer.metaBuffer[1])
