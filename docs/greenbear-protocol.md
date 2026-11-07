# Green Bear wire protocol

Byte-level specification shared by the BBG (`Ion/src/ion/greenbear/`), the
RB `usb-bridge` firmware, and the ground-station decoder. One definition,
three consumers.

## Logical frame (what the radio carries)

Fields are little-endian. CRC-16 is computed **before** COBS and travels to
the ground inside the PSDU.

| Offset | Size | Field     | Type  | Meaning                                      |
| -----: | ---: | --------- | ----- | -------------------------------------------- |
|      0 |    7 | callsign  | ASCII | `VE3 JKB` (sync word + legal ID)             |
|      7 |    1 | version   | u8    | `1`                                          |
|      8 |    2 | seq       | u16   | packet number, wraps at 65535                |
|     10 |    4 | time      | u32   | Unix seconds at send                         |
|     14 |    2 | length    | u16   | number of content bytes that follow          |
|     16 |  0..N| content   | bytes | opaque; N ≤ `MAX_CONTENT` (1024)             |
|   16+N |    2 | crc16     | u16   | CRC-16/CCITT-FALSE over bytes `[0 .. 16+N)`  |

Decoded frame size = `16 + N + 2`. Absolute air ceiling: N ≤ 2025
(2043 usable PSDU − 16 − 2). Launch constant: **N ≤ 1024**.

### CRC-16/CCITT-FALSE

- Polynomial `0x1021`
- Initial value `0xFFFF`
- No reflected input/output
- Final XOR `0x0000`
- Check: `b"123456789"` → `0x29B1`
- Python: `binascii.crc_hqx(data, 0xFFFF)`
- Zephyr: `crc16_itu_t(0xFFFF, data, len)`

### Fixed empty-content vector

`seq = 0x1234`, `time = 0`, `content = ""`:

```
56 45 33 20 4a 4b 42   # "VE3 JKB"
01                     # version
34 12                  # seq LE
00 00 00 00            # time LE
00 00                  # length 0
<crc16 LE over the 16 header bytes>
```

Compute the CRC with the parameters above; the Python `packet.crc16` helper
and the tests pin the value.

## USB framing (COBS)

USB CDC ACM is a byte stream with no inherent frame boundaries. COBS is
used **only on the USB hop**:

1. BBG builds the logical frame (`header | content | crc16`).
2. BBG COBS-encodes it (plain COBS; body contains no `0x00`).
3. BBG appends a single trailing `0x00` delimiter and writes the bytes.
4. RB splits on `0x00`, COBS-decodes, checks CRC-16 and `length`.
5. On success, RB hands the **decoded logical frame** to `radio_tx` verbatim.
6. The radio chip appends its own CRC-32 FCS.

COBS never appears on the air. A CRC-16 failure on the ground means
corruption somewhere in the whole path; an FCS failure with good CRC-16
would mean air-only corruption (unusual with this layout, since FCS covers
the same PSDU).

### Plain COBS rules

- Empty input → `01`.
- Encoded body contains no `0x00`.
- Trailing delimiter is **not** part of encode's return value; the sender
  adds it.
- A 254-byte run of non-zeros uses code `0xFF`.
- Malformed COBS → discard and resync at the next `0x00`.

### Published encode vectors (no trailing delimiter)

| Input (hex)              | Encoded (hex)                |
| ------------------------ | ---------------------------- |
| *(empty)*                | `01`                         |
| `00`                     | `01 01`                      |
| `00 00`                  | `01 01 01`                   |
| `11`                     | `02 11`                      |
| `11 22`                  | `03 11 22`                   |
| `11 00`                  | `02 11 01`                   |
| `11 00 00`               | `02 11 01 01`                |
| `11 22 00 33`            | `03 11 22 02 33`             |
| `11 22 33 44`            | `05 11 22 33 44`             |

## Traffic model

One-way, fire-and-forget. No ACK, no retry, no frame kinds. Sequence
number is for gap detection on the ground and in the send log only.

## Content

Opaque to this document. Defined by `telemetry.build_content` on the BBG.
Number format (int16 vs float32) is deferred until that function is written;
document the choice in a comment above it.

## Constants (must match across languages)

```
CALLSIGN      = b"VE3 JKB"
VERSION       = 1
HEADER_SIZE   = 16
CRC_SIZE      = 2
MAX_CONTENT   = 1024
CRC_INIT      = 0xFFFF
CRC_CHECK     = 0x29B1
```
