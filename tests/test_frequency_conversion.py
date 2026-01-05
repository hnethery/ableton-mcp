
import sys
import unittest
import math
from unittest.mock import MagicMock

# Mock _Framework.ControlSurface
module_name = "_Framework.ControlSurface"
if module_name not in sys.modules:
    mock_framework = MagicMock()
    sys.modules["_Framework"] = mock_framework
    sys.modules["_Framework.ControlSurface"] = mock_framework

    # Create the ControlSurface class in the mock module
    class MockControlSurface:
        def __init__(self, c_instance=None):
            pass
        def log_message(self, msg):
            pass
        def show_message(self, msg):
            pass
        def disconnect(self):
            pass
        def schedule_message(self, delay, callback, *args):
            pass
        def song(self):
            return MagicMock()
        def application(self):
            return MagicMock()

    mock_framework.ControlSurface = MockControlSurface

# Add the parent directory to sys.path to import AbletonMCP_Remote_Script
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AbletonMCP_Remote_Script import AbletonMCP

class TestFrequencyConversion(unittest.TestCase):
    def test_frequency_to_normalized(self):
        # We can call the method using the class, passing None as self since it doesn't use self
        mcp = AbletonMCP

        # Test boundaries with explicit min_freq=20.0 and max_freq=20000.0 to match original test assumptions
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 20, min_freq=20.0, max_freq=20000.0), 0.0)
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 20000, min_freq=20.0, max_freq=20000.0), 1.0)

        # Test mid-point (logarithmic middle)
        # Log(20) = 1.301
        # Log(20000) = 4.301
        # Mid = 2.801
        # 10^2.801 = 632.45
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 632.455, min_freq=20.0, max_freq=20000.0), 0.5, places=3)

        # Test 1kHz
        # Log(1000) = 3
        # Range = 3 - 1.301 = 1.699
        # Total Range = 3
        # Normalized = 1.699 / 3 = 0.566
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 1000, min_freq=20.0, max_freq=20000.0), (math.log10(1000) - math.log10(20)) / (math.log10(20000) - math.log10(20)), places=5)

    def test_frequency_to_normalized_defaults(self):
        # Test with default values (10Hz - 22kHz) - This exercises the optimized path
        mcp = AbletonMCP

        # 10Hz should be 0.0
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 10.0), 0.0)
        # 22kHz should be 1.0
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 22000.0), 1.0)

        # Check geometric mean (midpoint)
        # sqrt(10 * 22000) = 469.04
        mid_freq = math.sqrt(10.0 * 22000.0)
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, mid_freq), 0.5)

    def test_normalized_to_frequency(self):
        mcp = AbletonMCP

        # Pass explicit min/max to match expectations
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 0.0, min_freq=20.0, max_freq=20000.0), 20.0)
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 1.0, min_freq=20.0, max_freq=20000.0), 20000.0)

        # 0.5 -> 632.45
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 0.5, min_freq=20.0, max_freq=20000.0), 632.455, places=1)

    def test_normalized_to_frequency_defaults(self):
        # Test with default values (10Hz - 22kHz) - optimized path
        mcp = AbletonMCP

        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 0.0), 10.0)
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 1.0), 22000.0)

        # 0.5 -> 469.04
        mid_freq = math.sqrt(10.0 * 22000.0)
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 0.5), mid_freq, places=4)

    def test_round_trip(self):
        mcp = AbletonMCP

        for freq in [20, 100, 500, 1000, 5000, 10000, 20000]:
            # Use explicit min/max to stay consistent with original test intent
            norm = mcp._frequency_to_normalized(None, freq, min_freq=20.0, max_freq=20000.0)
            back = mcp._normalized_to_frequency(None, norm, min_freq=20.0, max_freq=20000.0)
            self.assertAlmostEqual(freq, back, places=4)

        # Test default path round trip
        for freq in [10, 100, 1000, 10000, 22000]:
            norm = mcp._frequency_to_normalized(None, freq)
            back = mcp._normalized_to_frequency(None, norm)
            self.assertAlmostEqual(freq, back, places=4)

if __name__ == '__main__':
    unittest.main()
