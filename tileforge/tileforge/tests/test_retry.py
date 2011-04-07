import unittest
from StringIO import StringIO
from tileforge.utils.retry import dump, load
from tileforge.utils.layer import grid
from tileforge.tests import tilecache_service

class TestRetry(unittest.TestCase):
    def test_dump_load(self):
        service = tilecache_service()
        raster = service.layers.get("valid-raster")

        in_tiles = [_ for _ in grid(raster, bbox=[655000,194000,672500,206000], levels=(19,20))]
        f = StringIO()
        dump(raster, in_tiles, f)
        f.seek(0)
        out_layername, out_tiles = load(f, service)
        f.close()

        assert out_layername == raster.name
        assert out_tiles == in_tiles
