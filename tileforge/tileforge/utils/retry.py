from math import ceil

__ALL__ = ["load", "dump"]

def load(f, service):
    lines = [line.strip() for line in f.readlines() if not line.startswith('#')]
    layername = lines.pop(0)
    layer = service.layers.get(layername)
    tiles = []
    for z, row, col in [tuple(map(int, tile.split())) for tile in lines if len(tile) > 0]:
        row_count = int(ceil(((layer.bbox[3] - layer.bbox[1]) / layer.size[1]) / layer.resolutions[z]))
        tiles.append((col, row_count - 1 - row, z))

    return layername, tiles

def dump(layer, tiles, f):
    f.write("# retry file in WMTS format: 'tile_matrix, row, col'\n")
    f.write(layer.name + "\n")
    for x, y, z in tiles:
        row_count = int(ceil(((layer.bbox[3] - layer.bbox[1]) / layer.size[1]) / layer.resolutions[z]))
        f.write("%d %d %d\n"%(z, row_count - y - 1, x))
