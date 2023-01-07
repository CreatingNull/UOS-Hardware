"""The high level interface for communicating with UOS devices."""
import logging
from enum import Enum

__author__ = "Steve Richardson (Creating Null)"
__copyright__ = f"2023, {__author__}"
# Semantic Versioning, MAJOR.MINOR.PATCH[-'pre-release-type'.'num']
__version__ = "0.6.0"
# Dead code false positive as this constant is for use outside primary project.
PROJECT = "UOS Hardware"  # dead: disable


# Dead code false positive as this enum if for client usage.
class Persistence(Enum):
    """Volatility levels that can be used in UOS instructions."""

    NONE = 0
    RAM = 1
    EEPROM = 2  # dead: disable


class Loading(Enum):
    """Set the management strategy for handling the device's connection."""

    LAZY = 0
    EAGER = 1


class UOSError(Exception):
    """Base class exception for all UOS Interface Errors."""


class UOSUnsupportedError(UOSError):
    """Exception for attempting an unknown / unsupported action."""


class UOSCommunicationError(UOSError):
    """Exception while communicating with a UOS Device."""


class UOSRuntimeError(UOSError):
    """General exception for runtime failure, usually indicates misuse."""


# Configures the global logger for the library
# Note: Clients need to initialize logging otherwise no output will be visible.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
