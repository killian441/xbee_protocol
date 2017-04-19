import serial
import xbee
from time import sleep
from nio.block.base import Block
from nio.properties import StringProperty, IntProperty, BoolProperty
from nio.util.threading.spawn import spawn
from nio.util.discovery import not_discoverable


@not_discoverable
class XBeeBase(Block):

    """ Read XBee over serial.

    Parameters:
        escaped (bool): True uses API mode 2 
        serial_port (str): COM/Serial port the XBee is connected to
        baud_rate (int): BAUD rate to communicate with the serial port
        digimesh (bool): Use DigiMesh protocol rather than XBee (IEEE 802.15.4)
    """

    escaped = BoolProperty(title='Escaped characters? (API mode 2)',
                           default=True)

    def __init__(self):
        super().__init__()
        self._xbee = None
        self._serial = None
        self._protocol = xbee.XBee

    def configure(self, context):
        super().configure(context)
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

