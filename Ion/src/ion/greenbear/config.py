"""Central tunables for Green Bear.

Packet/wire constants come from ``cdh_packets`` so BBG stays in sync with
the shared HITL package. USB and flight-loop paths stay local to Ion.
"""

from __future__ import annotations

from cdh_packets.constants import (
    CALLSIGN,
    CRC_CHECK,
    CRC_INIT,
    CRC_POLY,
    CRC_SIZE,
    HEADER_SIZE,
    MAX_CONTENT,
    VERSION,
)

# --- USB ---
USB_DEVICE: str = "/dev/ttyACM0"
USB_BAUD: int = 115200  # CDC ACM ignores baud; kept for pyserial open()
USB_OPEN_RETRY_S: float = 5.0  # how long to wait between open attempts
USB_WRITE_TIMEOUT_S: float = 1.0

# --- flight loop ---
PACKET_INTERVAL_S: float = 20.0
CSV_DIR: str = "/home/cubesat/logs"
SEND_LOG_DIR: str = "/home/cubesat/logs"
SEND_LOG_PREFIX: str = "greenbear_"  # produces greenbear_001.log, etc.
CSV_PREFIX: str = "ion"  # logsmain produces ion001.csv, etc.
CSV_GLOB: str = "ion*.csv"

__all__ = [
    "CALLSIGN",
    "CRC_CHECK",
    "CRC_INIT",
    "CRC_POLY",
    "CRC_SIZE",
    "CSV_DIR",
    "CSV_GLOB",
    "CSV_PREFIX",
    "HEADER_SIZE",
    "MAX_CONTENT",
    "PACKET_INTERVAL_S",
    "SEND_LOG_DIR",
    "SEND_LOG_PREFIX",
    "USB_BAUD",
    "USB_DEVICE",
    "USB_OPEN_RETRY_S",
    "USB_WRITE_TIMEOUT_S",
    "VERSION",
]
