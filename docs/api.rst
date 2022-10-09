.. Source file outline how to use tooling

Getting Started
===============


Supported Hardware
------------------

Supported devices are enumerated and defined in `uoshardware.devices.py`
module.

.. autoclass:: uoshardware.devices.Devices

All names defined in `Devices` link to a defined `Device` abstraction
class. This class defines hardware and firmware functionality for the
device.

.. autoclass:: uoshardware.abstractions.Device
   :members:

Abstraction Layer
-----------------

Devices can be accessed through the hardware layer by instantiating a
`UOSDevice`. By default the device is used in a lazy manner, where
references to the interface opened and closed automatically as required
for functions.

Example usage:

This is the `hello world` usage for turning on the arduino on-board pin
13 LED.

.. code-block:: python

    from uoshardware.api import UOSDevice
    from uoshardware.devices import Devices

    with UOSDevice(identity=Devices.arduino_nano, address="/dev/ttyUSB0") as device:
        device.set_gpio_output(pin=13, level=1)  # switch on LED

Note: that individual pins and functions must be enabled and supported by
the `Device`.

In the above example we are handling the connection using a Context Manager,
this is the preferred method to manage the connection as it avoids resource
conflicts.

.. autoclass:: uoshardware.api.UOSDevice
   :members:

Hardware Interfaces
-------------------

* Stub
* USB Serial
