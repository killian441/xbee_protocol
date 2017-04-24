from unittest import skipUnless
from unittest.mock import patch, MagicMock
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


xbee_available = True
try:
    import xbee
    from ..xbee_parse_frame_block import XBeeParseFrame
except:
    xbee_available = False


@skipUnless(xbee_available, 'xbee is not available!!')
class TestXBeeParseFrame(NIOBlockTestCase):

    @patch('xbee.XBee')
    @patch('serial.Serial')
    def test_xbee_parse_frame_defaults(self, mock_serial, mock_xbee):
        blk = XBeeParseFrame()
        self.configure_block(blk, {})
        blk.logger = MagicMock()
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk.logger.exception.assert_called_once_with("Failed to parse frame")
        blk.stop()

    def test_notify_signal(self):
        blk = XBeeParseFrame()
        self.configure_block(blk, {
            "escaped":False,
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': b'\x7E\x00\x0B\x81\x11\x7E\x00'
                        b'\x01\x73\x69\x67\x6E\x61\x6C\x70'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame': {'id': 'rx',
                        'options': b'\x01',
                        'rf_data': b'signal',
                        'rssi': b'\x00',
                        'source_addr': b'\x11\x7E'}})

    def test_escaped_notify_signal(self):
        blk = XBeeParseFrame()
        self.configure_block(blk, {
            "escaped":True,
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': b'\x7E\x00\x0B\x81\x7D\x31\x7D'
                        b'\x5E\x00\x01\x73\x69\x67\x6E\x61\x6C\x70'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame': {'id': 'rx',
                        'options': b'\x01',
                        'rf_data': b'signal',
                        'rssi': b'\x00',
                        'source_addr': b'\x11\x7E'}})