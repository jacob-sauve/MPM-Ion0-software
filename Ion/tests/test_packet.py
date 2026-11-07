"""Packet build/parse tests — these ARE the spec for packet.py."""

from __future__ import annotations

import struct
import unittest

from ion.greenbear import config, packet


def _manual_header(seq: int, time: int, content: bytes) -> bytes:
    """Reference layout for tests that need a known-good frame without build()."""
    return (
        config.CALLSIGN
        + bytes([config.VERSION])
        + struct.pack("<H", seq & 0xFFFF)
        + struct.pack("<I", time & 0xFFFFFFFF)
        + struct.pack("<H", len(content))
        + content
    )


class TestCrc(unittest.TestCase):
    def test_check_value_123456789(self) -> None:
        self.assertEqual(packet.crc16(b"123456789"), config.CRC_CHECK)

    def test_crc_is_16_bit(self) -> None:
        value = packet.crc16(b"hello")
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 0xFFFF)


class TestBuild(unittest.TestCase):
    def test_round_trip_empty_content(self) -> None:
        frame = packet.build(seq=1, time=1_700_000_000, content=b"")
        parsed = packet.parse(frame)
        self.assertEqual(parsed.callsign, config.CALLSIGN)
        self.assertEqual(parsed.version, config.VERSION)
        self.assertEqual(parsed.seq, 1)
        self.assertEqual(parsed.time, 1_700_000_000)
        self.assertEqual(parsed.content, b"")

    def test_round_trip_with_content(self) -> None:
        content = b"hello-green-bear\x00\xff"
        frame = packet.build(seq=0x1234, time=42, content=content)
        parsed = packet.parse(frame)
        self.assertEqual(parsed.seq, 0x1234)
        self.assertEqual(parsed.time, 42)
        self.assertEqual(parsed.content, content)

    def test_frame_length(self) -> None:
        content = b"abc"
        frame = packet.build(seq=0, time=0, content=content)
        self.assertEqual(
            len(frame),
            config.HEADER_SIZE + len(content) + config.CRC_SIZE,
        )

    def test_little_endian_fields(self) -> None:
        frame = packet.build(seq=0x1234, time=0x89ABCDEF, content=b"\xaa")
        # callsign(7) + version(1) = 8
        self.assertEqual(frame[8:10], b"\x34\x12")  # seq LE
        self.assertEqual(frame[10:14], b"\xef\xcd\xab\x89")  # time LE
        self.assertEqual(frame[14:16], b"\x01\x00")  # length 1 LE
        self.assertEqual(frame[16:17], b"\xaa")

    def test_callsign_prefix(self) -> None:
        frame = packet.build(seq=0, time=0, content=b"")
        self.assertEqual(frame[:7], config.CALLSIGN)

    def test_max_content_accepted(self) -> None:
        content = b"\x5a" * config.MAX_CONTENT
        frame = packet.build(seq=9, time=9, content=content)
        self.assertEqual(packet.parse(frame).content, content)

    def test_max_content_plus_one_rejected(self) -> None:
        content = b"\x5a" * (config.MAX_CONTENT + 1)
        with self.assertRaises(ValueError):
            packet.build(seq=0, time=0, content=content)

    def test_seq_wraps_to_u16(self) -> None:
        # Implementation may accept and mask, or raise — either is fine
        # as long as the on-wire field is u16. Prefer mask for flight use.
        frame = packet.build(seq=65536, time=0, content=b"")
        self.assertEqual(packet.parse(frame).seq, 0)


class TestParse(unittest.TestCase):
    def test_truncation_raises(self) -> None:
        with self.assertRaises(ValueError):
            packet.parse(b"short")

    def test_bad_callsign_raises(self) -> None:
        content = b"x"
        body = _manual_header(1, 1, content)
        # corrupt callsign
        body = b"XXXXXXX" + body[7:]
        crc = packet.crc16(body)
        frame = body + struct.pack("<H", crc)
        with self.assertRaises(ValueError):
            packet.parse(frame)

    def test_bad_version_raises(self) -> None:
        content = b"x"
        body = bytearray(_manual_header(1, 1, content))
        body[7] = 99
        crc = packet.crc16(bytes(body))
        frame = bytes(body) + struct.pack("<H", crc)
        with self.assertRaises(ValueError):
            packet.parse(frame)

    def test_bad_crc_raises(self) -> None:
        frame = bytearray(packet.build(seq=1, time=1, content=b"hi"))
        frame[-1] ^= 0xFF
        with self.assertRaises(ValueError):
            packet.parse(bytes(frame))

    def test_length_mismatch_raises(self) -> None:
        # Claim length 5 but only provide 1 content byte before CRC.
        body = bytearray(_manual_header(1, 1, b"x"))
        body[14:16] = struct.pack("<H", 5)
        crc = packet.crc16(bytes(body))
        frame = bytes(body) + struct.pack("<H", crc)
        with self.assertRaises(ValueError):
            packet.parse(frame)

    def test_known_vector_callsign_empty(self) -> None:
        """Fixed vector: seq=0x1234, time=0, empty content.

        CRC computed with the real crc16 so this stays a layout check even
        before you implement build — once build works, it must match.
        """
        body = _manual_header(0x1234, 0, b"")
        crc = packet.crc16(body)
        frame = body + struct.pack("<H", crc)
        built = packet.build(seq=0x1234, time=0, content=b"")
        self.assertEqual(built, frame)


if __name__ == "__main__":
    unittest.main()
