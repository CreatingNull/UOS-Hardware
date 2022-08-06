"""Package defining io interfaces used for NPC Comms."""
from enum import Enum

from uoshardware.interface.serial import Serial
from uoshardware.interface.stub import Stub


class Interface(Enum):
    """Enumerate interface module names."""

    STUB = Stub
    SERIAL = Serial
