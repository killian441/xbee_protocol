XBee Protocol Blocks
===========

These blocks generate and parse raw XBee and Digimesh frames. 

-------------------------------------------------------------------------------

XBeeParseFrame
==============

Take in a raw XBee frame and outputs the individual components of the frame.

Properties
----------

-  **data**: Raw frame from XBee.

Dependencies
------------

-   [XBee](https://pypi.python.org/pypi/XBee)

Commands
--------
None

Input
-----
Any list of raw frames.

Output
------

```
{
  'id': 'rx',
  'options': b'\x01',
  'rf_data': b'signal',
  'rssi': b'\x00',
  'source_addr': b'\x11\x7E'
}
```

XBeeTXFrame
===========

Takes input data and generates a raw frame suitable to transmit.

Properties
----------

-   **dest_addr**: 2-byte or 8-byte address of receiving XBee. Defaults to `FF FF` which is broadcast.
-   **data**: Payload data to serialize. Default maximum size is 100 bytes.

Dependencies
------------

-   [XBee](https://pypi.python.org/pypi/XBee)

Commands
--------
None

Input
-----
Any list of signals.

Output
------
### default

Notifies a signal of a raw XBee frame of type 0x00 or 0x01 (depending on dest_addr)

  - **frame**: The raw XBee frame.

```
{
   'frame':b'\x7E\x00\x0B\x01\x7D\x11\x7E\x00\x73\x69\x67\x6E\x61\x6C\x74'
}

```

-------------------------------------------------------------------------------

XBeeATCommandFrame
=============

Generate [AT commands](http://examples.digi.com/wp-content/uploads/2012/07/XBee_ZB_ZigBee_AT_Commands.pdf) suitable for a local XBee.

Properties
----------

-   **command**: The command to execute, ex. `D0`, `WR`.
-   **parameter**: The command parameter, ex. `05` for `D0` command to set pin high.

Dependencies
------------

-   [XBee](https://pypi.python.org/pypi/XBee)

Commands
--------
None

Input
-----
Any list of signals.

Output
------

### default

Notifies a signal for each signal input.

  - **frame**: Raw XBee frame of local AT command.

```
{
  'frame':b'\x7E\x00\x06\x08\x4D\x49\x44\x11\x7E\x8E'
}
```

-------------------------------------------------------------------------------

XBeeRemoteAT
============

Generate [Remote AT commands](http://examples.digi.com/wp-content/uploads/2012/07/XBee_ZB_ZigBee_AT_Commands.pdf) suitable for a remote XBee.

Properties
----------

-   **command**: The command to execute, ex. `D0`, `WR`.
-   **parameter**: The command parameter, ex. `05` for `D0` command to set pin high.
-   **dest_addr**: 2-byte or 8-byte address of remote XBee to send AT command too. Default value when left blank is `FF FF` which sends a broadcast.

Dependencies
------------

-   [XBee](https://pypi.python.org/pypi/XBee)

Commands
--------
None

Input
-----
Any list of signals.

Output
------

### default

Notifies a signal for each input signal.

  - **frame**: The raw XBee frame for a Remote AT command.

```
{
  'frame':b'\x7E\x00\x11\x17\x4D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x02\x49\x44\x11\x7E\x3B'
}
```
