
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

        # Test boundaries
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 20), 0.0)
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 20000), 1.0)

        # Test mid-point (logarithmic middle)
        # Log(20) = 1.301
        # Log(20000) = 4.301
        # Mid = 2.801
        # 10^2.801 = 632.45
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 632.455), 0.5, places=3)

        # Test 1kHz
        # Log(1000) = 3
        # Range = 3 - 1.301 = 1.699
        # Total Range = 3
        # Normalized = 1.699 / 3 = 0.566
        self.assertAlmostEqual(mcp._frequency_to_normalized(None, 1000), (3 - math.log10(20)) / (math.log10(20000) - math.log10(20)), places=5)

    def test_normalized_to_frequency(self):
        mcp = AbletonMCP

        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 0.0), 20.0)
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 1.0), 20000.0)

        # 0.5 -> 632.45
        self.assertAlmostEqual(mcp._normalized_to_frequency(None, 0.5), 632.455, places=1)

    def test_round_trip(self):
        mcp = AbletonMCP

        for freq in [20, 100, 500, 1000, 5000, 10000, 20000]:
            norm = mcp._frequency_to_normalized(None, freq)
            back = mcp._normalized_to_frequency(None, norm)
            self.assertAlmostEqual(freq, back, places=4)

if __name__ == '__main__':
    unittest.main()
