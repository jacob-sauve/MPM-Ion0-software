"""Plain COBS encode/decode for the USB hop only.

The radio never sees COBS: the RB strips it before radio_tx.

YOU write the bodies. The tests in Ion/tests/test_cobs.py are the spec.
Signatures and types are fixed — do not change them.
"""

from __future__ import annotations


def encode(data: bytes) -> bytes:
    """COBS-encode ``data``.

    Parameters
    ----------
    data:
        Raw bytes of any length, including empty and zero-heavy.

    Returns
    -------
    bytes
        Encoded body with **no** ``0x00`` bytes inside, and **no** trailing
        delimiter. The caller (``usb_link``) appends a single ``0x00`` after
        this return value to mark the end of the frame.

    Notes
    -----
    - Empty input encodes to ``b"\\x01"``.
    - A run of 254 non-zero bytes is followed by a code byte of ``0xFF``,
      then the next code (or end).
    - See docs/greenbear-protocol.md for published vectors.
    """
    raise NotImplementedError("fill in: plain COBS encode; see test_cobs.py")


def decode(data: bytes) -> bytes:
    """COBS-decode ``data``.

    Parameters
    ----------
    data:
        Encoded body **without** the trailing ``0x00`` delimiter (already
        stripped by the frame splitter). Must contain no ``0x00`` bytes.

    Returns
    -------
    bytes
        The original payload.

    Raises
    ------
    ValueError
        If the encoding is malformed (truncated code, embedded zero, etc.).
    """
    raise NotImplementedError("fill in: plain COBS decode; see test_cobs.py")
