
import unittest
import math
import sys
from unittest.mock import MagicMock

# Mock _Framework.ControlSurface
# We need to ensure that when AbletonMCP imports ControlSurface, it gets our mock
sys.modules['_Framework'] = MagicMock()
mock_control_surface_module = MagicMock()
sys.modules['_Framework.ControlSurface'] = mock_control_surface_module

# Create a mock class for ControlSurface
class MockControlSurface:
    def __init__(self, c_instance):
        pass
    def disconnect(self):
        pass
    def song(self):
        # Return a mock song object
        mock_song = MagicMock()
        mock_song.tempo = 120.0
        mock_song.tracks = []
        mock_song.return_tracks = []
        mock_song.master_track.mixer_device.volume.value = 1.0
        return mock_song
    def log_message(self, msg):
        pass
    def show_message(self, msg):
        pass
    def schedule_message(self, delay, callback, *args):
        callback(*args)
    def application(self):
        return MagicMock()

mock_control_surface_module.ControlSurface = MockControlSurface

# Import AbletonMCP
import os
sys.path.append(os.getcwd())
from AbletonMCP_Remote_Script import AbletonMCP

class TestQConversion(unittest.TestCase):
    def setUp(self):
        # Mock ControlSurface
        c_instance = MagicMock()
        # Prevent socket creation in __init__
        original_start_server = AbletonMCP.start_server
        AbletonMCP.start_server = MagicMock()

        try:
            self.mcp = AbletonMCP(c_instance)
        finally:
            AbletonMCP.start_server = original_start_server

    def test_q_to_normalized_min(self):
        q = 0.1
        normalized = self.mcp._q_to_normalized(q)
        self.assertAlmostEqual(normalized, 0.0)

    def test_q_to_normalized_max(self):
        q = 18.0
        normalized = self.mcp._q_to_normalized(q)
        self.assertAlmostEqual(normalized, 1.0)

    def test_q_to_normalized_mid(self):
        # Middle of log scale is sqrt(0.1 * 18.0) approx 1.34
        q = math.sqrt(0.1 * 18.0)
        normalized = self.mcp._q_to_normalized(q)
        self.assertAlmostEqual(normalized, 0.5)

    def test_q_to_normalized_clamping(self):
        self.assertAlmostEqual(self.mcp._q_to_normalized(0.05), 0.0)
        self.assertAlmostEqual(self.mcp._q_to_normalized(20.0), 1.0)

    def test_normalized_to_q_min(self):
        norm = 0.0
        q = self.mcp._normalized_to_q(norm)
        self.assertAlmostEqual(q, 0.1)

    def test_normalized_to_q_max(self):
        norm = 1.0
        q = self.mcp._normalized_to_q(norm)
        self.assertAlmostEqual(q, 18.0)

    def test_normalized_to_q_mid(self):
        norm = 0.5
        q = self.mcp._normalized_to_q(norm)
        expected = math.sqrt(0.1 * 18.0)
        self.assertAlmostEqual(q, expected)

    def test_round_trip(self):
        test_qs = [0.1, 0.5, 1.0, 5.0, 10.0, 18.0]
        for q in test_qs:
            norm = self.mcp._q_to_normalized(q)
            q_back = self.mcp._normalized_to_q(norm)
            self.assertAlmostEqual(q, q_back)

if __name__ == '__main__':
    unittest.main()
