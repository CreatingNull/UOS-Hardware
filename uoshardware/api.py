"""Provides the HAL layer for communicating with the hardware."""
from uoshardware import (
    Loading,
    Persistence,
    UOSRuntimeError,
    UOSUnsupportedError,
    logger,
)
from uoshardware.abstractions import (
    ComResult,
    Device,
    InstructionArguments,
    NPCPacket,
    Pin,
    UOSFunction,
    UOSFunctions,
    UOSInterface,
)
from uoshardware.devices import Devices
from uoshardware.interface import Interface
from uoshardware.interface.serial import Serial
from uoshardware.interface.stub import Stub


# This is an interface for client implementations dead code false positive.
def enumerate_system_devices(  # dead: disable
    interface_filter: Interface | None = None,
) -> list:
    """Iterate through all interfaces and locates available devices.

    :param interface_filter: Interface enum to limit the search to a single interface type.
    :return: A list of uosinterface objects.
    """
    system_devices = []
    for interface in Interface:  # enum object
        if not interface_filter or interface_filter == interface:
            system_devices.extend(interface.value.enumerate_devices())
        if interface_filter is not None:
            break
    return system_devices


def get_device_definition(identity: str) -> Device | None:
    """Look up the system config dictionary for the defined device mappings.

    :param identity: String containing the lookup key of the device in the dictionary.
    :return: Device Object or None if not found
    """
    if identity is not None and hasattr(Devices, identity):
        device = getattr(Devices, identity)
    else:
        device = None
    return device


