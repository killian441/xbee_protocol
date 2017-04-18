import binascii
from nio.properties import Property
from nio.properties.version import VersionProperty
from .xbee_base import XBeeBase


class XBeeTX(XBeeBase):

    """Execute TX Command.

    XBee sends the serialized version of each input signal to thie block. It is
    sent to the configured "Distnation Address" of the XBee. That destination
    XBee will receive that serialized signal. If that block is connected to nio
    then the block will notify the signal.

    Parameters:
        dest_addr: 2 or 8 byte address of remote xbee to send AT command to.
            must be 8 bytes when using digimesh.
            Default value when left blank is "FF FF" which sends a broadcast.
    """

    version = VersionProperty(version='0.2.1')
    data = Property(title="Data", default="{{ $.to_dict() }}")
    dest_addr = Property(title='Destination Address \
                         (2 or 8 bytes hex, ex: "00 05")',
                         default='',
                         allow_none=True)

    def process_signals(self, signals):
        for signal in signals:
            data_encoded = "{}".format(self.data(signal)).encode()
            dest_addr = \
                binascii.unhexlify(self.dest_addr(signal).replace(" ", "")) \
                if self.dest_addr(signal) else None
            self.logger.debug('Sending data: {}'.format(data_encoded))
            # tx: 0x01 "Tx (Transmit) Request: 16-bit address"
            # tx: 0x10 "Tx (Transmit) Request: 64-bit address", DigiMesh
            # frame_id: 0x01
            # dest_addr: 0xFFFF appears to make it so that it sends to the		
            # configured "Destination Address" on the XBee
            # data: RF data bytes to be transmitted
            #
            # frame_id is an arbitrary value, 1 hex byte, used to associate
            # sent packets with their responses. If set to 0 no response will
            # be sent. Could be a block property.
            if self.digimesh():
                # pass all arguments to work around bug in
                # python-xbee/xbee/digimesh.py where default values are not
                # bytes
                self._xbee.send('tx',
                                id=b'\x10',
                                frame_id=b'\x01',
                                dest_addr=dest_addr or \
                                    b'\x00\x00\x00\x00\x00\x00\xFF\xFF',
                                reserved=b'\xFF\xFE',
                                broadcast_radius=b'\x00',
                                options=b'\x00',
                                data=data_encoded)
            else:
                self._xbee.send('tx',
                                frame_id=b'\x01',
                                dest_addr=dest_addr or b'\xFF\xFF',
                                data=data_encoded)
