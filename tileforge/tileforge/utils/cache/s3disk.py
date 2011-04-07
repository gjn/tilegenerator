import os
from math import ceil
from TileCache.Caches.Disk import Disk

class S3Disk(Disk):
    def getKey(self, tile):
        layer = tile.layer
        row_count = int(ceil(((layer.bbox[3] - layer.bbox[1]) / layer.size[1]) / layer.resolutions[tile.z]))

        style = layer.metadata.get("style", "default")
        dimension = layer.metadata.get("dimension")
        tile_matrix_set = layer.metadata.get("matrix_set", layer.name)
        tile_matrix = "%d"%int(tile.z)
        tile_row = "%d"%int(row_count - tile.y - 1)
        tile_col = "%d"%int(tile.x)

        return os.path.join(self.basedir, "1.0.0", layer.name, style, dimension,
                            tile_matrix_set, tile_matrix, tile_row, tile_col + ".%s"%layer.extension)
