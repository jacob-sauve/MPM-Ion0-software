"""CSV tail tests — independent of build_content / packet / cobs."""

from __future__ import annotations

import unittest
from pathlib import Path

from ion.greenbear import telemetry

FIXTURE = Path(__file__).parent / "fixtures" / "ion001.csv"


class TestLatestCsv(unittest.TestCase):
    def test_picks_highest_number(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "ion001.csv").write_text("x\n")
            (d / "ion003.csv").write_text("x\n")
            (d / "ion002.csv").write_text("x\n")
            (d / "notes.txt").write_text("x\n")
            self.assertEqual(telemetry.latest_csv(d), d / "ion003.csv")

    def test_empty_dir(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(telemetry.latest_csv(Path(tmp)))


class TestReadNewRows(unittest.TestCase):
    def test_parses_fixture(self) -> None:
        samples, offset = telemetry.read_new_rows(FIXTURE, 0)
        self.assertEqual(len(samples), 4)
        self.assertEqual(samples[0].time_hms, "12:00:00")
        self.assertAlmostEqual(samples[0].pressure, 1013.25)
        self.assertAlmostEqual(samples[0].current, 0.12)
        self.assertEqual(samples[2].time_hms, "12:00:02")
        self.assertEqual(samples[3].time_hms, "12:00:04")  # skipped message line
        self.assertEqual(offset, FIXTURE.stat().st_size)

    def test_offset_resume(self) -> None:
        samples1, off1 = telemetry.read_new_rows(FIXTURE, 0)
        samples2, off2 = telemetry.read_new_rows(FIXTURE, off1)
        self.assertEqual(len(samples1), 4)
        self.assertEqual(samples2, [])
        self.assertEqual(off2, off1)

    def test_build_content_still_skeleton(self) -> None:
        with self.assertRaises(NotImplementedError):
            telemetry.build_content([])


if __name__ == "__main__":
    unittest.main()
