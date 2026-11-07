"""Premade logical/wire frame pairs for dry-run and tests.

These bytes were generated offline against the protocol spec. They do
**not** import ``cobs`` or ``packet`` — so Step 2 / tests can run before
those HITL slots are filled.

When you implement ``packet.build`` / ``cobs.encode``, your output for
the same inputs must match these hex strings (see test_stub_frames.py
once you flip ``REQUIRE_MATCH = True``, or compare by hand).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StubFrame:
    name: str
    # Inputs that produced the frame (documentation only).
    seq: int
    time: int
    content: bytes
    logical: bytes  # header | content | crc16
    wire: bytes  # COBS(logical) + 0x00


def _h(hexstr: str) -> bytes:
    return bytes.fromhex(hexstr.replace(" ", ""))


# Generated with CRC-16/CCITT-FALSE and plain COBS per docs/greenbear-protocol.md
FRAMES: dict[str, StubFrame] = {
    "empty_seq1234": StubFrame(
        name="empty_seq1234",
        seq=0x1234,
        time=0,
        content=b"",
        logical=_h("564533204a4b420134120000000000001ee6"),
        wire=_h("0b564533204a4b420134120101010101031ee600"),
    ),
    "hello": StubFrame(
        name="hello",
        seq=1,
        time=1_700_000_000,
        content=b"hello",
        logical=_h("564533204a4b4201010000f15365050068656c6c6f8c0f"),
        wire=_h("0a564533204a4b4201010105f15365050868656c6c6f8c0f00"),
    ),
    "two_bytes": StubFrame(
        name="two_bytes",
        seq=7,
        time=42,
        content=b"\xaa\xbb",
        logical=_h("564533204a4b420107002a0000000200aabb5f23"),
        wire=_h("0a564533204a4b420107022a0101020205aabb5f2300"),
    ),
}

# Default cycle used by ``uv run greenbear --stub``
STUB_CYCLE: tuple[str, ...] = ("empty_seq1234", "hello", "two_bytes")


def wire_for_logical(logical: bytes) -> bytes | None:
    """Return premade wire bytes for a known logical frame, or None."""
    for stub in FRAMES.values():
        if stub.logical == logical:
            return stub.wire
    return None


class StubLink:
    """Link that only sends premade frames from ``FRAMES``.

    ``send(logical)`` succeeds if ``logical`` matches a stub; otherwise
    returns False. Never calls ``cobs`` or ``packet``.
    """

    def __init__(self) -> None:
        self.frames: list[bytes] = []
        self.wire: list[bytes] = []
        self.names: list[str] = []
        self.fail_next: bool = False

    def send(self, frame: bytes) -> bool:
        if self.fail_next:
            self.fail_next = False
            return False
        for stub in FRAMES.values():
            if stub.logical == frame:
                self.frames.append(frame)
                self.wire.append(stub.wire)
                self.names.append(stub.name)
                return True
        return False

    def send_named(self, name: str) -> bool:
        stub = FRAMES[name]
        return self.send(stub.logical)

    def read_pending(self) -> bytes:
        return b""

    def close(self) -> None:
        return None
