from cloudfiles import get_connection

from TileCache.Cache import Cache

# NOT TESTED AT ALL !
class CloudFiles(Cache):
    def __init__ (self, username, api_key, container, **kwargs):
        Cache.__init__(self, **kwargs)
        connection = connect_cloudfiles(username, api_key)
        self.container = connection.get_container(container)

    def getKey(self, tile):
        raise NotImplementedError()

    def set(self, tile, data):
        if self.readonly:
            return data
        else:
            obj = self.container.create_object(self.getKey(tile))
            obj.content_type = tile.layer.mime_type
            obj.write(data)

    def get(self, tile):
        # write only cache
        return None

    def lock(self, tile, blocking=True):
        return True

    def unlock(self, tile):
        pass

