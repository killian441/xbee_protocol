from collections import defaultdict
from unittest import skipUnless
from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

xbee_available = True
try:
    import xbee
    from ..xbee_at_command_frame_block import XBeeATCommandFrame
except:
    xbee_available = False


@skipUnless(xbee_available, 'xbee is not available!!')
class TestXBeeATCommandFrame(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.signals = defaultdict(list)

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_defaults(self, mock_serial, mock_xbee):
        blk = XBeeATCommandFrame()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'at',
            frame_id=b'\x01',
            command=b'ID',
            parameter=b'')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_assign_expression(self, mock_serial, mock_xbee):
        blk = XBeeATCommandFrame()
        self.configure_block(blk, {
            "command": "D0",
            "parameter": "05",
            "frame_id": "00"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'at',
            frame_id=b'\x00',
            command=b'D0',
            parameter=b'\x05')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeATCommandFrame()
        self.configure_block(blk, {
            "command": "{{ $c }}",
            "parameter": "{{ $p }}",
            "frame_id": "{{ $f }}"
        })
        blk.start()
        blk.process_signals([Signal({
            'c': 'D0',
            'p': '05',
            'f': '00'
            })])
        blk._xbee._build_command.assert_called_once_with(
            'at',
            frame_id=b'\x00',
            command=b'D0',
            parameter=b'\x05')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_invalid_command(self, mock_serial, mock_xbee):
        blk = XBeeATCommandFrame()
        self.configure_block(blk, {
            "command": "{{ 1 }}"
        })
        blk.logger = MagicMock()
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        # build_command is never called because of the command not being ascii encodable
        # It needs to be a two ascii characters
        self.assertFalse(blk._xbee._build_command.called)
        # expected behavior is to log an error
        blk.logger.exception.assert_called_once_with('Failed to execute at command')
        blk.stop()

    def test_at_notify_signal(self):
        blk = XBeeATCommandFrame()
        self.configure_block(blk, {
            "escaped":False,
            "command": "{{ $iama }}",
            "parameter": "{{ $p }}",
            "frame_id": "4d"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'ID', 'p': '117E'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame':b'\x7E\x00\x06\x08\x4D\x49\x44\x11\x7E\x8E'})

    def test_at_escaped_notify_signal(self):
        blk = XBeeATCommandFrame()
        self.configure_block(blk, {
            "escaped":True,
            "command": "{{ $iama }}",
            "parameter": "{{ $p }}",
            "frame_id": "4d"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'ID', 'p': '11 7E'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame':b'\x7E\x00\x06\x08\x4D\x49\x44\x7D\x31\x7D\x5E\x8E'})
