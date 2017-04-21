import binascii
from nio.properties import Property
from nio.properties.version import VersionProperty
from nio.signal.base import Signal
from .xbee_base import XBeeBase


class XBeeRemoteAT(XBeeBase):

    """Execute Remote AT commands.

    Parameters:
        command: The command to execute, ex. 'D0', WR'
        parameter: The command parameter, ex. '05' for 'D0' command
           to set pin high
        dest_addr: 2 or 8 byte address of remote xbee to send AT command to.
            must be 8 bytes when using digimesh.
            Default value when left blank is "FF FF" which sends a broadcast.
    """

    version = VersionProperty(version='0.1.0')
    command = Property(title='AT Command (ascii)', default='ID')
    parameter = Property(title='Command Parameter (hex, ex: "05")', default='')
    dest_addr = Property(title='Destination Address \
                         (2 or 8 bytes hex, ex: "00 05")',
                         default='',
                         allow_none=True)
    frame_id = Property(title='Frame options', 
                        default="{{ $frame_id }}", 
                        hidden=True)

    def process_signals(self, signals):
        for signal in signals:
            try:
                command = self.command(signal).encode('ascii')
                parameter = \
                    binascii.unhexlify(self.parameter(signal).replace(" ", ""))
                dest_addr = \
                    binascii.unhexlify(
                        self.dest_addr(signal).replace(" ", "")) \
                        if self.dest_addr(signal) else None
                try:
                    frame_id = binascii.unhexlify(self.frame_id(signal))
                    self.logger.debug("Frame ID = {}".format(frame_id))
                except:
                    frame_id = None
                self._remote_at(command, parameter, dest_addr, frame_id)
            except:
                self.logger.exception("Failed to execute remote at command")

    def _remote_at(self, command, parameter, dest_addr, frame_id):
        self.logger.debug(
            "Executing Remote AT command: {}, with parameter: {}".format(
                command, parameter))
        # remote_at: 0x17 "Remote AT Command"
        # frame_id: 0x01
        # dest_addr: 0xFFFF broadcasts to all XBees
        # data: RF data bytes to be transmitted
        # command: The command to execute, ex. 'D0', WR'
        # parameter: The command parameter, ex. b'\x05' for 'D0' command
        #    to set pin high
        #
        # frame_id is an arbitrary value, 1 hex byte, used to associate sent 
        # packets with their responses. If set to 0 no response will be sent.
        # Could be a block property.
        if dest_addr is not None and len(dest_addr) == 8:
            packet = self._xbee._build_command('remote_at',
                    frame_id=frame_id or b'\x01',
                    dest_addr_long=dest_addr or 
                        b'\x00\x00\x00\x00\x00\x00\xFF\xFF',
                    command=command,
                    parameter=parameter)
        else:
            packet = self._xbee._build_command('remote_at',
                    frame_id=frame_id or b'\x01',
                    dest_addr=dest_addr or b'\xFF\xFF',
                    command=command,
                    parameter=parameter)
        self.notify_signals([Signal( { "frame" :
                    self._API_frame_packer(packet)
                    } )])
