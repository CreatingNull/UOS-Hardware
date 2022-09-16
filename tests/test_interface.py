"""Unit tests for the hardware interface module."""
from dataclasses import dataclass
from inspect import signature

import pytest

from uoshardware import Persistence, UOSCommunicationError, UOSUnsupportedError
from uoshardware.abstractions import UOSFunction, UOSFunctions, UOSInterface
from uoshardware.api import UOSDevice
from uoshardware.devices import enumerate_system_devices
from uoshardware.interface import Interface
from uoshardware.interface.stub import Stub


@dataclass
class Packet:
    """Dataclass for storing test packet definitions."""

    address_to: int
    address_from: int
    payload: list
    checksum: int
    binary: bytes


class TestHardwareCOMInterface:
    """Tests for the object orientated abstraction layer."""

    @staticmethod
    def test_implemented_devices(uos_identities: dict):
        """Checks devices in config can init without error."""
        assert (
            UOSDevice(
                identity=uos_identities["identity"],
                address=uos_identities["address"],
                interface=uos_identities["interface"],
            )
            is not None
        )

    @staticmethod
    def test_unimplemented_devices():
        """Checks an un-implemented device throws the correct error."""
        with pytest.raises(UOSUnsupportedError):
            UOSDevice(identity="Not Implemented", address="", interface=Interface.STUB)

    @staticmethod
    @pytest.mark.parametrize("interface", Interface)  # checks all interfaces
    def test_bad_connection(uos_identities: dict, interface: Interface):
        """Checks that bad connections fail sensibly."""
        with pytest.raises(UOSCommunicationError):
            device = UOSDevice(
                uos_identities["identity"],
                "",
                interface=interface,
                loading=uos_identities["loading"],
            )
            if device.is_lazy():  # lazy connection so manually open
                device.open()

    @staticmethod
    @pytest.mark.parametrize("function", UOSFunctions.enumerate_functions())
    def test_device_function(uos_device, function: UOSFunction):
        """Checks the UOS functions respond correctly."""
        for volatility in Persistence:
            if volatility not in uos_device.device.functions_enabled[function.name]:
                continue  # Ignore unsupported volatilities for device
            pins = uos_device.device.get_compatible_pins(function)
            if pins is None or len(pins) == 0:
                pins = [0]  # insert a dummy pin for non-pinned functions.
            for pin in pins:
                api_function = getattr(uos_device, function.name)
                call_arguments = {}
                if "pin" in signature(api_function).parameters.keys():
                    call_arguments["pin"] = pin
                if "level" in signature(api_function).parameters.keys():
                    call_arguments["level"] = 0
                if "volatility" in signature(api_function).parameters.keys():
                    call_arguments["volatility"] = volatility
                result = api_function(**call_arguments)
                assert result.status
                assert len(result.rx_packets) == len(function.rx_packets_expected)
                for i, rx_packet in enumerate(result.rx_packets):
                    assert (  # packet length validation
                        len(rx_packet) == 6 + function.rx_packets_expected[i]
                    )
                    assert (  # payload length validation
                        rx_packet[3] == function.rx_packets_expected[i]
                    )

    @staticmethod
    def test_invalid_pin(uos_device):
        """Checks a pin based instruction with an invalid pin throws error."""
        with pytest.raises(UOSUnsupportedError):
            uos_device.set_gpio_output(-1, 1, volatility=Persistence.NONE)

    @staticmethod
    def test_close_error(uos_errored_device):
        """Checks error is thrown correctly on close."""
        with pytest.raises(UOSCommunicationError):
            uos_errored_device.close()

    @staticmethod
    def test_enumerate_devices():
        """Checks at least the stub is returned by the enumeration func."""
        devices = enumerate_system_devices()
        assert isinstance(devices, list)
        assert len(devices) > 0
        assert all(isinstance(device, UOSInterface) for device in devices)
        devices = enumerate_system_devices(Interface.STUB)
        assert len(devices) == 1
        assert isinstance(devices[0], Stub)


