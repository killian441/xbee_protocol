import binascii
from nio.properties import Property
from nio.properties.version import VersionProperty
from nio.signal.base import Signal
from .xbee_frame_base import XBeeFrameBase


class XBeeTXFrame(XBeeFrameBase):

    """Execute TX Command.

    XBee sends the serialized version of each input signal to thie block. It is
    sent to the configured "Distnation Address" of the XBee. That destination
    XBee will receive that serialized signal. If that block is connected to nio
    then the block will notify the signal.

    Parameters:
        dest_addr: 2 byte hex address of remote xbee to send AT command to.
            Default value when left blank is "FF FF" which sends a broadcast.
    """

    version = VersionProperty(version='0.1.0')
    data = Property(title="Data", default="{{ $.to_dict() }}")
    dest_addr = Property(title='Destination Address \
                         (2 bytes hex, ex: "00 05")',
                         default='',
                         allow_none=True)
    frame_id = Property(title='Frame options', 
                        default="{{ $frame_id }}", 
                        hidden=True)

    def process_signals(self, signals):
        for signal in signals:
            data_encoded = "{}".format(self.data(signal)).encode()
            dest_addr = \
                binascii.unhexlify(self.dest_addr(signal).replace(" ", "")) \
                if self.dest_addr(signal) else None
            try:
                frame_id = binascii.unhexlify(self.frame_id(signal))
                self.logger.debug("Frame ID = {}".format(frame_id))
            except:
                frame_id = None
            self.logger.debug('Creating frame, data: {}'.format(data_encoded))
            # tx: 0x01 "Tx (Transmit) Request: 16-bit address"
            # frame_id: 0x01
            # dest_addr: 0xFFFF is the broadcast address
            # data: RF data bytes to be transmitted
            #
            # frame_id is an arbitrary value, 1 hex byte, used to associate
            # sent packets with their responses. If set to 0 no response will
            # be sent. Could be a block property.
            packet = self._xbee._build_command('tx',
                        frame_id=frame_id or b'\x01',
                        dest_addr=dest_addr or b'\xFF\xFF',
                        data=data_encoded)
            self.notify_signals([Signal( { "frame" :
                        self._API_frame_packer(packet)
                        } )])
