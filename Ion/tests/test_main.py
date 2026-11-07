"""Flight-loop tests using --stub + FakeLink/StubLink (no user codecs)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ion.greenbear.main import main, run_loop
from ion.greenbear.stub_frames import FRAMES, STUB_CYCLE, StubLink


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


if __name__ == "__main__":
    unittest.main()
