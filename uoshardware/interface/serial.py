"""Module defining the low level UOSImplementation for serial port devices."""
import platform
from logging import getLogger as Log
from time import sleep, time_ns

import serial
from serial.serialutil import SerialException
from serial.tools import list_ports

from uoshardware import UOSCommunicationError
from uoshardware.abstractions import ComResult, UOSInterface

if platform.system() == "Linux":
    import termios  # pylint: disable=E0401


class Serial(UOSInterface):
    """Pyserial class that handles reading / writing to ports.

    :ivar _device: Holds the pyserial device once opened. None if not opened.
    :ivar _connection: Holds the standard connection string 'Interface'|'OS Connection String.
    :ivar _port: Holds the port class, none type if device not instantiated.
    :ivar _kwargs: Additional keyword arguments as defined in the documentation.
    """

    _device = None

    _connection = ""
    _port = None
    _kwargs: dict = {}

    def __init__(self, connection: str, **kwargs):
        """Create an NPCSerialPort device.

        :param connection: OS connection string for the serial port.
        """
        self._connection = connection
        self._port = self.check_port_exists(connection)
        self._kwargs = kwargs
        if self._port is None:
            Log(__name__).error("%s port does not exist", connection)
        else:
            Log(__name__).debug("%s located", self._port)

    def open(self):
        """Open a connection to the port and creates the device object."""
        try:
            self._port = self.check_port_exists(self._connection)
            if self._port is None:
                Log(__name__).error(
                    "%s device was not present to open", self._connection
                )
                raise UOSCommunicationError("Device could not be found on system.")
            self._device = serial.Serial()
            self._device.port = self._connection
            if "baudrate" in self._kwargs:
                self._device.baudrate = self._kwargs["baudrate"]
            if platform.system() == "Linux":  # DTR transient workaround for Unix
                Log(__name__).debug("Linux platform found so using DTR workaround")
                with open(self._connection, mode="rb") as port:
                    attrs = termios.tcgetattr(port)
                    attrs[2] = attrs[2] & ~termios.HUPCL
                    termios.tcsetattr(port, termios.TCSAFLUSH, attrs)
            else:  # DTR transient workaround for Windows
                self._device.dtr = False
            self._device.open()
            Log(__name__).debug("%s opened successfully", self._port.device)
            return
        except (SerialException, FileNotFoundError) as exception:
            Log(__name__).error(
                "Opening %s threw error %s",
                self._port.device if self._port is not None else "None",
                str(exception),
            )
            if (
                exception.errno == 13
            ):  # permission denied another connection open to this device.
                Log(__name__).error(
                    "Cannot open connection, account has insufficient permissions."
                )
                raise UOSCommunicationError(
                    "Cannot open connection insufficient permissions."
                ) from exception
            raise UOSCommunicationError(
                f"Failed to open device '{exception}'"
            ) from exception

    def close(self):
        """Close the serial connection and clear the device."""
        if self._device is None:
            return  # already closed
        try:
            self._device.close()
        except SerialException as exception:
            Log(__name__).debug("Closing the connection threw error %s", str(exception))
            raise UOSCommunicationError(
                f"Closing connection threw error '{exception}'."
            ) from exception
        Log(__name__).debug("Connection closed successfully")
        self._device = None

    # Kwargs is defined in the abstractmethod definition, false positive.
    def execute_instruction(self, address, payload, **kwargs):  # dead: disable
        """Build and execute a new instruction packet.

        :param address: An 8-bit unsigned integer of the UOS subsystem targeted by the instruction.
        :param payload: A tuple containing the uint8 parameters of the UOS instruction.
        :return: Tuple containing a status boolean and index 0 and a result-set dict at index 1.
        """
        if self._device is None:
            raise UOSCommunicationError(
                "Connection must be open to execute instructions."
            )
        packet = self.get_npc_packet(to_addr=address, from_addr=0, payload=payload)
        Log(__name__).debug("packet formed %s", packet)
        try:  # Send the packet.
            num_bytes = self._device.write(packet)
            self._device.flush()
            Log(__name__).debug("Sent %s bytes of data", num_bytes)
        except serial.SerialException as exception:
            raise UOSCommunicationError(
                f"Executing instruction threw error '{exception}'"
            ) from exception
        finally:
            self._device.reset_output_buffer()
        return ComResult(num_bytes == len(packet))

    def read_response(self, expect_packets: int, timeout_s: float):
        """Read ACK and response packets from the serial device.

        :param expect_packets: How many packets including ACK to expect.
        :param timeout_s: The maximum time this function will wait for data.
        :return: ComResult object.
        """
        if self._device is None:
            raise UOSCommunicationError(
                "Connection must be open to read response from device."
            )
        response_object = ComResult(False)
        start_ns = time_ns()
        packet: list = []
        byte_index = -1  # tracks the byte position index of the current packet
        packet_index = 0  # tracks the packet number being received 0 = ACK
        try:
            while (
                timeout_s * 1000000000
            ) > time_ns() - start_ns and byte_index > -2:  # read until packet or timeout
                num_bytes = self._device.in_waiting
                for _ in range(num_bytes):
                    byte_in = self._device.read(1)
                    byte_index, packet = self.decode_and_capture(
                        byte_index, byte_in, packet
                    )
                    if byte_index == -2:
                        if packet_index == 0:
                            response_object.ack_packet = packet
                        else:
                            response_object.rx_packets.append(packet)
                        packet_index += 1
                        if expect_packets == packet_index:
                            break
                        byte_index = -1
                        packet = []
                    byte_index += 1
                sleep(0.05)  # Don't churn CPU cycles waiting for data
            Log(__name__).debug("Packet received %s", packet)
            if expect_packets != packet_index or len(packet) < 6 or byte_index != -2:
                response_object.rx_packets.append(packet)
                response_object.exception = "did not receive all the expected data"
                return response_object
            response_object.status = True
            return response_object
        except serial.SerialException as exception:
            raise UOSCommunicationError(
                f"Reading response raised exception '{exception}'"
            ) from exception

    def hard_reset(self):
        """Manually drive the DTR line low to reset the device.

        :return: Tuple containing a status boolean and index 0 and a result-set dict at index 1.
        """
        if self._device is None:
            raise UOSCommunicationError("Connection must be open to hard reset device.")
        Log(__name__).debug("Resetting the device using the DTR line")
        self._device.dtr = not self._device.dtr
        sleep(0.2)
        self._device.dtr = not self._device.dtr
        return ComResult(True)

    def is_active(self) -> bool:
        """Check if connection is active to the device."""
        return self._device is not None

    def __repr__(self):
        """Representation of object.

        :return: String containing connection, port and device.
        """
        return (
            f"<NPCSerialPort(_connection='{self._connection}', _port={self._port}, "
            f"_device={self._device})>"
        )

    @staticmethod
    def decode_and_capture(
        byte_index: int, byte_in: bytes, packet: list
    ) -> tuple[int, list]:
        """Parser takes in a byte and vets it against UOS packet.

        :param byte_index: The index of the last 'valid' byte found.
        :param byte_in: The current byte for inspection.
        :param packet: The current packet of validated bytes.
        :return: Tuple containing the updated byte index and updated packet.
        """
        if byte_index == -1:  # start symbol
            if byte_in == b">":
                byte_index += 1
        if byte_index >= 0:
            Log(__name__).debug(
                "read %s byte index = %s",
                byte_in,
                byte_index,
            )
            payload_len = packet[3] if len(packet) > 3 else 0
            if byte_index == 3 + 2 + payload_len:  # End packet symbol
                if byte_in == b"<":
                    byte_index = -2  # packet complete
                    Log(__name__).debug("Found end packet symbol")
                else:  # Errored data
                    byte_index = -1
                    packet = []
            packet.append(int.from_bytes(byte_in, byteorder="little"))
        return byte_index, packet

    @staticmethod
    def enumerate_devices():
        """Get the available ports on the system."""
        return [Serial(port.device) for port in list_ports.comports()]

    @staticmethod
    def check_port_exists(device: str):
        """Check if serial device is available on system.

        :param device: OS connection string for the serial port.
        :return: The port device class if it exists, else None.
        """
        ports = list_ports.comports()
        for port in ports:
            if device in port.device:
                return port
        return None
