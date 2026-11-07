"""Stub frame driver tests — no dependency on cobs/packet bodies."""

from __future__ import annotations

import unittest

from ion.greenbear.stub_frames import FRAMES, STUB_CYCLE, StubLink, wire_for_logical
from ion.greenbear.usb_link import FakeLink


class TestStubFrames(unittest.TestCase):
    def test_known_names(self) -> None:
        self.assertIn("empty_seq1234", FRAMES)
        self.assertIn("hello", FRAMES)
        self.assertIn("two_bytes", FRAMES)

    def test_wire_ends_with_delimiter(self) -> None:
        for stub in FRAMES.values():
            with self.subTest(name=stub.name):
                self.assertTrue(stub.wire.endswith(b"\x00"))
                self.assertNotIn(0, stub.wire[:-1])

    def test_callsign_prefix(self) -> None:
        for stub in FRAMES.values():
            self.assertEqual(stub.logical[:7], b"VE3 JKB")

    def test_wire_for_logical(self) -> None:
        stub = FRAMES["hello"]
        self.assertEqual(wire_for_logical(stub.logical), stub.wire)
        self.assertIsNone(wire_for_logical(b"nope"))

    def test_stub_link_send(self) -> None:
        link = StubLink()
        self.assertTrue(link.send_named("hello"))
        self.assertEqual(link.names, ["hello"])
        self.assertEqual(link.wire[0], FRAMES["hello"].wire)
        self.assertFalse(link.send(b"unknown"))

    def test_stub_link_fail_next(self) -> None:
        link = StubLink()
        link.fail_next = True
        self.assertFalse(link.send_named("hello"))
        self.assertTrue(link.send_named("hello"))

    def test_fake_link_uses_stub_wire_without_cobs(self) -> None:
        """FakeLink falls back to stub wire when cobs.encode is a skeleton."""
        link = FakeLink()
        stub = FRAMES["empty_seq1234"]
        self.assertTrue(link.send(stub.logical))
        self.assertEqual(link.frames[0], stub.logical)
        self.assertEqual(link.wire[0], stub.wire)

    def test_stub_cycle_nonempty(self) -> None:
        self.assertTrue(STUB_CYCLE)
        for name in STUB_CYCLE:
            self.assertIn(name, FRAMES)


if __name__ == "__main__":
    unittest.main()