# Interface aimed for use by client projects, dead false positive.
class UOSDevice:  # dead: disable
    """Class for high level object-orientated control of UOS devices.

    :ivar identity: The type of device, this is must have a valid device in the config.
    :ivar address: Compliant connection string for identifying the device and interface.
    """

    __device: Device  # Device definitions as parsed from a compatible ini.
    identity = ""
    address = ""
    __device_interface: UOSInterface  # Lower level communication protocol layer.
    loading: Loading
    __kwargs: dict = {}  # Connection specific / optional parameters.

    def __init__(
        self,
        identity: str | Device,
        address: str,
        interface: Interface = Interface.SERIAL,
        loading: Loading = Loading.EAGER,
        **kwargs,
    ):
        """Instantiate a UOS device instance for communication.

        :param identity: Specify the type of device, this must exist in the device LUT.
        :param address: Compliant connection string for identifying the device and interface.
        :param interface: Set the type of interface to use for communication.
        loading: Alter the loading strategy for managing the communication.
        :param kwargs: Additional optional connection parameters as defined in documentation.
        """
        self.address = address
        self.__kwargs = kwargs
        self.loading = loading
        device = None
        if isinstance(identity, Device):
            self.identity = identity.name
            device = identity
        elif isinstance(identity, str):
            self.identity = identity
            device = get_device_definition(identity)
        if device is None:
            raise UOSUnsupportedError(
                f"'{self.identity}' does not have a valid look up table"
            )
        self.__device = device
        if (
            interface == Interface.SERIAL
            and Interface.SERIAL in self.__device.interfaces
        ):
            self.__device_interface = Serial(
                address,
                baudrate=self.__device.aux_params["default_baudrate"],
            )
        elif interface == Interface.STUB and Interface.STUB in self.__device.interfaces:
            self.__device_interface = Stub(
                connection=address,
                errored=(kwargs["errored"] if "errored" in kwargs else False),
            )
        else:
            raise UOSUnsupportedError(
                f"'{interface}' cannot be used for device `{self.identity}`"
            )
        if (
            self.loading == Loading.EAGER
        ):  # eager connections open when they are created
            self.open()
        logger.debug("Created device %s", self.__device_interface.__repr__())

    def __enter__(self):
        """Dunder function for opening the interface as a context manager."""
        return self

    # Dunder context manager prototype, false positive for dead variables.
    def __exit__(self, exc_type, exc_val, exc_tb):  # dead: disable
        """Dunder function for closing the interface as a context manager."""
        self.close()

    def set_gpio_output(
        self, pin: int, level: int, volatility: Persistence = Persistence.NONE
    ) -> ComResult:
        """Set a pin to digital output mode and sets a level on that pin.

        :param pin: The numeric number of the pin as defined in the dictionary for that device.
        :param level: The output level, 0 - low, 1 - High.
        :param volatility: How volatile should the command be, use constants from uoshardware.
        :return: ComResult object.
        """
        return self.__execute_instruction(
            UOSFunctions.set_gpio_output,
            InstructionArguments(
                payload=(pin, level),
                check_pin=pin,
                volatility=volatility,
            ),
        )

    def get_gpio_input(
        self,
        pin: int,
        pull_up: bool = False,
        volatility: Persistence = Persistence.NONE,
    ) -> ComResult:
        """Read a GPIO pins level from device and returns the value.

        :param pin: The numeric number of the pin as defined in the dictionary for that device.
        :param pull_up: Enable the internal pull-up resistor. Default is false.
        :param volatility: How volatile should the command be, use constants from uoshardware.
        :return: ComResult object.
        """
        result = self.__execute_instruction(
            UOSFunctions.get_gpio_input,
            InstructionArguments(
                payload=(pin, 1 if pull_up else 0),
                expected_rx_packets=2,
                check_pin=pin,
                volatility=volatility,
            ),
        )
        if result.status:
            self.__device.update_gpio_samples(result)
        return result

    def get_adc_input(
        self,
        pin: int,
    ) -> ComResult:
        """Read the current 10 bit ADC value.

        :param pin: The index of the analog pin to read
        :return: ComResult object containing the ADC readings.
        """
        result = self.__execute_instruction(
            UOSFunctions.get_adc_input,
            InstructionArguments(
                payload=tuple([pin]), expected_rx_packets=2, check_pin=pin
            ),
        )
        if result.status:  # update the samples in the device.
            self.__device.update_adc_samples(result)
        return result

    def get_system_info(self) -> ComResult:
        """Read the UOS version and device type.

        :return: ComResult object containing the system information.
        """
        return self.__execute_instruction(
            UOSFunctions.get_system_info,
            InstructionArguments(
                expected_rx_packets=2,
            ),
        )

    def reset_all_io(self, volatility=Persistence.RAM) -> ComResult:
        """Execute the reset IO at the defined volatility level.

        :param volatility: Where should the pins reset from, use constants from uoshardware.
        :return: ComResult object containing the result of the reset operation..
        """
        return self.__execute_instruction(
            UOSFunctions.reset_all_io,
            InstructionArguments(volatility=volatility),
        )

    def hard_reset(self) -> ComResult:
        """Hard reset functionality for the UOS Device."""
        return self.__execute_instruction(
            UOSFunctions.hard_reset,
            InstructionArguments(),
        )

    def open(self):
        """Connect to the device, explict calls are normally not required.

        :raises: UOSCommunicationError - Problem opening a connection.
        """
        self.__device_interface.open()

    def close(self):
        """Release connection, must be called explicitly if loading is eager.

        :raises: UOSCommunicationError - Problem closing the connection to an active device.
        """
        self.__device_interface.close()

    def __execute_instruction(
        self,
        function: UOSFunction,
        instruction_data: InstructionArguments,
        retry: bool = True,
    ) -> ComResult:
        """Execute a generic UOS function and get the result.

        :param function: The name of the function in the OOL.
        :param instruction_data: device_functions from the LUT, payload ect.
        :param retry: Allows the instruction to retry execution when fails.
        :return: ComResult object
        :raises: UOSUnsupportedError if function is not possible on the loaded device.
        """
        if (
            function.name not in self.__device.functions_enabled
            or (
                instruction_data.check_pin is not None
                and instruction_data.check_pin not in self.get_compatible_pins(function)
            )
            or instruction_data.volatility
            not in self.__device.functions_enabled[function.name]
        ):
            logger.debug(
                "Known functions %s", str(self.__device.functions_enabled.keys())
            )
            raise UOSUnsupportedError(
                f"{function.name}({instruction_data.volatility.name}) "
                f"has not been implemented for {self.identity}"
            )
        rx_response = ComResult(False)
        try:
            if self.loading == Loading.LAZY:  # Lazy loaded
                self.open()
            if function.address_lut[instruction_data.volatility] >= 0:
                # a normal instruction
                packet = NPCPacket(
                    to_address=function.address_lut[instruction_data.volatility],
                    from_address=0,
                    payload=instruction_data.payload,
                )
                logger.debug("Function %s assembled packet: %s", function.name, packet)
                tx_response = self.__device_interface.execute_instruction(packet)
                if tx_response.status:
                    rx_response = self.__device_interface.read_response(
                        instruction_data.expected_rx_packets, 2
                    )
                    if rx_response.status:
                        # validate checksums on all packets
                        for count in range(len(rx_response.rx_packets) + 1):
                            current_packet = (
                                rx_response.ack_packet
                                if count == 0
                                else rx_response.rx_packets[count - 1]
                            )
                            computed_checksum = NPCPacket.get_npc_checksum(
                                current_packet[1:-2]
                            )
                            logger.debug(
                                "Calculated checksum %s must match rx %s",
                                computed_checksum,
                                current_packet[-2],
                            )
                            rx_response.status = rx_response.status & (
                                computed_checksum == current_packet[-2]
                            )
                # include the tx packet for convenience
                rx_response.tx_packet = packet
            else:  # run a special action
                rx_response = getattr(self.__device_interface, function.name)()
        finally:  # Safety check for lazy loading being used outside of context manager
            if self.loading == Loading.LAZY:  # Lazy loaded
                self.close()
        if not rx_response.status and retry:
            # allow one retry per instruction due to DTR resets
            return self.__execute_instruction(function, instruction_data, False)
        return rx_response

    def is_active(self) -> bool:
        """Check if a connection is being held active to the device.

        :return: Boolean, true if connection is held active.
        """
        return self.__device_interface.is_active()

    # False positive as this is a client-facing function.
    def get_pin(self, pin: int) -> Pin:  # dead: disable
        """Return a pin object corresponding to index.

        :param pin: The index of the pin to return.
        :return: Pin object for provided index.
        """
        if pin not in self.__device.pins:
            raise UOSRuntimeError(
                f"Pin index {pin} doesn't exist for device {self.__device.name}"
            )
        return self.__device.pins[pin]

    def get_compatible_pins(self, function: UOSFunction) -> set:
        """Get pins suitable for use with a particular UOS Function.

        :param function: the string name of the UOS Schema function.
        :return: Set of pin indices which support the function.
        """
        if (
            not isinstance(function, UOSFunction)
            or function not in UOSFunctions.enumerate_functions()
        ):
            raise UOSUnsupportedError(f"UOS function {function.name} doesn't exist.")
        if function.pin_requirements is None:  # pins are not relevant to this function
            return set()
        return {
            pin_index
            for pin_index, pin in self.__device.pins.items()
            if all(
                getattr(pin, requirement) for requirement in function.pin_requirements
            )
        }

    # False positive as this is a client-facing function.
    def get_functions_enabled(self) -> dict:  # dead: disable
        """Return functions enabled for the device.

        :return: Dictionary of function names to list of Persistence levels.
        """
        return self.__device.functions_enabled

    def __repr__(self):
        """Representation of the UOS device.

        :return: String containing connection and identity of the device
        """
        return (
            f"<UOSDevice(address='{self.address}', identity='{self.identity}', "
            f"device={self.__device}, __device_interface='{self.__device_interface}', "
            f"__kwargs={self.__kwargs})>"
        )
