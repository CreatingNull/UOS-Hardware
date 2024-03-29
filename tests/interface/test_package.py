"""Module for testing the interface package."""
from time import sleep

import pytest

from uoshardware import UOSCommunicationError
from uoshardware.abstractions import NPCPacket
from uoshardware.interface.serial import Serial

# Allow access to protected members in test module.
# Intended as protected only for safety in client code.
# pylint: disable=W0212


class TestSerialPort:
    """Test suite for the low level serial backend."""

    @staticmethod
    @pytest.fixture(scope="class")
    def npc_serial_port(usb_serial_argument):
        """Fixture to connect to a physical UOS device for testing."""
        serial_port = Serial(usb_serial_argument, baudrate=115200)
        yield serial_port
        serial_port.close()

    @staticmethod
    @pytest.fixture(scope="class")
    def invalid_serial_port():
        """Fixture to attempt a connection to an invalid device."""
        serial_port = Serial("not_a_valid_connection")
        return serial_port

    @staticmethod
    def test_basic_functions(npc_serial_port: Serial):
        """Checks some low level execution on a NPCSerialPort fixture."""
        # This shouldn't raise an error on opening
        assert npc_serial_port.open() is None
        assert npc_serial_port._device is not None
        sleep(2)  # Allow the system time to boot
        assert npc_serial_port.execute_instruction(NPCPacket(61, 0, (13, 1))).status
        response = npc_serial_port.read_response(expect_packets=1, timeout_s=2)
        assert response.status
        assert npc_serial_port.hard_reset()
        # Shouldn't raise an error on close
        assert npc_serial_port.close() is None
        # should be safe to close an already closed connection
        assert npc_serial_port.close() is None
        assert npc_serial_port._device is None
        assert isinstance(npc_serial_port.enumerate_devices(), list)

    @staticmethod
    def test_basic_fault_cases(invalid_serial_port: Serial):
        """Checks the invalid fixture fails correctly."""
        assert invalid_serial_port._device is None
        with pytest.raises(UOSCommunicationError):
            invalid_serial_port.open()
        assert invalid_serial_port.close() is None
        with pytest.raises(UOSCommunicationError):
            invalid_serial_port.execute_instruction(NPCPacket(64, 0, (13, 0, 1)))
        with pytest.raises(UOSCommunicationError):
            invalid_serial_port.read_response(expect_packets=1, timeout_s=1)