class TestHardwareCOMAbstractions:
    """Test for the UOSInterface abstraction layer and helper functions."""

    TEST_PACKETS = [
        Packet(
            address_to=0,
            address_from=1,
            payload=[1],
            checksum=253,
            binary=b">\x00\x01\x01\x01\xfd<",
        ),
        Packet(
            address_to=64,
            address_from=0,
            payload=[13, 0, 1, 12, 1, 0],
            checksum=159,
            binary=b">\x40\x00\x06\x0d\x00\x01\x0c\x01\x00\x9f<",
        ),
        Packet(  # Bad packet
            address_to=256,
            address_from=256,
            payload=[],
            checksum=0,
            binary=b"",
        ),
    ]

    @staticmethod
    def test_execute_instruction():
        """Using the base class directly should throw an error."""
        with pytest.raises(UOSUnsupportedError):
            # noinspection PyTypeChecker
            UOSInterface.execute_instruction(self=None, address=10, payload=())

    @staticmethod
    def test_read_response():
        """Using the base class directly should throw an error."""
        with pytest.raises(UOSUnsupportedError):
            # noinspection PyTypeChecker
            UOSInterface.read_response(self=None, expect_packets=1, timeout_s=2)

    @staticmethod
    def test_hard_reset():
        """Using the base class directly should throw an error."""
        with pytest.raises(UOSUnsupportedError):
            # noinspection PyTypeChecker
            UOSInterface.hard_reset(self=None)

    @staticmethod
    def test_open():
        """Using the base class directly should throw an error."""
        with pytest.raises(UOSUnsupportedError):
            # noinspection PyTypeChecker
            UOSInterface.open(self=None)

    @staticmethod
    def test_close():
        """Using the base class directly should throw an error."""
        with pytest.raises(UOSUnsupportedError):
            # noinspection PyTypeChecker
            UOSInterface.close(self=None)

    @staticmethod
    @pytest.mark.parametrize(
        "test_packet_data, expected_lrc",
        [
            [[255], 1],  # overflow case
            [[0], 0],  # base case
            [
                tuple(  # simple NPC packet case
                    [
                        TEST_PACKETS[0].address_to,
                        TEST_PACKETS[0].address_from,
                        len(TEST_PACKETS[0].payload),
                    ]
                    + list(TEST_PACKETS[0].payload)
                ),
                TEST_PACKETS[0].checksum,
            ],
            [
                tuple(  # simple NPC packet case
                    [
                        TEST_PACKETS[1].address_to,
                        TEST_PACKETS[1].address_from,
                        len(TEST_PACKETS[1].payload),
                    ]
                    + TEST_PACKETS[1].payload
                ),
                TEST_PACKETS[1].checksum,
            ],
            [
                tuple(  # simple NPC packet case
                    [
                        TEST_PACKETS[2].address_to,
                        TEST_PACKETS[2].address_from,
                        len(TEST_PACKETS[2].payload),
                    ]
                    + TEST_PACKETS[2].payload
                ),
                TEST_PACKETS[2].checksum,
            ],
        ],
    )
    def test_get_npc_checksum(test_packet_data: tuple, expected_lrc: int):
        """Checks the computation of LRC checksums for some known packets."""
        print(f"\n -> packet: {test_packet_data}, lrc:{expected_lrc}")
        assert UOSInterface.get_npc_checksum(test_packet_data) == expected_lrc

    @staticmethod
    @pytest.mark.parametrize(
        "test_packet", [TEST_PACKETS[0], TEST_PACKETS[1], TEST_PACKETS[2]]
    )
    def test_get_npc_packet(test_packet: Packet):
        """Checks packets are formed correctly from some known data."""
        print(
            f"\n -> addr_to: {test_packet.address_to}, addr_from: {test_packet.address_from}, "
            f"payload: {test_packet.payload}, packet: {test_packet.binary!r}"
        )
        assert (
            UOSInterface.get_npc_packet(
                test_packet.address_to,
                test_packet.address_from,
                tuple(test_packet.payload),
            )
            == test_packet.binary
        )
