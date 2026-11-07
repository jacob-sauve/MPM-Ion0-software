# Green Bear design

USB telemetry for the HAB launch (BBG → RB → radio → ground). Decisions
from the grill session of 2026-11-07. Companion byte-spec:
[`greenbear-protocol.md`](greenbear-protocol.md).

## Intent

By launch day: the BBG sends telemetry over USB to the RB; the RB radiates
it; the ground station (HackRF + Yagis) receives for at least a few minutes
post-launch. Every packet the BBG sends is also logged to the SD card so
the flight record is continuous regardless of link loss.

## Goals / non-goals / anti-goals

**Goals**

- One-way USB protocol, beginner-legible code, ≤ 4 big steps.
- Modular and stub-testable (`FakeLink`, fixture CSV).
- Human-in-the-loop for packet construction; user writes COBS and packet
  bodies against full test suites.
- Preserve a path back to OLAF/CAN without keeping OLAF on the launch path.

**Non-goals**

- ACK / retry / request-response.
- GPS (antenna insufficient).
- Extrusion / inverter flight sequence (`flightmain.c` is obsolete).
- Porting C sensor drivers to Python for launch day.

**Anti-goals**

- Another 20-task decomposition.
- Surprising bloat / competing OLAF + USB clients.
- Protocol that the RB must understand beyond COBS + CRC + length.

## Architecture

```
logsmain (C) ──CSV──► Green Bear (Python)
                          │
                          ├─ build_content (user)
                          ├─ packet.build  (user)
                          ├─ usb_link.send (COBS + 0x00)
                          └─ send log on SD
                                │
                                ▼  /dev/ttyACM0
                     RB usb-bridge (Zephyr)
                          │ COBS-decode, CRC check
                          ▼ radio_tx (tx-burst setup)
                     HackRF + fsk_decode.py --expect greenbear
```

`logsmain` stays the sole sensor reader. Green Bear tails its CSV. OLAF
files stay in the tree; `oresat-olaf` is an optional extra. Launch entry
point is `uv run greenbear`.

## Layout (BBG)

COBS / packet codecs live in the shared HITL package
[`cdh-cdc-cobs-packets`](https://github.com/Orbital-CubeSat-McGill/cdh-cdc-cobs-packets)
(`cdh_packets`). Ion re-exports them and keeps the test suites + stub
vectors here (`Ion/tests/`, `stub_frames.py`).

```
Ion/src/ion/greenbear/
  config.py      USB/flight tunables; packet constants from cdh_packets
  cobs.py        re-export cdh_packets.cobs     [USER fills shared pkg]
  packet.py      re-export cdh_packets.packet   [USER fills shared pkg]
  stub_frames.py premade logical/wire pairs (failsafe)
  usb_link.py    UsbLink + FakeLink
  telemetry.py   Sample, CSV tail, build_content [USER slot]
  main.py        flight loop
```

## RB firmware

`software/apps/usb-bridge/` in `satcomms-ocs-rf-1.0`. Radio path is
byte-for-byte the working `tx-burst` setup (RF24 asleep, RF09, preset 0,
TX_POWER 15, TRXOFF after each send). USB CDC ACM; console stays on
SERCOM5. Bad frames dropped and counted, never transmitted.

## Ground station

`fsk_decode.py --expect greenbear` parses and prints the header live,
using a copy of `packet.py` in `ground-station/` marked "keep in sync".

## Implementation steps

1. **Foundations** — branches, archive usbeast, package skeleton, tests, docs.
2. **Green Bear on BBG** — usb_link, telemetry reader, main, systemd.
3. **RB bridge + ground parser** — usb-bridge firmware, decoder.
4. **Integration + pre-flight** — bench chain, checklist.

User HITL slots: fill `cdh_packets` COBS/packet bodies (Ion tests are the
spec); write `build_content` after step 2; review protocol doc before
step 3; approve each step's diff before the next.

## RGB USB migration (future — stub)

**Out of scope for launch.** The RB today is transmit-only: USB in, radio
out. A full RGB migration would open at least:

- RB → BBG receive path and a command set (what can the ground ask the
  BBG to do via the radio?).
- Radio configuration over USB (channel, power, preset) instead of
  compile-time constants.
- Replacement for the CAN heartbeat that previously proved the cable.
- Whether the RB should buffer / retransmit on its own.
- What the Green Board CAN-FD connector becomes once USB owns the link.

**Note to self:** replace this stub with real specs after the flight,
informed by what the bench and the flight send-log / ground decode show.
Update `docs/greenbear-design.md` and open a dedicated conversation on
`~/Documents/GitHub/satcomms-ocs-rf-1.0`.

## Branches

- This repo: `greenbear` from `main`. `usbeast` holds an archive commit.
- RF repo: `greenbear` from `claudette`. `usbeast` holds an archive commit.
