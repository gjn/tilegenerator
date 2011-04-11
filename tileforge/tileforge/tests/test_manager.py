import unittest
from tileforge.tests import tilecache_service
from tileforge.manager import Manager

class TestManager(unittest.TestCase):
    def setUp(self):
        service = tilecache_service()
        self.raster = service.layers.get("valid-raster")
        self.invalid = service.layers.get("error-invalid-url")
        self.cache = service.cache

    def test_init(self):
        manager = Manager(self.raster, self.cache, threads=12)

        assert manager.poolsize == 12
        assert manager.success_count == len(manager.failures) == 0

    def test_run_valid_layer(self):
        manager = Manager(self.raster, self.cache, levels=(0, 1), threads=2)
        manager.start()
        assert manager.running()

        status = manager.join()
        assert not manager.running()
        assert manager.success_count > 0
        assert len(manager.failures) == 0
        assert status is True
        assert manager.fatal is False

    def test_run_invalid_layer(self):
        manager = Manager(self.invalid, self.cache, levels=(0, 1), threads=2)
        manager.start()
        assert manager.running()

        status = manager.join()
        assert not manager.running()
        assert manager.success_count == 0
        assert len(manager.failures) > 0
        assert status is False
        assert manager.fatal is False, "not so many errors"

#     def test_run_too_many_errors(self):
#         manager = Manager(self.invalid, self.cache, tiles=[(0, 0, z) for z in range(20)], 
#                           threads=2, )
#         manager.start()
#         status = manager.join()
#         assert status is False
#         assert manager.fatal is True
