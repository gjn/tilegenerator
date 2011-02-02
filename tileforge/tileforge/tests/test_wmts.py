import unittest

from xml.dom import minidom

from tileforge.tests import tilecache_service
from tileforge.utils.wmts import wmts_capabilities

class TestWMTS(unittest.TestCase):
    def setUp(self):
        service = tilecache_service()
        self.layers = service.layers.values()
        self.metadata = service.metadata

    def test_wmts_capabilities(self):
        doc = minidom.parseString(wmts_capabilities(self.layers, self.metadata))

        assert len(doc.getElementsByTagName("Layer")) == len(self.layers)
