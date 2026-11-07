"""CSV tail + content packing for Green Bear.

``logsmain`` (C) owns the sensors and writes ``ionNNN.csv``.
Green Bear only reads new lines and packs them.

YOU write ``build_content``. Decide int16 vs float32 when you do.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Sample:
    """One ``logsmain`` CSV data row.

    CSV header (from logs.c)::

        time, pressure, ms5607 temp, hdc humidity, hdc temp,
        prob 1 temp, prob 2 temp, prob 3 temp, current
    """

    time_hms: str  # "HH:MM:SS" as written by logsmain
    pressure: float
    ms_temp: float
    humidity: float
    hdc_temp: float
    probe1: float
    probe2: float
    probe3: float
    current: float


def read_new_rows(csv_path: Path, since_offset: int) -> tuple[list[Sample], int]:
    """Read CSV rows starting at byte ``since_offset``.

    Returns ``(samples, new_offset)``. Skips the header line and any
    ``[HH:MM:SS] message`` log lines. Implemented in Step 2.
    """
    raise NotImplementedError("Step 2: tail logsmain CSV")


def latest_csv(csv_dir: Path) -> Path | None:
    """Return the highest-numbered ``ionNNN.csv`` in ``csv_dir``, or None."""
    raise NotImplementedError("Step 2: find newest ionNNN.csv")


def build_content(rows: list[Sample]) -> bytes:
    """Pack the given samples into packet content.

    Parameters
    ----------
    rows:
        Zero or more samples to put in this packet. May be empty.

    Returns
    -------
    bytes
        Opaque content, ``len(...) <= config.MAX_CONTENT``. The packet
        layer enforces the cap; keep yourself under it.

    Notes
    -----
    Number format (int16 vs float32, scaling, endianness inside content)
    is yours to decide. Document it in a comment above the function when
    you implement it so the ground decoder can match.
    """
    raise NotImplementedError("fill in: your content packing; see plan §C deferred")
