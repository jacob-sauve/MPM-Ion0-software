#!/usr/bin/env python3
"""Decode a Green Bear logical-frame hex string from the send log.

Usage::

    PYTHONPATH=src uv run python tools/decode_frame.py 56453320...

Uses ``packet.parse`` when implemented; otherwise prints a raw header
peek and notes that parse is still a skeleton.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

# Allow running from Ion/ without install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ion.greenbear import config, packet


def peek(frame: bytes) -> None:
    if len(frame) < config.HEADER_SIZE + config.CRC_SIZE:
        print(f"too short: {len(frame)} bytes")
        return
    print(f"callsign: {frame[0:7]!r}")
    print(f"version:  {frame[7]}")
    print(f"seq:      {struct.unpack_from('<H', frame, 8)[0]}")
    print(f"time:     {struct.unpack_from('<I', frame, 10)[0]}")
    print(f"length:   {struct.unpack_from('<H', frame, 14)[0]}")
    print(f"crc16:    0x{struct.unpack_from('<H', frame, len(frame) - 2)[0]:04x}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("hex", help="logical frame as hex (no 0x, no spaces ok)")
    args = parser.parse_args()
    frame = bytes.fromhex(args.hex)
    peek(frame)
    try:
        parsed = packet.parse(frame)
    except NotImplementedError:
        print("(packet.parse not implemented yet)")
        return
    except ValueError as exc:
        print(f"parse error: {exc}")
        return
    print(f"ok: seq={parsed.seq} time={parsed.time} content={parsed.content!r}")


if __name__ == "__main__":
    main()
