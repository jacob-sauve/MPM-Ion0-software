"""COBS encode/decode — re-exported from ``cdh_packets`` (HITL home).

Fill bodies in the ``cdh-cdc-cobs-packets`` repo. Ion tests remain the spec.
"""

from __future__ import annotations

from cdh_packets.cobs import decode, encode

__all__ = ["decode", "encode"]
