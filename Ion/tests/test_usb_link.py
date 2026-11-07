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


if __name__ == "__main__":
    unittest.main()
