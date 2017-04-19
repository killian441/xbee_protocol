from unittest import skipUnless
from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


xbee_available = True
try:
    import xbee
    from ..xbee_queued_at_block import XBeeQueuedAT
except:
    xbee_available = False


@skipUnless(xbee_available, 'xbee is not available!!')
class TestXBeeQueuedAT(NIOBlockTestCase):

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_defaults(self, mock_serial, mock_xbee):
        blk = XBeeQueuedAT()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'queued_at',
            frame_id=b'\x01',
            command=b'ID',
            parameter=b'')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_assign_expression(self, mock_serial, mock_xbee):
        blk = XBeeQueuedAT()
        self.configure_block(blk, {
            "command": "D0",
            "parameter": "05",
            "frame_id": "00"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'queued_at',
            frame_id=b'\x00',
            command=b'D0',
            parameter=b'\x05')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeQueuedAT()
        self.configure_block(blk, {
            "command": "{{ $c }}",
            "parameter": "{{ $p }}",
            "frame_id": "{{ $f }}"
        })
        blk.start()
        blk.process_signals([Signal({
            'c' : 'D0',
            'p' : '05',
            'f' : '00'})])
        blk._xbee._build_command.assert_called_once_with(
            'queued_at',
            frame_id=b'\x00',
            command=b'D0',
            parameter=b'\x05')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_invalid_command(self, mock_serial, mock_xbee):
        blk = XBeeQueuedAT()
        self.configure_block(blk, {
            "command": "{{ 1 }}"
        })
        blk.logger = MagicMock()
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        # Because of the command not being ascii encodable
        # It needs to be a two ascii characters
        self.assertFalse(len(self.last_notified[DEFAULT_TERMINAL]))
        # expected behavior is to log error
        blk.logger.exception.assert_called_once_with('Failed to execute queued at command')
        blk.stop()
