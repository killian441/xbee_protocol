from unittest import skipUnless
from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


xbee_available = True
try:
    import xbee
    from ..xbee_tx_block import XBeeTX
except:
    xbee_available = False


@skipUnless(xbee_available, 'xbee is not available!!')
class TestXBeeTX(NIOBlockTestCase):

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_xbee_build_command(self, mock_serial, mock_xbee):
        blk = XBeeTX()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'tx',
            frame_id=b'\x01',
            dest_addr=b'\xFF\xFF',
            data=b"{'iama': 'signal'}")
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_xbee_build_multiple_commands(self, mock_serial, mock_xbee):
        blk = XBeeTX()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal(), Signal()])
        self.assertEqual(2, blk._xbee._build_command.call_count)
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeTX()
        self.configure_block(blk, {
            "dest_addr": "00 42",
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'tx',
            frame_id=b'\x01',
            dest_addr=b'\x00\x42',
            data=b'signal')

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_hidden_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeTX()
        self.configure_block(blk, {
            "dest_addr": "00 42",
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal', 'frame_id': '00'})])
        blk._xbee._build_command.assert_called_once_with(
            'tx',
            frame_id=b'\x00',
            dest_addr=b'\x00\x42',
            data=b'signal')

    def test_notify_signal(self):
        blk = XBeeTX()
        self.configure_block(blk, {
            "dest_addr": "00 42",
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        self.assert_num_signals_notified(1, blk)