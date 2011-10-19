from math import ceil
from boto import connect_s3
from boto.s3.key import Key

from TileCache.Cache import Cache

class AWSS3(Cache):
    def __init__ (self, access_key, secret_access_key, bucket_name, validate="false", is_secure="false",**kwargs):
        Cache.__init__(self, **kwargs)
        self.validate = validate.lower() in ["yes", "y", "t", "true"]
        self.is_secure = is_secure=is_secure.lower() in ["yes", "y", "t", "true"]
        self.credential = (access_key, secret_access_key)
        self.bucket_name = bucket_name
        self._bucket = None
        self.options = kwargs

    @property
    def bucket(self):
        if self._bucket is None:
            connection = connect_s3(*self.credential, is_secure=self.is_secure)
            self._bucket = connection.get_bucket(self.bucket_name)
        return self._bucket

    def __getstate__(self):
        d = self.__dict__.copy()
        d['_bucket'] = None
        return d

    def __setstate__(self, state):
        self.__dict__ = state

    def getKey(self, tile):
        layer = tile.layer
        row_count = int(ceil(((layer.bbox[3] - layer.bbox[1]) / layer.size[1]) / layer.resolutions[tile.z]))

        style = layer.metadata.get("style", "default")
        dimension = layer.metadata.get("dimension")
        tile_matrix_set = layer.metadata.get("matrix_set", layer.name)
        tile_matrix = "%d"%int(tile.z)
        tile_row = "%d"%int(row_count - tile.y - 1)
        tile_col = "%d"%int(tile.x)

        return "/".join(["1.0.0", layer.name, style, dimension, tile_matrix_set,
                         tile_matrix, tile_row, tile_col + ".%s"%layer.extension])

    def set(self, tile, data):
        if self.readonly:
            return data
        else:
            k = Key(bucket=self.bucket, name=self.getKey(tile))
            k.set_contents_from_string(data, headers={"Content-Type": tile.layer.mime_type})
            if self.validate and k.name not in self.bucket:
                raise Exception("'%s' uploaded but not in bucket"%k.key)

            return data

    def read(self, path, *args, **kwargs):
        k = Key(bucket=self.bucket, name=path)
        return k.get_contents_as_string(*args, **kwargs)

    def write(self, data, path, *args, **kwargs):
        k = Key(bucket=self.bucket, name=path)
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
