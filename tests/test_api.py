"""Unit tests for the api module."""
from inspect import signature

import pytest

from uoshardware import Persistence, UOSCommunicationError, UOSUnsupportedError
from uoshardware.abstractions import UOSFunction, UOSFunctions, UOSInterface
from uoshardware.api import UOSDevice, enumerate_system_devices
from uoshardware.interface import Interface
from uoshardware.interface.stub import Stub


def test_implemented_devices(uos_identities: dict):
    """Checks devices in config can init without error."""
    assert (
        UOSDevice(
            identity=uos_identities["identity"],
            address=uos_identities["address"],
            interface=uos_identities["interface"],
        )
        is not None
    )


def test_unimplemented_devices():
    """Checks an un-implemented device throws the correct error."""
    with pytest.raises(UOSUnsupportedError):
        UOSDevice(identity="Not Implemented", address="", interface=Interface.STUB)


@pytest.mark.parametrize("interface", Interface)  # checks all interfaces
def test_bad_connection(uos_identities: dict, interface: Interface):
    """Checks that bad connections fail sensibly."""
    with pytest.raises(UOSCommunicationError):
        device = UOSDevice(
            uos_identities["identity"],
            "",
            interface=interface,
            loading=uos_identities["loading"],
        )
        if device.is_lazy():  # lazy connection so manually open
            device.open()


def test_context_manager(uos_identities: dict):
    """Check UOS devices can be used as context managers."""
    with UOSDevice(
        uos_identities["identity"],
        uos_identities["address"],
        uos_identities["interface"],
        loading=uos_identities["loading"],
    ) as device:
        # Check connection works correctly
        assert device.reset_all_io().status
    assert not device.is_active()
    if uos_identities["loading"] == "EAGER":
        # LAZY loading can use connection when not active as it manages it internally.
        with pytest.raises(UOSCommunicationError):
            device.reset_all_io()


@pytest.mark.parametrize("function", UOSFunctions.enumerate_functions())
def test_device_function(uos_device, function: UOSFunction):
    """Checks the UOS functions respond correctly."""
    for volatility in Persistence:
        if volatility not in uos_device.device.functions_enabled[function.name]:
            continue  # Ignore unsupported volatilities for device
        pins = uos_device.device.get_compatible_pins(function)
        if pins is None or len(pins) == 0:
            pins = [0]  # insert a dummy pin for non-pinned functions.
        for pin in pins:
            api_function = getattr(uos_device, function.name)
            call_arguments = {}
            if "pin" in signature(api_function).parameters.keys():
                call_arguments["pin"] = pin
            if "level" in signature(api_function).parameters.keys():
                call_arguments["level"] = 0
            if "volatility" in signature(api_function).parameters.keys():
                call_arguments["volatility"] = volatility
            result = api_function(**call_arguments)
            assert result.status
            assert len(result.rx_packets) == len(function.rx_packets_expected)
            for i, rx_packet in enumerate(result.rx_packets):
                assert (  # packet length validation
                    len(rx_packet) == 6 + function.rx_packets_expected[i]
                )
                assert (  # payload length validation
                    rx_packet[3] == function.rx_packets_expected[i]
                )


def test_invalid_pin(uos_device):
    """Checks a pin based instruction with an invalid pin throws error."""
    with pytest.raises(UOSUnsupportedError):
        uos_device.set_gpio_output(-1, 1, volatility=Persistence.NONE)


def test_close_error(uos_errored_device):
    """Checks error is thrown correctly on close."""
    with pytest.raises(UOSCommunicationError):
        uos_errored_device.close()


def test_enumerate_devices():
    """Checks at least the stub is returned by the enumeration func."""
    devices = enumerate_system_devices()
    assert isinstance(devices, list)
    assert len(devices) > 0
    assert all(isinstance(device, UOSInterface) for device in devices)
    devices = enumerate_system_devices(Interface.STUB)
    assert len(devices) == 1
    assert isinstance(devices[0], Stub)
