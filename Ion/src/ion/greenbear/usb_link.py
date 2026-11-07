"""USB CDC ACM transport (Step 2 fills the bodies).

``send`` never raises to the caller: a down link returns False and the
flight loop keeps logging.
"""

from __future__ import annotations

from typing import Protocol


class Link(Protocol):
    """Anything Green Bear can send a logical frame through."""

    def send(self, frame: bytes) -> bool:
        """COBS-encode ``frame``, append ``0x00``, write to the wire.

        Returns True on success, False if the link is down / write failed.
        Must not raise.
        """
        ...

    def close(self) -> None:
        """Release the device. Must not raise."""
        ...


class FakeLink:
    """In-memory link for tests. Records every successful send."""

    def __init__(self) -> None:
        self.frames: list[bytes] = []  # logical frames (pre-COBS), as passed to send
        self.wire: list[bytes] = []  # COBS body + 0x00 as would hit the wire
        self.fail_next: bool = False

    def send(self, frame: bytes) -> bool:
        # Step 2 wires real COBS; until then this is a placeholder that
        # records the logical frame only so higher-level tests can run.
        if self.fail_next:
            self.fail_next = False
            return False
        self.frames.append(frame)
        return True

    def close(self) -> None:
        return None


class UsbLink:
    """Real ``/dev/ttyACM*`` transport. Implemented in Step 2."""

    def __init__(self, path: str | None = None) -> None:
        raise NotImplementedError("Step 2: open CDC ACM with pyserial")

    def send(self, frame: bytes) -> bool:
        raise NotImplementedError("Step 2: COBS-encode, append 0x00, write")

    def close(self) -> None:
        raise NotImplementedError("Step 2: close serial port")
