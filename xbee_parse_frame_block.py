import binascii
from nio.properties import Property
from nio.properties.version import VersionProperty
from nio.signal.base import Signal
from .xbee_frame_base import XBeeFrameBase


class XBeeParseFrame(XBeeFrameBase):

    """Parse Frame.

    Take a XBee Frame as an input signal and output a signal composed of the
    individual frame components.

    Parameters:
        data: An XBee frame, can either be with a start byte and checksum
            or only the data packet. 
    """

    version = VersionProperty(version='0.1.0')
    data = Property(title="Data", default="{{ $ }}")

    def process_signals(self, signals):
        for signal in signals:
            if isinstance(self.data(signal),bytes):
                data_encoded = self.data(signal)
            else:
                data_encoded = "{}".format(self.data(signal)).encode()
            try:
                frame = self._API_frame_unpacker(data_encoded)
                self.notify_signals([Signal( { "frame" : frame } )])
            except:
                self.logger.exception("Failed to parse frame")
