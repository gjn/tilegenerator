import pickle

def load(f):
    layername = f.readline().strip()
    tiles = [tuple(map(int, tile.strip().split())) for tile in f.readlines()]
    return layername, tiles

def dump(layer, tiles, f):
    f.write(layer.name + "\n")
    for tile in tiles:
        f.write("%d %d %d\n"%tile)
