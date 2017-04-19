import binascii
from nio.properties import Property
from nio.properties.version import VersionProperty
from nio.signal.base import Signal
from .xbee_base import XBeeBase


class XBeeQueuedAT(XBeeBase):

    """ Execute AT commands
    Parameters:
        command: The command to execute, ex. 'D0', WR'
        parameter: The command parameter, ex. '05' for 'D0' command
           to set pin high
    """

    version = VersionProperty(version='0.1.0')
    command = Property(title='AT Command (ascii)',
                       default='ID')
    parameter = Property(title='Command Parameter (hex, ex: "05")',
                         default='')
    frame_id = Property(title='Frame options', 
                        default="{{ $frame_id }}", 
                        hidden=True)

    def process_signals(self, signals):
        for signal in signals:
            try:
                command = self.command(signal)
                parameter = self.parameter(signal).replace(" ", "")
                try:
                    frame_id = binascii.unhexlify(self.frame_id(signal))
                    self.logger.debug("Frame ID = {}".format(frame_id))
                except:
                    frame_id = None
                self._at(command, parameter, frame_id)
            except:
                self.logger.exception("Failed to execute queued at command")

    def _at(self, command, parameter, frame_id):
        command = command.encode('ascii')
        parameter = binascii.unhexlify(parameter)
        self.logger.debug(
            "Executing AT command: {}, with parameter: {}".format(
                command, parameter)
        )
        # at: 0x09 "Queued AT Command"
        # frame_id: 0x01
        # data: RF data bytes to be transmitted
        # command: The command to execute, ex. 'D0', WR'
        # parameter: The command parameter, ex. b'\x05' for 'D0' command
        #    to set pin high
        #
        # frame_id is an arbitrary value, 1 hex byte, used to associate sent
        # packets with their responses. If set to 0 no response will be sent.
        # Could be a block property.
        self.notify_signals([Signal( { "frame" :
                self._xbee._build_command('queued_at',
                frame_id=frame_id or b'\x01',
                command=command,
                parameter=parameter) } )])
