import unittest
from tileforge.utils.file import run

class TestUtilsFile(unittest.TestCase):
    def test_cmd_returns_non_zero(self):
        raised = False
        try:
            result = run(None, "false")
        except Exception, e:
            raised = True

        assert raised

