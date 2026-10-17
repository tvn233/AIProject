import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.mcp import tools

class MCPBusinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = patch.object(tools, 'DB_FILE', Path(self.tmp.name) / 'db.json')
        self.patch.start()
    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()
    def test_confirmation_required(self):
        self.assertFalse(tools.register_ctxh_activity('SV001', 'ACT001')['ok'])
        self.assertFalse(tools.DB_FILE.exists())
    def test_write_read_verify(self):
        result = tools.register_ctxh_activity('SV001', 'ACT001', confirmed=True)
        self.assertTrue(result['ok'])
        self.assertEqual(tools.get_ctxh_registration_status('SV001', 'ACT001')['record'], result['record'])
    def test_duplicate_rejected(self):
        tools.register_ctxh_activity('SV001', 'ACT001', confirmed=True)
        self.assertFalse(tools.register_ctxh_activity('SV001', 'ACT001', confirmed=True)['ok'])
    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            tools.register_ctxh_activity('', 'ACT001', confirmed=True)
    def test_convert_explicit_rate(self):
        self.assertEqual(tools.convert_ctxh_points(40, 10)['days'], 4)
        with self.assertRaises(ValueError):
            tools.convert_ctxh_points(40, 0)

if __name__ == '__main__':
    unittest.main()
