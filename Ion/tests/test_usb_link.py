"""UsbLink / FakeLink unit tests (no hardware)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from ion.greenbear.stub_frames import FRAMES
from ion.greenbear.usb_link import FakeLink, UsbLink


class TestFakeLink(unittest.TestCase):
    def test_records_frame_and_wire(self) -> None:
        link = FakeLink()
        stub = FRAMES["two_bytes"]
        self.assertTrue(link.send(stub.logical))
        self.assertEqual(link.frames, [stub.logical])
        self.assertEqual(link.wire, [stub.wire])

    def test_fail_next(self) -> None:
        link = FakeLink()
        link.fail_next = True
        self.assertFalse(link.send(FRAMES["hello"].logical))
        self.assertEqual(link.frames, [])
        self.assertTrue(link.send(FRAMES["hello"].logical))


class TestUsbLinkNoDevice(unittest.TestCase):
    def test_send_returns_false_when_port_missing(self) -> None:
        link = UsbLink(path="/dev/ttyACM_does_not_exist_greenbear")
        stub = FRAMES["hello"]
        self.assertFalse(link.send(stub.logical))
        link.close()

    def test_send_writes_wire_bytes(self) -> None:
        stub = FRAMES["hello"]
        fake_ser = MagicMock()
        fake_ser.is_open = True
        fake_ser.write.return_value = len(stub.wire)

        with patch("serial.Serial", return_value=fake_ser):
            link = UsbLink(path="/dev/null")
            self.assertTrue(link.send(stub.logical))
            fake_ser.write.assert_called_once_with(stub.wire)
            link.close()

    def test_read_pending_returns_buffered_bytes_then_empty_when_closed(self) -> None:
        fake_ser = MagicMock()
        fake_ser.is_open = True
        fake_ser.in_waiting = 11
        fake_ser.read.return_value = b"sent seq=1\n"

        with patch("serial.Serial", return_value=fake_ser):
            link = UsbLink(path="/dev/null")
            self.assertEqual(link.read_pending(), b"sent seq=1\n")
            fake_ser.read.assert_called_once_with(11)

            fake_ser.in_waiting = 0
            self.assertEqual(link.read_pending(), b"")

            link.close()
            self.assertEqual(link.read_pending(), b"")

    def test_fake_link_read_pending_is_empty(self) -> None:
        self.assertEqual(FakeLink().read_pending(), b"")


if __name__ == "__main__":
    unittest.main()
