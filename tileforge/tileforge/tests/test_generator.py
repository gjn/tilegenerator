import unittest
from tileforge.tests import tilecache_service, CacheAlwaysFalse, CacheAlwaysTrue
from tileforge.generator import Generator

class TestGenerator(unittest.TestCase):
    def setUp(self):
        service = tilecache_service()
        self.raster = service.layers.get("valid-raster")
        self.invalid = service.layers.get("error-invalid-url")
        self.success_count = 0
        self.failure_count = 0

    def assert_false(self, *args, **kwargs):
        self.failure_count += 1
        assert False

    def assert_true(self, *args, **kwargs):
        self.success_count += 1
        assert True

    def test_run_tiles(self):
        generator = Generator(self.raster, CacheAlwaysTrue(), 
                              [(0, 0, 0)], 
                              on_failure=self.assert_false, 
                              on_success=self.assert_true)
        assert not generator.isAlive()
        generator.start()
        generator.join()

        assert self.success_count == 1
        assert self.failure_count == 0
 
    def test_run_tiles_invalid_cache(self):
        generator = Generator(self.raster, CacheAlwaysFalse(), 
                              [(0, 0, 0), (0, 0, 1)], 
                              on_failure=self.assert_true, 
                              on_success=self.assert_false)
        assert not generator.isAlive()
        generator.start()
        generator.join()

        assert self.success_count == 2
        assert self.failure_count == 0
 
