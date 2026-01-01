import unittest
import sys
from unittest.mock import MagicMock, patch

# Define a dummy ControlSurface class before importing AbletonMCP_Remote_Script
class ControlSurface:
    def __init__(self, c_instance):
        self.c_instance = c_instance

    def song(self):
        return MagicMock()

    def application(self):
        return MagicMock()

    def log_message(self, message):
        pass

    def show_message(self, message):
        pass

    def disconnect(self):
        pass

    def schedule_message(self, delay, func, *args):
        func(*args)

# Mock _Framework.ControlSurface
module_mock = MagicMock()
module_mock.ControlSurface = ControlSurface
sys.modules["_Framework.ControlSurface"] = module_mock

# Add the current directory to sys.path so we can import AbletonMCP_Remote_Script
import os
sys.path.append(os.getcwd())

from AbletonMCP_Remote_Script import AbletonMCP

class TestEQEightMode(unittest.TestCase):

    def setUp(self):
        self.c_instance = MagicMock()
        self.mcp = AbletonMCP(self.c_instance)

        # Setup mock song structure
        self.song = MagicMock()
        self.mcp._song = self.song

        self.track = MagicMock()
        self.song.tracks = [self.track]

        self.device = MagicMock()
        self.device.name = "EQ Eight"
        self.device.class_name = "AudioEffect"
        self.track.devices = [self.device]

        # Default device parameters
        self.device.parameters = []

    def test_global_mode_property_handling(self):
        """Test that global_mode property is used when available"""
        # Add global_mode property to device
        self.device.global_mode = 0  # Initial value: Stereo

        # Mock hasattr to return True for global_mode
        # Note: We need to use spec or attach attribute directly.
        # MagicMock usually handles attributes dynamically, but hasattr might check __dict__
        # or dir().
        # In Python, hasattr on a Mock usually works if the attribute has been accessed or set.

        # Test setting Mode to 'M/S' (should map to 2)
        result = self.mcp._set_eq_global(0, 0, mode="M/S")

        self.assertEqual(self.device.global_mode, 2)
        self.assertEqual(result["global_parameters"]["mode"], "M/S")

        # Test setting Mode to 'Stereo' (should map to 0)
        result = self.mcp._set_eq_global(0, 0, mode="Stereo")

        self.assertEqual(self.device.global_mode, 0)
        self.assertEqual(result["global_parameters"]["mode"], "Stereo")

    def test_fallback_to_parameter(self):
        """Test fallback to parameter if global_mode property is missing (older Live versions)"""
        # Ensure device does NOT have global_mode property
        # We can't easily 'delete' an attribute from a Mock that creates them on fly,
        # but we can configure it to raise AttributeError on access or use a fresh mock
        # that doesn't have it set.
        # Actually, `hasattr` on a MagicMock is always True unless spec is used.
        # Let's assume the implementation uses `hasattr(device, 'global_mode')`.

        # Create a device mock that does NOT have global_mode
        # We can achieve this by using a class without the attribute or a spec.
        device_no_prop = MagicMock(spec=['parameters', 'name'])
        device_no_prop.name = "EQ Eight"

        # Setup Mode parameter
        mode_param = MagicMock()
        mode_param.name = "Mode"
        mode_param.value_items = ["Stereo", "L/R", "M/S"]
        mode_param.value = 0
        device_no_prop.parameters = [mode_param]

        self.track.devices = [device_no_prop]

        # Test setting Mode
        result = self.mcp._set_eq_global(0, 0, mode="L/R")

        self.assertEqual(mode_param.value, 1)
        self.assertEqual(result["global_parameters"]["mode"], "L/R")

    def test_failure_when_neither_exists(self):
        """Test failure when neither global_mode property nor Mode parameter exists"""
        # Create a device mock that does NOT have global_mode and NO Mode parameter
        device_broken = MagicMock(spec=['parameters', 'name'])
        device_broken.name = "EQ Eight"
        device_broken.parameters = [] # No parameters

        self.track.devices = [device_broken]

        with self.assertRaises(ValueError) as context:
            self.mcp._set_eq_global(0, 0, mode="Stereo")

        self.assertIn("Mode parameter not found", str(context.exception))

if __name__ == '__main__':
    unittest.main()
