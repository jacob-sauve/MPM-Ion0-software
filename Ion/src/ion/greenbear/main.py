"""Green Bear flight loop entry point. Body filled in Step 2.

Run with::

    uv run greenbear
"""

from __future__ import annotations

import logging

logger = logging.getLogger("greenbear")


def main() -> None:
    """Configure logging and run the send loop forever.

    Loop (once Step 2 is done)::

        every PACKET_INTERVAL_S:
            rows = new CSV samples since last send
            content = build_content(rows)          # yours
            frame = packet.build(seq, now, content)  # yours
            ok = link.send(frame)
            append send-log line (time, seq, len, sent|link down, hex)
            seq = (seq + 1) & 0xFFFF
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Green Bear skeleton — Step 2 fills the loop")
    raise NotImplementedError("Step 2: implement the flight loop")


if __name__ == "__main__":
    main()
