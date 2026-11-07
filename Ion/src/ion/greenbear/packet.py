"""Green Bear logical packet: 16-byte header + content + CRC-16.

CRC is computed *before* COBS and travels all the way to the ground.
Endianness is little-endian throughout.

YOU write ``build`` and ``parse``. The tests in Ion/tests/test_packet.py
are the spec. Do not change the dataclasses or signatures.
"""

from __future__ import annotations

from dataclasses import dataclass

from ion.greenbear import config


@dataclass(frozen=True)
class Packet:
    """Decoded logical packet (header fields + content, CRC already verified)."""

    callsign: bytes  # exactly config.CALLSIGN
    version: int
    seq: int  # 0..65535
    time: int  # Unix seconds (u32)
    content: bytes  # 0..MAX_CONTENT bytes


def crc16(data: bytes) -> int:
    """CRC-16/CCITT-FALSE over ``data``.

    Returns the 16-bit value (0..65535). Use ``binascii.crc_hqx(data, 0xFFFF)``.
    Provided so tests and callers share one place; you may leave this as-is
    or reimplement equivalently.
    """
    import binascii

    return binascii.crc_hqx(data, config.CRC_INIT) & 0xFFFF


def build(seq: int, time: int, content: bytes) -> bytes:
    """Serialize a packet to ``header | content | crc16`` (no COBS).

    Parameters
    ----------
    seq:
        Packet sequence number, wrapped to ``u16`` (0..65535).
    time:
        Unix seconds at send time, as ``u32``.
    content:
        Opaque bytes you packed. Must be ``len(content) <= config.MAX_CONTENT``.

    Returns
    -------
    bytes
        Exactly ``HEADER_SIZE + len(content) + CRC_SIZE`` bytes:
        callsign (7 ASCII) | version (u8=1) | seq (u16 LE) | time (u32 LE)
        | length (u16 LE) | content | crc16 (u16 LE over everything before it).

    Raises
    ------
    ValueError
        If ``len(content) > config.MAX_CONTENT``, or seq/time out of range
        for their field widths.
    """
    raise NotImplementedError("fill in: packet.build; see test_packet.py")


def parse(frame: bytes) -> Packet:
    """Parse and CRC-check a logical frame (no COBS).

    Parameters
    ----------
    frame:
        ``header | content | crc16`` bytes as produced by ``build``.

    Returns
    -------
    Packet
        Validated packet. ``content`` is the opaque payload only.

    Raises
    ------
    ValueError
        On truncation, wrong callsign, wrong version, length mismatch,
        content longer than ``MAX_CONTENT``, or CRC mismatch.
    """
    raise NotImplementedError("fill in: packet.parse; see test_packet.py")
