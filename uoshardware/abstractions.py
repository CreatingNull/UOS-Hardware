"""Module defining the base class and static func for interfaces."""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from uoshardware import Persistence, UOSRuntimeError, UOSUnsupportedError, logger


@dataclass(frozen=True)
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
        address_lut={
            Persistence.NONE: 60,
            Persistence.RAM: 70,
        },
        ack=True,
        pin_requirements=["gpio_out"],
    )
    get_gpio_input = UOSFunction(
        name="get_gpio_input",
        address_lut={
            Persistence.NONE: 61,
            Persistence.RAM: 71,
        },
        ack=True,
        rx_packets_expected=[1],
        pin_requirements=["gpio_in"],
    )
    get_adc_input = UOSFunction(
        name="get_adc_input",
        address_lut={Persistence.NONE: 90},
        ack=True,
        rx_packets_expected=[2],
        pin_requirements=["adc_in"],
    )
    reset_all_io = UOSFunction(
        name="reset_all_io", address_lut={Persistence.RAM: 79}, ack=True
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

    @staticmethod
    def enumerate_functions() -> list:
        """Return all the defined UOSFunction objects."""
        return [
            getattr(UOSFunctions, member_name)
            for member_name in dir(UOSFunctions)
            if isinstance(getattr(UOSFunctions, member_name), UOSFunction)
        ]

    @staticmethod
    def get_from_address(address: int) -> UOSFunction | None:
        """Look up function from the address."""
        for function in UOSFunctions.enumerate_functions():
            if address in function.address_lut.values():
                return function  # function located.
        return None  # function not found.


@dataclass(init=False)
class NPCPacket:
    """Class contains functions and data for the packet based communication."""

    to_address: int
    from_address: int
    payload: tuple[int, ...]
    packet: bytes

    def __init__(self, to_address: int, from_address: int, payload: tuple[int, ...]):
        """Construct a new packet object."""
        self.to_address = to_address
        self.from_address = from_address
        self.payload = payload
        self.packet = self.compute_packet()

    def compute_packet(self) -> bytes:
        """Generate a standardised NPC binary packet."""
        if (
            self.to_address < 256
            and self.from_address < 256
            and len(self.payload) < 256
        ):  # check input is possible to parse
            packet_data = tuple(
                [self.to_address, self.from_address, len(self.payload)]
                + list(self.payload)
            )
            lrc = NPCPacket.get_npc_checksum(packet_data)
            return bytes(
                [0x3E, packet_data[0], packet_data[1], len(self.payload)]
                + list(self.payload)
                + [lrc, 0x3C]
            )
        return bytes([])

    @staticmethod
    def get_npc_checksum(packet_data: tuple[int, ...]) -> int:
        """Generate a NPC LRC checksum.

        :param packet_data: List of the uint8 values from an NPC packet.
        :return: NPC checksum as an 8-bit integer.
        """
        lrc = 0
        for byte in packet_data:
            lrc = (lrc + byte) & 0xFF
        return ((lrc ^ 0xFF) + 1) & 0xFF

    def expects_ack(self) -> bool:
        """Check if this packet is expected to be acknowledged."""
        if function := UOSFunctions.get_from_address(self.to_address):
            return function.ack
        raise UOSUnsupportedError(
            "When checking `gets_ack`, "
            f"function for address {self.to_address} could not be located.",
        )

    def expects_rx_packets(self) -> list[int]:
        """Check if this packet expects rx packets from the function def."""
        if function := UOSFunctions.get_from_address(self.to_address):
            return function.rx_packets_expected
        raise UOSUnsupportedError(
            "When checking `expects_rx_packets, "
            f"function for address {self.to_address} could not be located."
        )


@dataclass
class ComResult:
    """Containing the data structure used to capture UOS results."""

    status: bool
    exception: str = ""
    ack_packet: list = field(default_factory=list)
    rx_packets: list = field(default_factory=list)
    tx_packet: NPCPacket | None = None

    def get_rx_payload(self, packet_index: int) -> list[int]:
        """Return just the payload portion of a rx packet."""
        if len(self.rx_packets) <= packet_index:
            raise UOSRuntimeError(
                f"Can't index payload {packet_index} of "
                f"{len(self.rx_packets)} rx packet(s)."
            )
        return self.rx_packets[packet_index][4:-2]


@dataclass(frozen=True)
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
    def execute_instruction(self, packet: NPCPacket) -> ComResult:  # dead: disable
        """Abstract method for executing instructions on UOSInterfaces.

        :param packet: A tuple containing the uint8 npc packet for the UOS instruction.
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


@dataclass(init=False)
class Sample:
    """A converted response from a reading on a pin."""

    raw_value: int
    value: float
    time: datetime


@dataclass(init=False)
class ADCSample(Sample):
    """ADC specific Sample constructor for ADC readings."""

    def __init__(self, raw_value: list[int], steps: int, reference: float):
        """Create an ADC Sample."""
        self.raw_value = int(bytes(raw_value).hex(), 16)  # convert bytes to int
        self.value = (self.raw_value / steps) * reference
        self.time = datetime.now()
        logger.debug(
            "Constructing ADCSample from `%s` with adc steps `%s` and ref `%s`",
            self.raw_value,
            steps,
            reference,
        )


@dataclass(init=False)
class DigitalSample(Sample):
    """Digital specific sample constructor for gpio reads."""

    def __init__(self, raw_value: int):
        """Create a Digital GPIO Sample."""
        self.raw_value = raw_value
        self.value = raw_value
        self.time = datetime.now()


@dataclass
class Pin:
    """Defines supported features of the pin."""

    # pylint: disable=too-many-instance-attributes
    # Due to the nature of embedded pin complexity.

    index: int = -1

    gpio_out: bool = False
    gpio_in: bool = False
    dac_out: bool = False
    pwm_out: bool = False
    adc_in: bool = False
    pull_up: bool = False
    pull_down: bool = False
    aliases: list = field(default_factory=list)

    # Values updated during runtime.
    gpio_reading: DigitalSample | None = None
    adc_reading: ADCSample | None = None


@dataclass(frozen=True)
class Device:
    """Class defines hardware for an implemented UOS device."""

    name: str
    interfaces: list
    functions_enabled: dict
    pins: dict[int, Pin] = field(default_factory=dict)
    aux_params: dict = field(default_factory=dict)

    def update_adc_samples(self, result: ComResult):
        """Update the pin samples with the response of a get_adc_input."""
        if not result.status:
            raise UOSRuntimeError("Can't update ADC samples from a failed response.")
        if result.tx_packet is None or len(result.rx_packets) < 1:
            raise UOSRuntimeError("Can't update ADC samples without a valid result.")
        if (
            "adc_reference" not in self.aux_params
            or "adc_resolution" not in self.aux_params
        ):
            raise UOSRuntimeError("Device not properly defined for ADC updates.")
        sample_values = result.get_rx_payload(0)
        logger.debug("Device returned sampled adc values %s", sample_values)
        for sample_index, pin in enumerate(result.tx_packet.payload):
            if pin not in self.pins:
                raise UOSRuntimeError(
                    f"Can't update ADC samples on pin {pin} as it's invalid for {self.name}."
                )
            self.pins[pin].adc_reading = ADCSample(
                sample_values[sample_index * 2 : sample_index * 2 + 2],
                steps=pow(2, self.aux_params["adc_resolution"]),
                reference=self.aux_params["adc_reference"],
            )
            logger.debug(
                "Setting pin %s adc reading to %s",
                pin,
                # This is a false call as it can't be None here.
                self.pins[pin].adc_reading.value,  # type: ignore
            )

    def update_gpio_samples(self, result: ComResult):
        """Update the pin samples with the response of a get_gpio_inpout."""
        if not result.status:
            raise UOSRuntimeError("Can't update GPIO samples from a failed responsee.")
        if result.tx_packet is None or len(result.rx_packets) < 1:
            raise UOSRuntimeError("Can't update GPIO samples without a valid result.")
        sample_values = result.get_rx_payload(0)
        logger.debug("Device returned sampled gpio values %s", sample_values)
        for sample_index, pin in enumerate(sample_values):
            pin = result.tx_packet.payload[2 * sample_index]
            if pin not in self.pins:
                raise UOSRuntimeError(
                    f"Can't update GPIO samples on pin {pin} as it's invalid for {self.name}."
                )
            self.pins[pin].gpio_reading = DigitalSample(sample_values[sample_index])
            logger.debug(
                "Setting pin %s gpio reading to %s",
                pin,
                # This is a false call as it can't be None here.
                self.pins[pin].gpio_reading.value,  # type: ignore
            )
