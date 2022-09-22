.. Source file outline how to use tooling

Getting Started
===============


Supported Hardware
------------------

Supported devices are enumerated and defined in `uoshardware.devices.py`.

All devices are defined using the `Device` abstraction class.
This class

.. autoclass:: uoshardware.abstractions.Device
   :members:

Abstraction Layer
-----------------

Devices can be accessed through the hardware layer by instantiating a `UOSDevice`.
By default the device is used in a lazy manner, where references to the interface opened and closed automatically as required for functions.

Example usage:

This is the `hello world` usage for turning on the arduino on-board pin 13 LED.

.. code-block:: python

    from uoshardware.api import UOSDevice
    from uoshardware.devices import ARDUINO_NANO_3

    with UOSDevice(identity=ARDUINO_NANO_3, address="/dev/ttyUSB0") as device:
        device.set_gpio_output(pin=13, level=1)  # switch on LED

Note: that individual pins and functions must be enabled and supported by the `Device`.

.. autoclass:: uoshardware.api.UOSDevice
   :members:

Hardware Interfaces
-------------------

* Stub
* USB Serial
