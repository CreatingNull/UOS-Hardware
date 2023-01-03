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
            pins = uos_device.device.get_compatible_pins(function)
            assert len(pins) > 0
            assert isinstance(pins[next(iter(pins))], Pin)
            if function == UOSFunctions.get_adc_input:
                assert all(pins[pin].adc_in for pin in pins)
            elif function == UOSFunctions.set_gpio_output:
                assert all(pins[pin].gpio_out for pin in pins)
    # Check lookup of function without pins returns empty list.
    pins = uos_device.device.get_compatible_pins(UOSFunctions.hard_reset)
    assert isinstance(pins, dict)
    assert len(pins) == 0
    # Check bad function throws unsupported error
    with pytest.raises(UOSUnsupportedError):
        uos_device.device.get_compatible_pins(
            UOSFunction(name="bad_function", address_lut={}, ack=False)
        )
