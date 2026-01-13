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

# Now we can import the module to test
sys.path.append('.')

# Force reload if it was already loaded
if 'AbletonMCP_Remote_Script' in sys.modules:
    del sys.modules['AbletonMCP_Remote_Script']

from AbletonMCP_Remote_Script import AbletonMCP

class TestQValueConversion(unittest.TestCase):
    """
    Test class specifically for Q value conversion logic to ensure
    it matches the logarithmic scale requirement (0.1 to 18.0).
    """

    def test_q_logarithmic_scaling(self):
        """Verify that Q conversion follows a logarithmic scale."""
        min_q = 0.1
        max_q = 18.0

        # Calculate expected values using the formula directly
        log_min = math.log10(min_q)
        log_max = math.log10(max_q)

        # Test a few points
        test_points = [0.1, 1.0, 5.0, 10.0, 18.0]

        for q in test_points:
            log_q = math.log10(q)
            expected_normalized = (log_q - log_min) / (log_max - log_min)

            actual_normalized = AbletonMCP._q_to_normalized(None, q)

            self.assertAlmostEqual(actual_normalized, expected_normalized, places=5,
                                   msg=f"Failed for Q={q}")

    def test_q_limits(self):
        """Verify that Q values outside the range are clamped."""
        # Below min
        self.assertEqual(AbletonMCP._q_to_normalized(None, 0.05), 0.0)

        # Above max
        self.assertEqual(AbletonMCP._q_to_normalized(None, 20.0), 1.0)

    def test_normalized_to_q_conversion(self):
        """Verify that normalized value converts back to Q correctly."""
        min_q = 0.1
        max_q = 18.0

        # Test 0.0 -> min_q
        self.assertAlmostEqual(AbletonMCP._normalized_to_q(None, 0.0), min_q)

        # Test 1.0 -> max_q
        self.assertAlmostEqual(AbletonMCP._normalized_to_q(None, 1.0), max_q)

        # Test 0.5 -> Geometric mean
        # log(mid) = (log(min) + log(max)) / 2
        # mid = sqrt(min * max)
        expected_mid = math.sqrt(min_q * max_q)
        self.assertAlmostEqual(AbletonMCP._normalized_to_q(None, 0.5), expected_mid)

        # Round trip test
        q_original = 2.5
        normalized = AbletonMCP._q_to_normalized(None, q_original)
        q_restored = AbletonMCP._normalized_to_q(None, normalized)
        self.assertAlmostEqual(q_original, q_restored)

    def test_no_rough_approximation(self):
        """
        Verify that we are NOT using the rough approximation q / 10.0.
        For example, if q=10.0, the rough approximation would be 1.0.
        But using log scale (0.1 to 18.0):
        log10(10) = 1.0
        log10(0.1) = -1.0
        log10(18) = 1.255
        range = 2.255
        normalized = (1.0 - (-1.0)) / 2.255 = 2.0 / 2.255 = 0.886
        """
        q = 10.0
        rough_approx = q / 10.0  # 1.0

        actual = AbletonMCP._q_to_normalized(None, q)

        # Ensure the actual value is significantly different from the rough approximation
        self.assertNotAlmostEqual(actual, rough_approx, delta=0.1)

        # Verify it matches the log calculation
        log_min = math.log10(0.1)
        log_max = math.log10(18.0)
        expected = (math.log10(q) - log_min) / (log_max - log_min)
        self.assertAlmostEqual(actual, expected, places=5)

if __name__ == '__main__':
    unittest.main()
