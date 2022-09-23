"""Module defining the base class and static func for interfaces."""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache

from uoshardware import Persistence, UOSUnsupportedError


@dataclass
class UOSFunction:
    """Defines auxiliary information for UOS commands in the schema."""

    name: str
    address_lut: dict
    ack: bool
    rx_packets_expected: list = field(default_factory=list)
    pin_requirements: list | None = None


@dataclass(init=False, repr=False, frozen=True)
class UOSFunctions:
    """Class enumerates UOS functions and function requirements."""

    set_gpio_output = UOSFunction(
        name="set_gpio_output",
        address_lut={Persistence.NONE: 64},
        ack=True,
        pin_requirements=["gpio_out"],
    )
    get_gpio_input = UOSFunction(
        name="get_gpio_input",
        address_lut={Persistence.NONE: 64},
        ack=True,
        rx_packets_expected=[1],
        pin_requirements=["gpio_in"],
    )
    get_adc_input = UOSFunction(
        name="get_adc_input",
        address_lut={Persistence.NONE: 85},
        ack=True,
        rx_packets_expected=[2],
        pin_requirements=["adc_in"],
    )
    reset_all_io = UOSFunction(
        name="reset_all_io", address_lut={Persistence.NONE: 68}, ack=True
    )
    hard_reset = UOSFunction(
        name="hard_reset", address_lut={Persistence.NONE: -1}, ack=False
    )
    get_system_info = UOSFunction(
        name="get_system_info",
        address_lut={Persistence.NONE: 250},
        ack=True,
        rx_packets_expected=[6],
    )
    get_gpio_config = UOSFunction(
        name="get_gpio_config",
        address_lut={Persistence.NONE: 251},
        ack=True,
        rx_packets_expected=[2],
        pin_requirements=[],
    )

    @staticmethod
    def enumerate_functions() -> list:
        """Return all the defined UOSFunction objects."""
        return [
            getattr(UOSFunctions, member_name)
            for member_name in dir(UOSFunctions)
            if isinstance(getattr(UOSFunctions, member_name), UOSFunction)
        ]


@dataclass
class ComResult:
    """Containing the data structure used to capture UOS results."""

    status: bool
    exception: str = ""
    ack_packet: list = field(default_factory=list)
    rx_packets: list = field(default_factory=list)
    aux_data: dict = field(default_factory=dict)


@dataclass
class InstructionArguments:
    """Containing the data structure used to generalise UOS arguments."""

    payload: tuple = ()
    expected_rx_packets: int = 1
    check_pin: int | None = None
    volatility: Persistence = Persistence.NONE


