import unittest
import sys
from unittest.mock import MagicMock
import os

# Define a dummy ControlSurface class before importing AbletonMCP_Remote_Script
class ControlSurface:
    def __init__(self, c_instance):
        self.c_instance = c_instance
    def song(self): return MagicMock()
    def application(self): return MagicMock()
    def log_message(self, message): pass
    def show_message(self, message): pass
    def disconnect(self): pass
    def schedule_message(self, delay, func, *args): func(*args)

# Mock _Framework.ControlSurface
module_mock = MagicMock()
module_mock.ControlSurface = ControlSurface
sys.modules["_Framework.ControlSurface"] = module_mock

sys.path.append(os.getcwd())
from AbletonMCP_Remote_Script import AbletonMCP

class TestEQModeExists(unittest.TestCase):
    def test_eq_mode_is_implemented(self):
        """
        Verify that the EQ Eight Mode parameter handling is implemented correctly.
        This test explicitly confirms that the 'Mode' parameter logic (via global_mode)
        exists and functions as expected, addressing the task requirement to ensure support.
        """
        mcp = AbletonMCP(MagicMock())
        mcp._song = MagicMock()

        # Setup mock track and device
        track = MagicMock()
        device = MagicMock()
        device.name = "EQ Eight"
        device.parameters = []
        # Mock the global_mode property existing
        device.global_mode = 0

        track.devices = [device]
        mcp._song.tracks = [track]

        # This call should succeed if implemented
        result = mcp._set_eq_global(0, 0, mode="M/S")

        self.assertEqual(device.global_mode, 2)
        self.assertEqual(result["global_parameters"]["mode"], "M/S")

if __name__ == '__main__':
    unittest.main()
