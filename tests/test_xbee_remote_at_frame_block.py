from unittest import skipUnless
from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


xbee_available = True
try:
    import xbee
    from ..xbee_remote_at_frame_block import XBeeRemoteATFrame
except:
    xbee_available = False


@skipUnless(xbee_available, 'xbee is not available!!')
class TestXBeeRemoteATFrame(NIOBlockTestCase):

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_defaults(self, mock_serial, mock_xbee):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'remote_at',
            frame_id=b'\x01',
            dest_addr=b'\xFF\xFF',
            command=b'ID',
            parameter=b'')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_assign_expression(self, mock_serial, mock_xbee):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {
            "dest_addr": "00 42",
            "command": "D0",
            "parameter": "05",
            "frame_id": "00"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'remote_at',
            frame_id=b'\x00',
            dest_addr=b'\x00\x42',
            command=b'D0',
            parameter=b'\x05')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {
            "dest_addr": "{{ $d }}",
            "command": "{{ $c }}",
            "parameter": "{{ $p }}",
            "frame_id": "{{ $f }}"
        })
        blk.start()
        blk.process_signals([Signal({'d' : '00 42',
            'c' : 'D0',
            'p' : '05',
            'f' : '00'})])
        blk._xbee._build_command.assert_called_once_with(
            'remote_at',
            frame_id=b'\x00',
            dest_addr=b'\x00\x42',
            command=b'D0',
            parameter=b'\x05')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_invalid_dest_addr(self, mock_serial, mock_xbee):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {
            "dest_addr": "0"
        })
        blk.logger = MagicMock()
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        # Because of the odd length dest_addr
        # It needs to be a byte, represented as two ascii chars
        self.assertFalse(blk._xbee._build_command.called)
        # expected behavior is to log error
        blk.logger.exception.assert_called_once_with('Failed to execute remote at command')
        blk.stop()

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_invalid_command(self, mock_serial, mock_xbee):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {
            "command": "{{ 1 }}"
        })
        blk.logger = MagicMock()
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        # Because of the command not being ascii encodable
        # It needs to be a two ascii characters
        self.assertFalse(blk._xbee._build_command.called)
        # expected behavior is to log error
        blk.logger.exception.assert_called_once_with('Failed to execute remote at command')
        blk.stop()

    def test_notify_signal(self):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {
            "dest_addr": "00 42",
            "escaped":False,
            "command": "{{ $iama }}",
            "parameter": "{{ $p }}",
            "frame_id": "4d"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'ID', 'p': '117E'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame':b'\x7E\x00\x11\x17\x4D\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x42\x02\x49\x44\x11\x7E\x3B'})

    def test_escaped_notify_signal(self):
        blk = XBeeRemoteATFrame()
        self.configure_block(blk, {
            "dest_addr": "12 34 56 78 90 AB cd Ef",
            "escaped":True,
            "command": "{{ $iama }}",
            "parameter": "{{ $p }}",
            "frame_id": "4d"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'ID', 'p': '11 7E'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame':b'\x7E\x00\x7D\x31\x17\x4D\x12\x34\x56\x78\x90\xAB\xCD'
                    b'\xEF\xFF\xFE\x02\x49\x44\x7D\x31\x7D\x5E\x75'})
