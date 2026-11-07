"""Flight-loop tests using --stub + FakeLink/StubLink (no user codecs)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ion.greenbear.main import main, run_loop
from ion.greenbear.stub_frames import FRAMES, STUB_CYCLE, StubLink
from ion.greenbear.usb_link import FakeLink


class TestStubLoop(unittest.TestCase):
    def test_once_writes_send_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            send_dir = Path(tmp)
            link = StubLink()
            run_loop(
                link,
                csv_dir=send_dir,
                send_log=send_dir / "greenbear_001.log",
                interval_s=0.01,
                stub=True,
                once=True,
            )
            log = (send_dir / "greenbear_001.log").read_text()
            self.assertIn("sent", log)
            self.assertIn(FRAMES[STUB_CYCLE[0]].logical.hex(), log)
            self.assertEqual(link.names, [STUB_CYCLE[0]])

    def test_cli_stub_fake_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            main(
                [
                    "--stub",
                    "--fake",
                    "--once",
                    "--send-log-dir",
                    tmp,
                    "--csv-dir",
                    tmp,
                ]
            )
            logs = list(Path(tmp).glob("greenbear_*.log"))
            self.assertEqual(len(logs), 1)
            self.assertIn("sent", logs[0].read_text())


class _ChattyLink(FakeLink):
    """FakeLink that hands back canned RB console bytes once."""

    def __init__(self) -> None:
        super().__init__()
        self.pending = b"setup PASS: ret=0\r\nsent seq=4660 len=0 n=18 ok=1\r\n"

    def read_pending(self) -> bytes:
        out, self.pending = self.pending, b""
        return out


class TestRbConsoleLogging(unittest.TestCase):
    def test_rb_lines_are_logged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = _ChattyLink()
            with self.assertLogs("greenbear", level="INFO") as cm:
                run_loop(
                    link,
                    csv_dir=Path(tmp),
                    send_log=Path(tmp) / "greenbear_001.log",
                    interval_s=0.01,
                    stub=True,
                    once=True,
                )
            rb_lines = [m for m in cm.output if "rb: " in m]
            self.assertEqual(len(rb_lines), 2)
            self.assertIn("rb: setup PASS: ret=0", rb_lines[0])
            self.assertIn("rb: sent seq=4660 len=0 n=18 ok=1", rb_lines[1])


if __name__ == "__main__":
    unittest.main()
