from unittest import skipUnless
from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase


xbee_available = True
try:
    import xbee
    from ..xbee_digimesh_tx_block import XBeeDigiMeshTX
except:
    xbee_available = False


@skipUnless(xbee_available, 'xbee is not available!!')
class TestXBeeDigiMeshTX(NIOBlockTestCase):

    @patch('xbee.DigiMesh')
    @patch('serial.Serial')
    def test_XBeeDigiMesh_long_defaults(self, mock_serial, mock_xbee):
        blk = XBeeDigiMeshTX()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'tx',
            frame_id=b'\x01',
            dest_addr=b'\x00\x00\x00\x00\x00\x00\xFF\xFF',
            data=b"{'iama': 'signal'}",
            id=b'\x10',
            reserved=b'\xFF\xFE',
            broadcast_radius=b'\x00',
            options=b'\x00')
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.DigiMesh')
    @patch('serial.Serial')
    def test_xbee_long_build_multiple_commands(self, mock_serial, mock_xbee):
        blk = XBeeDigiMeshTX()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal(), Signal()])
        self.assertEqual(2, blk._xbee._build_command.call_count)
        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]))
        blk.stop()

    @patch('xbee.DigiMesh')
    @patch('serial.Serial')
    def test_tx_long_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeDigiMeshTX()
        self.configure_block(blk, {
            "dest_addr": "AB Cd ef 12 99 35 00 42",
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal'})])
        blk._xbee._build_command.assert_called_once_with(
            'tx',
            frame_id=b'\x01',
            dest_addr=b'\xAB\xCD\xEF\x12\x99\x35\x00\x42',
            data=b'signal',
            id=b'\x10',
            reserved=b'\xFF\xFE',
            broadcast_radius=b'\x00',
            options=b'\x00')

    @patch('xbee.DigiMesh')
    @patch('serial.Serial')
    def test_tx_long_hidden_expression_props(self, mock_serial, mock_xbee):
        blk = XBeeDigiMeshTX()
        self.configure_block(blk, {
            "dest_addr": "{{ $d }}",
            "data": "{{ $iama }}",
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'signal', 
            'frame_id': '00',
            'd': 'AB Cd ef 12 99 35 00 42'})])
        blk._xbee._build_command.assert_called_once_with(
            'tx',
            frame_id=b'\x00',
            dest_addr=b'\xAB\xCD\xEF\x12\x99\x35\x00\x42',
            data=b'signal',
            id=b'\x10',
            reserved=b'\xFF\xFE',
            broadcast_radius=b'\x00',
            options=b'\x00')

    def test_digimesh_tx_notify_signal(self):
        blk = XBeeDigiMeshTX()
        self.configure_block(blk, {
            "dest_addr": "0013A200400a0127",
            "escaped":False,
            "data": "{{ $iama }}"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'TxData0A'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame':b'\x7E\x00\x16\x10\x01\x00\x13\xA2\x00\x40\x0A\x01\x27' 
            b'\xFF\xFE\x00\x00\x54\x78\x44\x61\x74\x61\x30\x41\x13'})

    def test_digimesh_tx_escaped_notify_signal(self):
        blk = XBeeDigiMeshTX()
        self.configure_block(blk, {
            "dest_addr": "0013A200400a0127",
            "escaped":True,
            "data": "{{ $iama }}"
        })
        blk.start()
        blk.process_signals([Signal({'iama': 'TxData0A'})])
        self.assert_num_signals_notified(1, blk)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'frame':b'\x7E\x00\x16\x10\x01\x00\x7D\x33\xA2\x00\x40\x0A\x01'
            b'\x27\xFF\xFE\x00\x00\x54\x78\x44\x61\x74\x61\x30\x41\x7D\x33'})
