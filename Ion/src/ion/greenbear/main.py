"""Green Bear flight loop.

Run::

    uv run greenbear              # real CSV + packet + USB (needs your codecs)
    uv run greenbear --stub       # cycle premade frames on FakeLink / UsbLink
    uv run greenbear --stub --once
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from ion.greenbear import config, packet, telemetry
from ion.greenbear.stub_frames import FRAMES, STUB_CYCLE, StubLink
from ion.greenbear.usb_link import FakeLink, Link, UsbLink

logger = logging.getLogger("greenbear")


def _next_send_log_path(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        path = directory / f"{config.SEND_LOG_PREFIX}{n:03d}.log"
        if not path.exists():
            return path
        n += 1


def _append_send_log(
    path: Path,
    *,
    wall: float,
    seq: int,
    length: int,
    status: str,
    frame: bytes,
) -> None:
    line = f"{wall:.0f},{seq},{length},{status},{frame.hex()}\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()


def _build_frame(seq: int, now: int, rows: list[telemetry.Sample]) -> bytes | None:
    """Try user codecs; return None if HITL slots are still skeletons."""
    try:
        content = telemetry.build_content(rows)
    except NotImplementedError:
        logger.error("telemetry.build_content not implemented — use --stub")
        return None
    try:
        return packet.build(seq, now, content)
    except NotImplementedError:
        logger.error("packet.build not implemented — use --stub")
        return None


def _log_rb_console(link: Link) -> None:
    """Log any RB printk lines that came back on the port (``rb: ...``)."""
    if not config.RB_CONSOLE_LOG:
        return
    pending = link.read_pending()
    if not pending:
        return
    for line in pending.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            logger.info("rb: %s", line)


def run_loop(
    link: Link,
    *,
    csv_dir: Path,
    send_log: Path,
    interval_s: float,
    stub: bool,
    once: bool,
) -> None:
    seq = 0
    offset = 0
    csv_path: Path | None = None
    stub_i = 0

    logger.info("send log → %s", send_log)
    if stub:
        logger.info("stub mode: cycling %s", list(STUB_CYCLE))

    while True:
        _log_rb_console(link)
        wall = time.time()
        now = int(wall)

        if stub:
            name = STUB_CYCLE[stub_i % len(STUB_CYCLE)]
            stub_i += 1
            frame = FRAMES[name].logical
            content_len = len(FRAMES[name].content)
        else:
            csv_path = telemetry.latest_csv(csv_dir) or csv_path
            rows: list[telemetry.Sample] = []
            if csv_path is not None:
                rows, offset = telemetry.read_new_rows(csv_path, offset)
            frame = _build_frame(seq, now, rows)
            if frame is None:
                time.sleep(interval_s)
                if once:
                    return
                continue
            content_len = len(frame) - config.HEADER_SIZE - config.CRC_SIZE

        ok = link.send(frame)
        status = "sent" if ok else "link down"
        _append_send_log(
            send_log,
            wall=wall,
            seq=seq if not stub else FRAMES[STUB_CYCLE[(stub_i - 1) % len(STUB_CYCLE)]].seq,
            length=content_len,
            status=status,
            frame=frame,
        )
        logger.info(
            "seq=%s len=%s %s",
            seq if not stub else FRAMES[STUB_CYCLE[(stub_i - 1) % len(STUB_CYCLE)]].seq,
            content_len,
            status,
        )
        seq = (seq + 1) & 0xFFFF

        if once:
            # Give the RB a moment to answer so its "sent"/"drop" line is logged.
            time.sleep(min(0.5, interval_s))
            _log_rb_console(link)
            return
        time.sleep(interval_s)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Green Bear USB telemetry")
    parser.add_argument(
        "--stub",
        action="store_true",
        help="cycle premade stub frames (no cobs/packet/build_content needed)",
    )
    parser.add_argument(
        "--fake",
        action="store_true",
        help="use FakeLink instead of /dev/ttyACM* (implies in-memory only)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="send one packet and exit",
    )
    parser.add_argument(
        "--csv-dir",
        type=Path,
        default=Path(config.CSV_DIR),
    )
    parser.add_argument(
        "--send-log-dir",
        type=Path,
        default=Path(config.SEND_LOG_DIR),
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=config.PACKET_INTERVAL_S,
    )
    parser.add_argument(
        "--device",
        default=config.USB_DEVICE,
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    send_log = _next_send_log_path(args.send_log_dir)

    if args.stub and args.fake:
        link: Link = StubLink()
    elif args.fake:
        link = FakeLink()
    elif args.stub:
        # Real USB, but premade logical frames (wire via stub fallback in _to_wire)
        link = UsbLink(args.device)
    else:
        link = UsbLink(args.device)

    try:
        run_loop(
            link,
            csv_dir=args.csv_dir,
            send_log=send_log,
            interval_s=args.interval,
            stub=args.stub,
            once=args.once,
        )
    finally:
        link.close()


if __name__ == "__main__":
    main()
