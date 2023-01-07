"""Module contains definitions for arduino devices."""
from uoshardware import Persistence
from uoshardware.abstractions import Device, Pin, UOSFunctions
from uoshardware.interface import Interface

_ARDUINO_NANO_3 = Device(
    name="Arduino Nano 3",
    interfaces=[Interface.STUB, Interface.SERIAL],
    functions_enabled={
        UOSFunctions.set_gpio_output.name: [Persistence.NONE, Persistence.RAM],
        UOSFunctions.get_gpio_input.name: [Persistence.NONE, Persistence.RAM],
        UOSFunctions.get_adc_input.name: [Persistence.NONE],
        UOSFunctions.reset_all_io.name: [Persistence.RAM],
        UOSFunctions.hard_reset.name: [Persistence.NONE],
        UOSFunctions.get_system_info.name: [Persistence.NONE],
    },
    pins={
        2: Pin(gpio_out=True, gpio_in=True, pull_up=True),
        3: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            pwm_out=True,
        ),
        4: Pin(gpio_out=True, gpio_in=True, pull_up=True),
        5: Pin(gpio_out=True, gpio_in=True, pull_up=True, pwm_out=True),
        6: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            pwm_out=True,
        ),
        7: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
        ),
        8: Pin(gpio_out=True, gpio_in=True, pull_up=True),
        9: Pin(gpio_out=True, gpio_in=True, pull_up=True, pwm_out=True),
        10: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            pwm_out=True,
        ),
        11: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            pwm_out=True,
        ),
        12: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
        ),
        13: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
        ),
        14: Pin(gpio_out=True, gpio_in=True, pull_up=True, aliases=["A0"], adc_in=True),
        15: Pin(gpio_out=True, gpio_in=True, pull_up=True, aliases=["A1"], adc_in=True),
        16: Pin(gpio_out=True, gpio_in=True, pull_up=True, aliases=["A2"], adc_in=True),
        17: Pin(gpio_out=True, gpio_in=True, pull_up=True, aliases=["A3"], adc_in=True),
        18: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            adc_in=True,
            aliases=["A4"],
        ),
        19: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            adc_in=True,
            aliases=["A5"],
        ),
        20: Pin(
            adc_in=True,
            aliases=["A6"],
        ),
        21: Pin(
            adc_in=True,
            aliases=["A7"],
        ),
    },
    aux_params={"default_baudrate": 115200, "adc_reference": 5, "adc_resolution": 10},
)


_ARDUINO_UNO_3 = Device(
    name="Arduino Uno 3",
    interfaces=_ARDUINO_NANO_3.interfaces,
    functions_enabled=_ARDUINO_NANO_3.functions_enabled,
    pins={  # Doesn't expose the additional mux'd ADCs.
        pin_index: pin
        for pin_index, pin in _ARDUINO_NANO_3.pins.items()
        if pin_index not in {20, 21}
    },
    aux_params={"default_baudrate": 115200, "adc_reference": 5, "adc_resolution": 10},
)
