"""The high level interface for communicating with UOS devices."""
from enum import Enum
from logging import FileHandler, Formatter, getLogger
from pathlib import Path


# Dead code false positive as this enum if for client usage.
class Level(Enum):
    """Enum object defining volatility levels that can be used in UOS
    instructions."""

    SUPER_VOLATILE = 0
    VOLATILE = 1  # dead: disable
    NON_VOLATILE = 2  # dead: disable


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
