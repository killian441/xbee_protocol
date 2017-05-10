import serial
import xbee
from time import sleep
from nio.block.base import Block
from nio.properties import StringProperty, IntProperty, BoolProperty
from nio.properties.version import VersionProperty
from nio.util.threading.spawn import spawn
from nio.util.discovery import not_discoverable


@not_discoverable
class XBeeFrameBase(Block):

    """ Generate or interpret XBee frames

    Parameters:
        escaped (bool): True uses API mode 2 
        digimesh (bool): Use DigiMesh protocol rather than XBee (IEEE 802.15.4)
    """

    version = VersionProperty(version='1.0.0')
    escaped = BoolProperty(title='Escaped characters? (API mode 2)',
                           default=True)
    digimesh = BoolProperty(title='DigiMesh',
                            default=False)

    def __init__(self):
        super().__init__()
        self._xbee = None
        self._serial = None
        self._protocol = xbee.XBee

    def configure(self, context):
        super().configure(context)
        if self.digimesh():
            self._protocol = xbee.DigiMesh
        self._connect()
        
    def process_signals(self, signals):
        for signal in signals:
            pass

    def stop(self):
        try:
            self.logger.debug('Halting XBee callback thread')
            self._xbee.halt()
            self.logger.debug('XBee halted')
        except:
            self.logger.exception('Exception while halting xbee')
        super().stop()

    def _connect(self):
        ''' Establish XBee serial connection '''
        try:
            self._serial = serial.Serial(None)
            self.logger.debug('Escaped is'
                ': {}'.format(self.escaped()))
            try:
                self._xbee = self._protocol(self._serial,
                                       escaped=self.escaped())
            except:
                self.logger.exception(
                    'An exception occurred')
        except:
            self.logger.exception('An failure occurred')

    def _API_frame_packer(self, data):
        return xbee.frame.APIFrame(data, self.escaped()).output()

    def _API_frame_unpacker(self, data):
        frame = xbee.frame.APIFrame(escaped=self.escaped())
        for byte in data:
            frame.fill(bytes([byte]))
        frame.parse()
        return self._xbee._split_response(frame.data)
