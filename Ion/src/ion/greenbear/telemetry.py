"""CSV tail + content packing for Green Bear.

``logsmain`` (C) owns the sensors and writes ``ionNNN.csv``.
Green Bear only reads new lines and packs them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_CSV_NAME = re.compile(r"^ion(\d+)\.csv$")
# Data row: HH:MM:SS, then 8 floats (current has a space after the comma in logs.c)
_DATA_ROW = re.compile(
    r"^(\d{2}:\d{2}:\d{2}),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+),"
    r"\s*([-+eE0-9.]+)\s*$"
)


@dataclass(frozen=True)
class Sample:
    """One ``logsmain`` CSV data row."""

    time_hms: str
    pressure: float
    ms_temp: float
    humidity: float
    hdc_temp: float
    probe1: float
    probe2: float
    probe3: float
    current: float


def latest_csv(csv_dir: Path) -> Path | None:
    """Return the highest-numbered ``ionNNN.csv`` in ``csv_dir``, or None."""
    best: tuple[int, Path] | None = None
    if not csv_dir.is_dir():
        return None
    for path in csv_dir.iterdir():
        match = _CSV_NAME.match(path.name)
        if not match:
            continue
        num = int(match.group(1))
        if best is None or num > best[0]:
            best = (num, path)
    return None if best is None else best[1]


def _parse_row(line: str) -> Sample | None:
    line = line.strip()
    if not line or line.startswith("ION ") or line.startswith("time,"):
        return None
    if line.startswith("["):  # logMessage lines: [HH:MM:SS] text
        return None
    match = _DATA_ROW.match(line)
    if not match:
        return None
    g = match.groups()
    return Sample(
        time_hms=g[0],
        pressure=float(g[1]),
        ms_temp=float(g[2]),
        humidity=float(g[3]),
        hdc_temp=float(g[4]),
        probe1=float(g[5]),
        probe2=float(g[6]),
        probe3=float(g[7]),
        current=float(g[8]),
    )


def read_new_rows(csv_path: Path, since_offset: int) -> tuple[list[Sample], int]:
    """Read CSV rows starting at byte ``since_offset``.

    Returns ``(samples, new_offset)``. Incomplete trailing line is left
    unread (offset stays at the start of that line).
    """
    if not csv_path.is_file():
        return [], since_offset
    size = csv_path.stat().st_size
    if since_offset > size:
        since_offset = 0
    with csv_path.open("rb") as fh:
        fh.seek(since_offset)
        raw = fh.read()
    if not raw:
        return [], since_offset

    # Only consume complete lines (ending in \\n).
    last_nl = raw.rfind(b"\n")
    if last_nl < 0:
        return [], since_offset
    complete = raw[: last_nl + 1]
    new_offset = since_offset + len(complete)

    samples: list[Sample] = []
    for line in complete.decode("utf-8", errors="replace").splitlines():
        sample = _parse_row(line)
        if sample is not None:
            samples.append(sample)
    return samples, new_offset


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
