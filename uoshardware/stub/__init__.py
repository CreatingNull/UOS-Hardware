"""Package is used as a simulated UOSInterface for test purposes."""
from typing import Tuple

from uoshardware.abstractions import UOS_SCHEMA, ComResult, UOSInterface


class Stub(UOSInterface):
    """Class can be used as a low level test endpoint."""

    def __init__(self, connection: str, errored: int = 0):
        """Instantiate an instance of the test stub."""
        self.__packet_buffer = []
        self.__open = False
        self.errored = errored
        self.connection = connection

    def execute_instruction(
        self,
        address: int,
        # Dead code false positive as this is over-riding an interface.
        payload: Tuple[int, ...],  # dead: disable
    ) -> ComResult:
        """Simulate executing an instruction on a UOS endpoint.

        Should check whether the last instruction was valid and store
        it. This will allow read response to provide more realistic
        responses.
        """
        if not self.__open:
            return ComResult(status=False, exception="Port must be opened first.")
        for _, function in UOS_SCHEMA.items():
            for vol in function.address_lut:
                if function.address_lut[vol] == address:
                    if function.ack:
                        self.__packet_buffer.append(
                            self.get_npc_packet(0, address, tuple([0]))
                        )
                    for rx_packet in function.rx_packets_expected:
                        self.__packet_buffer.append(
                            self.get_npc_packet(
                                0, address, tuple(0 for _ in range(rx_packet))
                            )
                        )
                    return ComResult(True)
        return ComResult(False)

    # Dead code detection false positive due to abstract interface.
    def read_response(
        self, expect_packets: int, timeout_s: float  # dead: disable
    ) -> ComResult:
        """Simulate gathering the response from an instruction.

        Should have already executed an instruction. If no response is
        generated by instruction will error accordingly.
        """
        if not self.__open:
            return ComResult(status=False, exception="Port must be opened first.")
        result = ComResult(False)
        if len(self.__packet_buffer) > 0:
            result.ack_packet = self.__packet_buffer.pop(0)
            result.status = True
        for _ in self.__packet_buffer:
            result.rx_packets.append(self.__packet_buffer.pop(0))
        return result

    def hard_reset(self) -> ComResult:
        """Override base prototype, simulates reset."""
        if not self.__open:
            return ComResult(status=False, exception="Port must be opened first.")
        return ComResult(status=True)

    def open(self) -> bool:
        """Override base prototype, simulates opening a connection."""
        if len(self.connection) > 0:
            self.__open = True
            return True
        return False

    def close(self) -> bool:
        """Override base prototype, simulates close a connection."""
        self.__open = False
        return self.errored == 0

    @staticmethod
    def enumerate_devices() -> []:
        """Return a list of test stubs implemented in the interface."""
        return [Stub("STUB")]  # The test stub is always available
