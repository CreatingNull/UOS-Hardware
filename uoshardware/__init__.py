"""The high level interface for communicating with UOS devices."""
from enum import Enum
from logging import FileHandler, Formatter, getLogger
from pathlib import Path

__author__ = "Steve Richardson (Creating Null)"
__copywright__ = f"2022, {__author__}"
# Semantic Versioning, MAJOR.MINOR.PATCH[-'pre-release-type'.'num']
__version__ = "0.3.0"
# Dead code false positive as this constant is for use outside primary project.
PROJECT = "UOS Hardware"  # dead: disable


# Dead code false positive as this enum if for client usage.
class Persistence(Enum):
    """Volatility levels that can be used in UOS instructions."""

    NONE = 0
    RAM = 1  # dead: disable
    EEPROM = 2  # dead: disable


class Loading(Enum):
    """Set the management strategy for handling the devices connection."""

    LAZY = 0
    EAGER = 1


# Dead code false positive as interface intended to be used by client.
def configure_logs(name: str, level: int, base_path: Path):  # dead: disable
    """Per-package logs must be manually configured to prefix correctly."""
    logger = getLogger(name)
    logger.setLevel(level)
    # Don't capture to console as custom messages only, root logger captures stderr
    logger.propagate = False
    log_dir = Path(base_path.joinpath(Path("logs/")))
    if not log_dir.exists():
        log_dir.mkdir()
    file_handler = FileHandler(log_dir.joinpath(Path(name + ".log")))
    file_handler.setFormatter(
        Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
    )
    logger.addHandler(file_handler)


class UOSError(Exception):
    """Base class exception for all UOS Interface Errors."""


class UOSUnsupportedError(UOSError):
    """Exception for attempting an unknown / unsupported action."""


class UOSCommunicationError(UOSError):
    """Exception while communicating with a UOS Device."""
