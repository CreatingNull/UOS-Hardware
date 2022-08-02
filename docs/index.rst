.. UOS Hardware documentation master file

UOS Hardware documentation
==========================

This project provides a python package implementing a hardware abstraction layer for communicating with microcontrollers running `UOS compliant firmware <https://wiki.nulltek.xyz/docs/projects/uos/>`_.


.. toctree::
   :maxdepth: 2
   :caption: Contents:


Supported Hardware
------------------

Supported devices are enumerated and defined in `uoshardware.devices.py`.

All devices are defined using the `Devices` abstraction class.

.. autoclass:: uoshardware.abstractions.Device
   :members:

Abstraction Layer
-----------------

Devices can be accessed through the hardware layer by instantiating a `UOSDevice`.
By default the device is used in a lazy manner, where references to the interface opened and closed automatically as required for functions.

Example usage:

This is the `hello world` usage for turning on the arduino on-board pin 13 LED.

.. code-block:: python

    from uoshardware.interface import UOSDevice
    from uoshardware.devices import ARDUINO_NANO_3

    device = UOSDevice(identity=ARDUINO_NANO_3, address="/dev/ttyUSB0")
    device.set_gpio_output(pin=13, level=1)  # switch on LED

Note: that individual pins and functions must be enabled and supported by the `Device`.

.. autoclass:: uoshardware.interface.UOSDevice
   :members:

Hardware Interfaces
-------------------

*	Stub
*	USB Serial


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
