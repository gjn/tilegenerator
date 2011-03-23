import unittest

from tileforge.utils.layer import *
from tileforge.tests import tilecache_service

class TestLayerUtils(unittest.TestCase):

    def setUp(self):
        self.service = tilecache_service()
        self.layer = self.service.layers.get("valid-raster")
        self.bbox = self.layer.bbox
        self.levels = (0, len(self.layer.resolutions))

        self.expectedGrid = [
            (0, 0, 10),
            (1, 0, 10),
            (0, 0, 11),
            (0, 1, 11),
            (1, 0, 11),
            (1, 1, 11),
            (0, 0, 12),
            (0, 1, 12),
            (1, 0, 12),
            (1, 1, 12),
            (0, 0, 13),
            (0, 1, 13),
            (1, 0, 13),
            (1, 1, 13),
            (2, 0, 13),
            (2, 1, 13),
            (0, 0, 14),
            (0, 1, 14),
            (1, 0, 14),
            (1, 1, 14),
            (2, 0, 14),
            (2, 1, 14)]

        self.expectedCell = [
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (1, 0),
            (1, 0),
            (1, 1),
            (1, 1),
            (2, 1),
            (2, 1),
            (3, 2),
            (7, 5),
            (18, 12),
            (37, 25),
            (93, 62),
            (187, 125),
            (375, 250),
            (750, 500),
            (937, 625),
            (1250, 833),
            (1875, 1250),
            (3750, 2500)]

    def test_layer_grid(self):
        current = grid(self.layer, self.bbox, (10, 15))
        for tile in current:
            assert tile == self.expectedGrid.pop(0)

    def test_layer_cell(self):
        for zoom in range(self.levels[0], self.levels[1]):
            assert exact_cell(self.layer, self.bbox[2], self.bbox[3], zoom) == self.expectedCell.pop(0)

