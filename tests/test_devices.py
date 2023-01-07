"""Tests for the devices module."""
import pytest

from uoshardware import UOSUnsupportedError
from uoshardware.abstractions import Pin, UOSFunction, UOSFunctions
from uoshardware.api import UOSDevice


def test_get_compatible_pins(uos_device: UOSDevice):
    """Checks the device function for returning lists of compatible pins."""
    # Check lookup of digital / analog pins works.
    for function in (
        UOSFunctions.set_gpio_output,
        UOSFunctions.get_gpio_input,
        UOSFunctions.get_adc_input,
    ):
        if function.name in uos_device.device.functions_enabled:
            pins_indices = uos_device.device.get_compatible_pins(function)
            assert len(pins_indices) > 0
            for pin_index in pins_indices:
                pin = uos_device.get_pin(pin_index)
                assert isinstance(pin, Pin)
                if function == UOSFunctions.get_adc_input:
                    assert pin.adc_in
                elif function == UOSFunctions.set_gpio_output:
                    assert pin.gpio_out
    # Check lookup of function without pins returns empty list.
    pins = uos_device.device.get_compatible_pins(UOSFunctions.hard_reset)
    assert isinstance(pins, set)
    assert len(pins) == 0
    # Check bad function throws unsupported error
    with pytest.raises(UOSUnsupportedError):
        uos_device.device.get_compatible_pins(
            UOSFunction(name="bad_function", address_lut={}, ack=False)
        )
