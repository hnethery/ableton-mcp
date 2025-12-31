import unittest
import sys
import math
from unittest.mock import MagicMock

# Define a dummy ControlSurface class to inherit from
class MockControlSurface:
    def __init__(self, c_instance):
        pass
    def song(self):
        return MagicMock()
    def disconnect(self):
        pass
    def application(self):
        return MagicMock()
    def schedule_message(self, delay, callback, *args):
        callback(*args)
    def log_message(self, msg):
        pass
    def show_message(self, msg):
        pass

# Mock the module structure
control_surface_module = MagicMock()
control_surface_module.ControlSurface = MockControlSurface
sys.modules['_Framework.ControlSurface'] = control_surface_module
sys.modules['_Framework'] = MagicMock()

# Mock Queue for Python 3 (since the script handles import Queue as queue)
# The script does:
# try: import Queue as queue; except ImportError: import queue
# So we don't need to mock Queue if we are on Python 3, which we are.

# Now we can import the module to test
sys.path.append('.')

# Force reload if it was already loaded (unlikely but good for safety)
if 'AbletonMCP_Remote_Script' in sys.modules:
    del sys.modules['AbletonMCP_Remote_Script']

from AbletonMCP_Remote_Script import AbletonMCP

print(f"AbletonMCP is: {AbletonMCP}")

class TestEqConversion(unittest.TestCase):
    def test_q_to_normalized(self):
        # Test min value
        self.assertAlmostEqual(AbletonMCP._q_to_normalized(None, 0.1), 0.0)

        # Test max value
        self.assertAlmostEqual(AbletonMCP._q_to_normalized(None, 18.0), 1.0)

        # Test middle value
        val_1 = AbletonMCP._q_to_normalized(None, 1.0)
        expected = (math.log10(1.0) - math.log10(0.1)) / (math.log10(18.0) - math.log10(0.1))
        self.assertAlmostEqual(val_1, expected)

        # Test round trip
        test_values = [0.1, 0.5, 1.0, 5.0, 10.0, 18.0]
        for q in test_values:
            norm = AbletonMCP._q_to_normalized(None, q)
            back = AbletonMCP._normalized_to_q(None, norm)
            self.assertAlmostEqual(q, back, places=4)

    def test_frequency_to_normalized(self):
        # Test min value
        self.assertAlmostEqual(AbletonMCP._frequency_to_normalized(None, 20.0), 0.0)

        # Test max value
        self.assertAlmostEqual(AbletonMCP._frequency_to_normalized(None, 20000.0), 1.0)

        # Test round trip
        test_values = [20.0, 100.0, 1000.0, 5000.0, 20000.0]
        for freq in test_values:
            norm = AbletonMCP._frequency_to_normalized(None, freq)
            back = AbletonMCP._normalized_to_frequency(None, norm)
            self.assertAlmostEqual(freq, back, places=2)

if __name__ == '__main__':
    unittest.main()
