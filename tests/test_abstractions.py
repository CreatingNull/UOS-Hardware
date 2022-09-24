"""Unit tests for the abstractions module."""
import pytest

from tests import Packet
from uoshardware import UOSUnsupportedError
from uoshardware.abstractions import UOSInterface

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


def test_execute_instruction():
    """Using the base class directly should throw an error."""
    with pytest.raises(UOSUnsupportedError):
        # noinspection PyTypeChecker
        UOSInterface.execute_instruction(self=None, address=10, payload=())


def test_read_response():
    """Using the base class directly should throw an error."""
    with pytest.raises(UOSUnsupportedError):
        # noinspection PyTypeChecker
        UOSInterface.read_response(self=None, expect_packets=1, timeout_s=2)


def test_enumerate_devices():
    """Using the base class directly should throw an error."""
    with pytest.raises(UOSUnsupportedError):
        UOSInterface.enumerate_devices()


@pytest.mark.parametrize("func", ["hard_reset", "is_active", "open", "close"])
def test_abstract_functions(func):
    """Using the base class directly should throw an error."""
    with pytest.raises(UOSUnsupportedError):
        getattr(UOSInterface, func)(self=None)


def test_close():
    """Using the base class directly should throw an error."""
    with pytest.raises(UOSUnsupportedError):
        # noinspection PyTypeChecker
        UOSInterface.close(self=None)


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
