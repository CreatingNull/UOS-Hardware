"""Module for package test configuration, scope=session."""
import pytest

from uoshardware import Loading
from uoshardware.api import UOSDevice
from uoshardware.devices import Devices
from uoshardware.interface import Interface

DEVICES = {
    "Arduino Nano 3 LAZY": {
        "identity": Devices.arduino_nano,
        "address": "/dev/ttyUSB0",
        "interface": Interface.STUB,
        "loading": Loading.LAZY,
    },
    "Arduino Nano 3 EAGER": {
        "identity": Devices.arduino_nano,
        "address": "/dev/ttyUSB0",
        "interface": Interface.STUB,
        "loading": Loading.EAGER,
    },
}


@pytest.fixture(scope="session", params=list(DEVICES.keys()))
def uos_device(request):
    """Create a fixture for testing through the abstraction layer."""
    device = UOSDevice(
        DEVICES[request.param]["identity"],
        DEVICES[request.param]["address"],
        DEVICES[request.param]["interface"],
        loading=DEVICES[request.param]["loading"],
    )
    yield device
    device.close()


@pytest.fixture(scope="session", params=list(DEVICES.keys()))
def uos_errored_device(request):
    """Create a fixture for testing through the abstraction layer."""
    return UOSDevice(
        DEVICES[request.param]["identity"],
        DEVICES[request.param]["address"],
        DEVICES[request.param]["interface"],
        loading=DEVICES[request.param]["loading"],
        errored=1,
    )


@pytest.fixture(scope="session", params=list(DEVICES.keys()))
def uos_identities(request):
    """Create the device definition for testing interface config."""
    return DEVICES[request.param]


def pytest_addoption(parser):
    """Add USB serial connection optional CLI argument."""
    parser.addoption("--serial", action="store", default=None)
