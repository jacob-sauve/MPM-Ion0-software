"""Logical packet build/parse — re-exported from ``cdh_packets`` (HITL home).

Fill bodies in the ``cdh-cdc-cobs-packets`` repo. Ion tests remain the spec.
"""

from __future__ import annotations

from cdh_packets.packet import Packet, build, crc16, parse

__all__ = ["Packet", "build", "crc16", "parse"]
