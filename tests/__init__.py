"""Pytest package for testing uoshardware."""
from dataclasses import dataclass


@dataclass
class Packet:
    """Dataclass for storing test packet definitions."""

    address_to: int
    address_from: int
    payload: list
    checksum: int
    binary: bytes
