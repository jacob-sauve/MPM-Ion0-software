"""COBS encode/decode tests — these ARE the spec for cobs.py.

Published vectors follow Wikipedia / consistent-overhead-byte-stuffing.
"""

from __future__ import annotations

import unittest

from ion.greenbear import cobs


# (plaintext, encoded_without_trailing_delimiter)
PUBLISHED_VECTORS: list[tuple[bytes, bytes]] = [
    (b"", b"\x01"),
    (b"\x00", b"\x01\x01"),
    (b"\x00\x00", b"\x01\x01\x01"),
    (b"\x11", b"\x02\x11"),
    (b"\x11\x22", b"\x03\x11\x22"),
    (b"\x11\x00", b"\x02\x11\x01"),
    (b"\x11\x00\x00", b"\x02\x11\x01\x01"),
    (b"\x11\x22\x00\x33", b"\x03\x11\x22\x02\x33"),
    (b"\x11\x22\x33\x44", b"\x05\x11\x22\x33\x44"),
    (b"\x11\x22\x33\x44\x55", b"\x06\x11\x22\x33\x44\x55"),
    # classic longer vector
    (
        bytes([0x00, 0x11, 0x00, 0x00, 0x22, 0x00]),
        bytes([0x01, 0x02, 0x11, 0x01, 0x02, 0x22, 0x01]),
    ),
]


class TestCobsPublished(unittest.TestCase):
    def test_encode_published_vectors(self) -> None:
        for plain, encoded in PUBLISHED_VECTORS:
            with self.subTest(plain=plain.hex()):
                self.assertEqual(cobs.encode(plain), encoded)

    def test_decode_published_vectors(self) -> None:
        for plain, encoded in PUBLISHED_VECTORS:
            with self.subTest(plain=plain.hex()):
                self.assertEqual(cobs.decode(encoded), plain)

    def test_round_trip_published(self) -> None:
        for plain, _ in PUBLISHED_VECTORS:
            with self.subTest(plain=plain.hex()):
                self.assertEqual(cobs.decode(cobs.encode(plain)), plain)


class TestCobsProperties(unittest.TestCase):
    def test_encoded_contains_no_zeros(self) -> None:
        samples = [
            b"",
            b"\x00" * 10,
            bytes(range(256)),
            b"\xff" * 300,
            b"abc\x00def\x00\x00ghi",
        ]
        for sample in samples:
            with self.subTest(sample=sample[:20].hex()):
                encoded = cobs.encode(sample)
                self.assertNotIn(0, encoded)

    def test_round_trip_all_byte_values(self) -> None:
        data = bytes(range(256))
        self.assertEqual(cobs.decode(cobs.encode(data)), data)

    def test_round_trip_254_nonzero(self) -> None:
        # Exactly one full COBS block of non-zeros (code 0xFF).
        data = bytes([0x11] * 254)
        encoded = cobs.encode(data)
        self.assertEqual(cobs.decode(encoded), data)
        self.assertNotIn(0, encoded)

    def test_round_trip_255_nonzero(self) -> None:
        data = bytes([0x22] * 255)
        self.assertEqual(cobs.decode(cobs.encode(data)), data)

    def test_round_trip_many_zeros(self) -> None:
        data = b"\x00" * 100
        self.assertEqual(cobs.decode(cobs.encode(data)), data)

    def test_round_trip_zero_heavy_mixed(self) -> None:
        data = bytes([0 if i % 3 == 0 else (i % 255) + 1 for i in range(500)])
        self.assertEqual(cobs.decode(cobs.encode(data)), data)


class TestCobsMalformed(unittest.TestCase):
    def test_decode_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            cobs.decode(b"")

    def test_decode_truncated_code_raises(self) -> None:
        # Code says 5 bytes follow, but only 2 remain.
        with self.assertRaises(ValueError):
            cobs.decode(b"\x05\x11\x22")

    def test_decode_embedded_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            cobs.decode(b"\x03\x11\x00\x22")


if __name__ == "__main__":
    unittest.main()
