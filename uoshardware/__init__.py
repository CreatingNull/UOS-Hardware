"""The high level interface for communicating with UOS devices."""

SUPER_VOLATILE = 0
VOLATILE = 1
NON_VOLATILE = 2


from logging import FileHandler, Formatter, getLogger
from pathlib import Path


def configure_logs(name: str, level: int, base_path: Path):
    """Per-package logs must be manually configured to prefix correctly."""
    logger = getLogger(name)
    logger.setLevel(level)
    # Dont capture to console as custom messages only, root logger captures stderr
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


class UOSConfigurationError(UOSError):
    """Exception caused by the setup / config of the UOS Device."""


class UOSDatabaseError(UOSError):
    """Caused by an exception or illegal operation on the database."""


def register_logs(level, base_path: Path):
    """Configures the log files for the hardware COM package.

    :param level: Set the logger level, debug ect. Use the constants from logging lib.
    :param base_path: Set the logging directory.
    """
    configure_logs(__name__, level=level, base_path=base_path)
