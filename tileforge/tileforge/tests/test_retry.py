import unittest
from StringIO import StringIO
from tileforge.utils.retry import dump, load
from tileforge.tests import tilecache_service

class TestRetry(unittest.TestCase):
    def test_dump_load(self):
        service = tilecache_service()
        raster = service.layers.get("valid-raster")
        
        in_tiles = zip(range(10), range(10,20), range(20, 30))
        f = StringIO()
        dump(raster, in_tiles, f)
        f.seek(0)
        out_layername, out_tiles = load(f)
        f.close()
        
        assert out_layername == raster.name
        assert out_tiles == in_tiles
