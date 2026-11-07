"""Central tunables for Green Bear. Change numbers here, nowhere else."""

from __future__ import annotations

# --- identity / packet ---
CALLSIGN: bytes = b"VE3 JKB"  # exactly 7 ASCII bytes; also acts as sync word
VERSION: int = 1
HEADER_SIZE: int = 16  # callsign(7) + version(1) + seq(2) + time(4) + length(2)
CRC_SIZE: int = 2
MAX_CONTENT: int = 1024  # bytes of packed content; absolute air ceiling is 2025

# CRC-16/CCITT-FALSE parameters (see docs/greenbear-protocol.md)
CRC_POLY: int = 0x1021
CRC_INIT: int = 0xFFFF
CRC_CHECK: int = 0x29B1  # binascii.crc_hqx(b"123456789", 0xFFFF)

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
