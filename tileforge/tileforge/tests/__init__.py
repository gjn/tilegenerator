import os.path
from TileCache import Service
from TileCache.Cache import Cache

def tilecache_service():
    cfg = os.path.join(os.path.dirname(__file__), "data/tilecache.cfg")
    return Service.load(cfg)


class CacheAlwaysFalse(Cache):
    def set(self, tile, data):
        raise Exception("CacheAlwaysFalse::set()")


class CacheAlwaysTrue(Cache):
    def set(self, tile, data):
        return data
