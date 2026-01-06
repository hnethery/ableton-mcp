import unittest
import sys
import math
from unittest.mock import MagicMock
import os

# Mock the _Framework.ControlSurface module structure
module_name = '_Framework.ControlSurface'
if module_name not in sys.modules:
    mock_module = MagicMock()
    # Create a dummy class that can be inherited from
    class MockControlSurface:
        def __init__(self, c_instance):
            pass
        def log_message(self, msg):
            pass
        def show_message(self, msg):
            pass
        def disconnect(self):
            pass
        def song(self):
            return MagicMock()
        def application(self):
            return MagicMock()
        def schedule_message(self, delay, callback, *args):
            pass

    mock_module.ControlSurface = MockControlSurface
    sys.modules[module_name] = mock_module
    sys.modules['_Framework'] = MagicMock()
    sys.modules['_Framework'].ControlSurface = MockControlSurface

# Add parent directory to sys.path
sys.path.append(os.getcwd())

from AbletonMCP_Remote_Script import AbletonMCP

class TestLinearToDb(unittest.TestCase):
    def setUp(self):
        self.mcp = AbletonMCP(MagicMock())

    def test_linear_to_db_values(self):
        # 0.85 -> 0 dB
        self.assertAlmostEqual(self.mcp._linear_to_db(0.85), 0.0, places=5)

        # 1.0 -> 6 dB
        self.assertAlmostEqual(self.mcp._linear_to_db(1.0), 6.0, places=5)

        # < 0.85 should match log10 calculation
        # Test 0.5
        val = 0.5
        expected = 20 * math.log10(val / 0.85)
        self.assertAlmostEqual(self.mcp._linear_to_db(val), expected, places=5)

        # Test near zero
        val = 0.0001
        expected = 20 * math.log10(val / 0.85)
        self.assertAlmostEqual(self.mcp._linear_to_db(val), expected, places=5)

    def test_epsilon_handling(self):
        # Extremely small values should return -inf
        self.assertEqual(self.mcp._linear_to_db(0.0), float('-inf'))
        self.assertEqual(self.mcp._linear_to_db(1e-8), float('-inf'))

if __name__ == '__main__':
    unittest.main()
