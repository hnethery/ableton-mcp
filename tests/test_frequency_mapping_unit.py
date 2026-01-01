import unittest
import sys
import math
from unittest.mock import MagicMock

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

# Now we can import the class to test
# We need to add the parent directory to sys.path to find AbletonMCP_Remote_Script
import os
sys.path.append(os.getcwd())

from AbletonMCP_Remote_Script import AbletonMCP

class TestFrequencyMapping(unittest.TestCase):
    def setUp(self):
        self.mcp = AbletonMCP(MagicMock())

    def test_frequency_to_normalized_endpoints(self):
        # Test min frequency (10Hz)
        self.assertAlmostEqual(self.mcp._frequency_to_normalized(10.0), 0.0)
        # Test max frequency (22kHz)
        self.assertAlmostEqual(self.mcp._frequency_to_normalized(22000.0), 1.0)

    def test_frequency_to_normalized_midpoint(self):
        # Geometric mean should be exactly 0.5 in log scale
        # sqrt(10 * 22000) = sqrt(220000) ≈ 469.04
        mid_freq = math.sqrt(10 * 22000)
        self.assertAlmostEqual(self.mcp._frequency_to_normalized(mid_freq), 0.5)

    def test_normalized_to_frequency_endpoints(self):
        # Test min value (0.0)
        self.assertAlmostEqual(self.mcp._normalized_to_frequency(0.0), 10.0)
        # Test max value (1.0)
        self.assertAlmostEqual(self.mcp._normalized_to_frequency(1.0), 22000.0)

    def test_normalized_to_frequency_midpoint(self):
        # 0.5 should map to geometric mean
        expected_freq = math.sqrt(10 * 22000)
        self.assertAlmostEqual(self.mcp._normalized_to_frequency(0.5), expected_freq)

    def test_round_trip(self):
        # Test converting back and forth
        test_freqs = [20, 100, 440, 1000, 5000, 15000]
        for f in test_freqs:
            norm = self.mcp._frequency_to_normalized(f)
            back = self.mcp._normalized_to_frequency(norm)
            self.assertAlmostEqual(f, back, places=5)

if __name__ == '__main__':
    unittest.main()
