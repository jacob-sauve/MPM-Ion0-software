"""USB CDC ACM transport.

``send`` never raises to the caller: a down link returns False and the
flight loop keeps logging.
"""

from __future__ import annotations

import logging
import time
from typing import Protocol

from ion.greenbear import config, cobs
from ion.greenbear.stub_frames import wire_for_logical

logger = logging.getLogger("greenbear.usb")


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


def _to_wire(frame: bytes) -> bytes:
    """Logical frame → COBS body + trailing delimiter.

    Prefers ``cobs.encode``. If that HITL slot is still a skeleton,
    falls back to a premade stub wire frame when one exists.
    """
    try:
        return cobs.encode(frame) + b"\x00"
    except NotImplementedError:
        wire = wire_for_logical(frame)
        if wire is not None:
            return wire
        raise


class FakeLink:
    """In-memory link for tests. Records every successful send."""

    def __init__(self) -> None:
        self.frames: list[bytes] = []
        self.wire: list[bytes] = []
        self.fail_next: bool = False

    def send(self, frame: bytes) -> bool:
        if self.fail_next:
            self.fail_next = False
            return False
        try:
            wire = _to_wire(frame)
        except Exception:
            logger.exception("FakeLink encode failed")
            return False
        self.frames.append(frame)
        self.wire.append(wire)
        return True

    def close(self) -> None:
        return None


class UsbLink:
    """Real ``/dev/ttyACM*`` transport via pyserial."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path or config.USB_DEVICE
        self._ser = None
        self._open()

    def _open(self) -> bool:
        try:
            import serial  # pyserial
        except ImportError:
            logger.error("pyserial not installed")
            self._ser = None
            return False
        try:
            self._ser = serial.Serial(
                port=self.path,
                baudrate=config.USB_BAUD,
                timeout=0,
                write_timeout=config.USB_WRITE_TIMEOUT_S,
            )
            logger.info("opened %s", self.path)
            return True
        except Exception as exc:
            logger.warning("could not open %s: %s", self.path, exc)
            self._ser = None
            return False

    def _ensure_open(self) -> bool:
        if self._ser is not None and getattr(self._ser, "is_open", False):
            return True
        return self._open()

    def send(self, frame: bytes) -> bool:
        try:
            wire = _to_wire(frame)
        except Exception:
            logger.exception("encode failed")
            return False
        if not self._ensure_open():
            return False
        try:
            written = self._ser.write(wire)
            if written != len(wire):
                logger.warning("short write: %s/%s", written, len(wire))
                self.close()
                return False
            return True
        except Exception as exc:
            logger.warning("write failed: %s", exc)
            self.close()
            return False

    def close(self) -> None:
        if self._ser is None:
            return
        try:
            self._ser.close()
        except Exception:
            pass
        self._ser = None

    def reopen_loop(self, stop_after_s: float | None = None) -> bool:
        """Keep trying to open until success or optional timeout."""
        deadline = None if stop_after_s is None else time.monotonic() + stop_after_s
        while True:
            if self._ensure_open():
                return True
            if deadline is not None and time.monotonic() >= deadline:
                return False
            time.sleep(config.USB_OPEN_RETRY_S)
