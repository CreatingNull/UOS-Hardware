"""Module used for fixture initialisation in interface tests."""
import pytest


@pytest.fixture(scope="package")
def usb_serial_argument(request):
    """Create a serial fixture if --serial argument provided to CLI."""
    usb_serial_connection = request.config.option.serial
    if usb_serial_connection is None:
        pytest.skip("Low level hardware only tested if connection is provided to test.")
    return usb_serial_connection
