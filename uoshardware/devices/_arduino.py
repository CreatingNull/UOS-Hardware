"""Module contains definitions for arduino devices."""
from uoshardware import Persistence
from uoshardware.abstractions import Device, Pin, UOSFunctions
from uoshardware.interface import Interface

_ARDUINO_NANO_3 = Device(
    name="Arduino Nano 3",
    interfaces=[Interface.STUB, Interface.SERIAL],
    functions_enabled={
        UOSFunctions.set_gpio_output.name: [Persistence.NONE],
        UOSFunctions.get_gpio_input.name: [Persistence.NONE],
        UOSFunctions.get_adc_input.name: [Persistence.NONE],
        UOSFunctions.reset_all_io.name: [Persistence.NONE],
        UOSFunctions.hard_reset.name: [Persistence.NONE],
        UOSFunctions.get_system_info.name: [Persistence.NONE],
        UOSFunctions.get_gpio_config.name: [Persistence.NONE],
    },
    digital_pins={
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
        14: Pin(gpio_out=True, gpio_in=True, pull_up=True, alias=0),
        15: Pin(gpio_out=True, gpio_in=True, pull_up=True, alias=1),
        16: Pin(gpio_out=True, gpio_in=True, pull_up=True, alias=2),
        17: Pin(gpio_out=True, gpio_in=True, pull_up=True, alias=3),
        18: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            alias=4,
        ),
        19: Pin(
            gpio_out=True,
            gpio_in=True,
            pull_up=True,
            alias=5,
        ),
    },
    analog_pins={
        0: Pin(adc_in=True, alias=14),
        1: Pin(adc_in=True, alias=15),
        2: Pin(adc_in=True, alias=16),
        3: Pin(adc_in=True, alias=17),
        4: Pin(adc_in=True, alias=18),
        5: Pin(adc_in=True, alias=19),
        6: Pin(adc_in=True),
        7: Pin(adc_in=True),
    },
    aux_params={"default_baudrate": 115200},
)


_ARDUINO_UNO_3 = Device(
    name="Arduino Uno 3",
    interfaces=_ARDUINO_NANO_3.interfaces,
    functions_enabled=_ARDUINO_NANO_3.functions_enabled,
    digital_pins=_ARDUINO_NANO_3.digital_pins,
    analog_pins={
        0: Pin(adc_in=True, alias=14),
        1: Pin(adc_in=True, alias=15),
        2: Pin(adc_in=True, alias=16),
        3: Pin(adc_in=True, alias=17),
        4: Pin(adc_in=True, alias=18),
        5: Pin(adc_in=True, alias=19),
        # Uno has 2 less ADCs pins than the nano.
    },
    aux_params={"default_baudrate": 115200},
)
