"""Packages used to define Devices supported by the library."""
from dataclasses import dataclass

from uoshardware.abstractions import Device
from uoshardware.devices._arduino import _ARDUINO_NANO_3, _ARDUINO_UNO_3


@dataclass(init=False, repr=False, frozen=True)
class Devices:
    """Names for supported hardware linking to the Device object used.

    :cvar hwid_0: device: _ARDUINO_NANO_3
    :cvar arduino_nano: device: _ARDUINO_NANO_3
    :cvar arduino_uno: device: _ARDUINO_NANO_3
    """

    # Lookup constants linking devices to importable names
    hwid_0: Device = _ARDUINO_NANO_3
    arduino_nano: Device = _ARDUINO_NANO_3
    hwid_1: Device = _ARDUINO_UNO_3
    arduino_uno: Device = _ARDUINO_UNO_3
