import unittest
from StringIO import StringIO
from tileforge.utils.retry import dump, load

class TestRetry(unittest.TestCase):
    def test_dump_load(self):
        in_layername = "this_is_the_layername"
        in_tiles = zip(range(10), range(10,20), range(20, 30))
        f = StringIO()
        dump(in_layername, in_tiles, f)
        f.seek(0)
        out_layername, out_tiles = load(f)
        
        assert out_layername == in_layername
        assert out_tiles == in_tiles
        f.close()
