from boto import connect_s3
from boto.s3.key import Key
from tileforge.utils.layer import exact_cell

from TileCache.Cache import Cache

class AWSS3(Cache):
    def __init__ (self, access_key, secret_access_key, bucket_name, validate="false", **kwargs):
        Cache.__init__(self, **kwargs)
        self.validate = validate.lower() in ["yes", "y", "t", "true"]

        connection = connect_s3(access_key, secret_access_key)
        self.bucket = connection.get_bucket(bucket_name)

    def getKey(self, tile):
        _, row_count = exact_cell(tile.layer, tile.layer.bbox[2], tile.layer.bbox[3], tile.z)

        style = tile.layer.metadata.get("style", "default")
        dimension = tile.layer.metadata.get("dimension")
        tile_matrix_set = tile.layer.metadata.get("matrix_set", tile.layer.name)
        tile_matrix = "%d"%int(tile.z)
        tile_row = "%d"%int(row_count - tile.y)
        tile_col = "%d"%int(tile.x)

        return "/".join(["1.0.0", tile.layer.name, style, dimension, tile_matrix_set,
                         tile_matrix, tile_row, tile_col + ".%s"%tile.layer.extension])

    def set(self, tile, data):
        if self.readonly:
            return data
        else:
            k = Key(self.bucket)
            k.key = self.getKey(tile)
            k.set_contents_from_string(data, headers={"Content-Type": tile.layer.mime_type})
            if self.validate and k.key not in self.bucket:
                raise Exception("'%s' uploaded but not in bucket"%k.key)

            return data

    def read(self, path, *args, **kwargs):
        k = Key(self.bucket)
        k.key = path
        return k.get_contents_as_string(*args, **kwargs)

    def write(self, data, path, *args, **kwargs):
        k = Key(self.bucket)
        k.key = path
        k.set_contents_from_string(data, *args, **kwargs)

    def get(self, tile):
        # write only cache
        return None

    def lock(self, tile, blocking=True):
        return True

    def unlock(self, tile):
        pass

    def __contains__(self, tile):
        return self.getKey(tile) in self.bucket