class UOSInterface(metaclass=ABCMeta):
    """Base class for low level UOS interfaces classes to inherit."""

    # Dead code suppression used as abstract interfaces are false positives.
    @abstractmethod
    def execute_instruction(
        self, address: int, payload: tuple[int, ...], **kwargs  # dead: disable
    ) -> ComResult:
        """Abstract method for executing instructions on UOSInterfaces.

        :param address: An 8-bit unsigned integer of the UOS subsystem targeted by the instruction.
        :param payload: A tuple containing the uint8 parameters of the UOS instruction.
        :returns: ComResult object.
        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        :raises: UOSCommunicationError if there is a problem completing the action.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.execute_instruction.__name__} prototype."
        )

    @abstractmethod
    def read_response(
        self, expect_packets: int, timeout_s: float  # dead: disable
    ) -> ComResult:
        """Read ACK and Data packets from a UOSInterface.

        :param expect_packets: How many packets including ACK to expect
        :param timeout_s: The maximum time this function will wait for data.
        :return: COM Result object.
        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        :raises: UOSCommunicationError if there is a problem completing the action.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.read_response.__name__} prototype."
        )

    @abstractmethod
    def hard_reset(self) -> ComResult:
        """UOS loop reset functionality should be as hard a reset as possible.

        :return: COM Result object.
        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        :raises: UOSCommunicationError if there is a problem completing the action.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.hard_reset.__name__} prototype"
        )

    @abstractmethod
    def open(self):
        """Abstract method for opening a connection to a UOSInterface.

        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        :raises: UOSCommunicationError if there is a problem completing the action.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.open.__name__} prototype."
        )

    @abstractmethod
    def close(self):
        """Abstract method for closing a connection to a UOSInterface.

        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        :raises: UOSCommunicationError if there is a problem completing the action.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.close.__name__} prototype."
        )

    @abstractmethod
    def is_active(self) -> bool:
        """Abstract method for checking if a connection is being held active.

        :return: Success boolean.
        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.close.__name__} prototype."
        )

    @staticmethod
    @abstractmethod
    def enumerate_devices() -> list:
        """Return a list of UOSDevices visible to the driver.

        :return: A list of possible UOSInterfaces on the server.
        :raises: UOSUnsupportedError if the interface hasn't been built correctly.
        """
        raise UOSUnsupportedError(
            f"UOSInterfaces must over-ride {UOSInterface.enumerate_devices.__name__} prototype."
        )

    @staticmethod
    @lru_cache(maxsize=100)
    def get_npc_packet(to_addr: int, from_addr: int, payload: tuple[int, ...]) -> bytes:
        """Generate a standardised NPC binary packet.

        :param to_addr: An 8-bit unsigned integer of the UOS subsystem targeted by the instruction.
        :param from_addr: An 8-bit unsigned integer of the host system, usually 0.
        :param payload: A tuple containing the unsigned 8-bit integers of the command.
        :return: NPC packet as a bytes object. No bytes returned on fault.
        """
        if (
            to_addr < 256 and from_addr < 256 and len(payload) < 256
        ):  # check input is possible to parse
            packet_data = tuple([to_addr, from_addr, len(payload)] + list(payload))
            lrc = UOSInterface.get_npc_checksum(packet_data)
            return bytes(
                [0x3E, packet_data[0], packet_data[1], len(payload)]
                + list(payload)
                + [lrc, 0x3C]
            )
        return bytes([])

    @staticmethod
    def get_npc_checksum(packet_data: tuple[int, ...]) -> int:
        """Generate a NPC LRC checksum.

        :param packet_data: List of the uint8 values from an NPC packet.
        :return: NPC checksum as a 8-bit integer.
        """
        lrc = 0
        for byte in packet_data:
            lrc = (lrc + byte) & 0xFF
        return ((lrc ^ 0xFF) + 1) & 0xFF


@dataclass
class Pin:
    """Defines supported features of the pin."""

    # pylint: disable=too-many-instance-attributes
    # Due to the nature of embedded pin complexity.

    gpio_out: bool = False
    gpio_in: bool = False
    dac_out: bool = False
    pwm_out: bool = False
    adc_in: bool = False
    pull_up: bool = False
    pull_down: bool = False
    pc_int: bool = False
    hw_int: bool = False
    timer: dict = field(default_factory=dict)
    comp: dict = field(default_factory=dict)
    spi: dict = field(default_factory=dict)
    i2c: dict = field(default_factory=dict)


@dataclass
class Device:
    """Define an implemented UOS device dictionary."""

    name: str
    versions: dict
    interfaces: list
    functions_enabled: dict
    digital_pins: dict = field(default_factory=dict)
    analogue_pins: dict = field(default_factory=dict)
    aux_params: dict = field(default_factory=dict)

    def get_compatible_pins(self, function: UOSFunction) -> dict:
        """Return a dict of pin objects that are suitable for a function.

        :param function: the string name of the UOS Schema function.
        :return: Dict of pin objects, keyed on pin index.
        """
        if (
            not isinstance(function, UOSFunction)
            or function not in UOSFunctions.enumerate_functions()
        ):
            raise UOSUnsupportedError(f"UOS function {function.name} doesn't exist.")
        requirements = function.pin_requirements
        if requirements is None:  # pins are not relevant to this function
            return {}
        pin_dict = self.analogue_pins if "adc_in" in requirements else self.digital_pins
        return {
            pin_name: pin
            for pin_name, pin in pin_dict.items()
            if all(hasattr(pin, requirement) for requirement in requirements)
        }
