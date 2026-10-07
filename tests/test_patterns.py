from __future__ import annotations

import math
import random
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patterns import (
    bitComplement,
    bitReverse,
    bitRotation,
    broadcast,
    generatePacketsPairs,
    generatePacketsTimed,
    neighbor,
    shuffle,
    tornado,
    transpose,
    uniform,
)


def _bits(n: int) -> int:
    return len(bin(n - 1)[2:])


def _rev(src: int, n: int) -> int:
    b = _bits(n)
    s = format(src, f"0{b}b")
    return int(s[::-1], 2) % n


def _complement(src: int, n: int) -> int:
    b = _bits(n)
    s = format(src, f"0{b}b")
    return int("".join("1" if c == "0" else "0" for c in s), 2) % n


def _rotate(src: int, n: int) -> int:
    b = _bits(n)
    s = format(src, f"0{b}b")
    return int(s[1:] + s[0], 2) % n


def _shuffle(src: int, n: int) -> int:
    b = _bits(n)
    s = format(src, f"0{b}b")
    return int(s[-1] + s[:-1], 2) % n


def _transpose(src: int, n: int) -> int:
    b = _bits(n)
    s = format(src, f"0{b}b")
    shift = round(b / 2)
    return int(s[shift:] + s[:shift], 2) % n


class TestBitPermutations(unittest.TestCase):
    def test_bit_reverse_matches_formula(self):
        for n in (8, 16, 64):
            for src in range(n):
                expected = _rev(src, n)
                got = bitReverse(src, n, allow_self=True)
                self.assertEqual(got, expected)
                if expected == src:
                    self.assertEqual(bitReverse(src, n), -1)
                else:
                    self.assertEqual(bitReverse(src, n), expected)

    def test_bit_complement_matches_formula(self):
        for n in (8, 16, 64):
            for src in range(n):
                expected = _complement(src, n)
                self.assertEqual(bitComplement(src, n, allow_self=True), expected)
                if expected == src:
                    self.assertEqual(bitComplement(src, n), -1)
                else:
                    self.assertEqual(bitComplement(src, n), expected)

    def test_bit_rotation_and_shuffle(self):
        for n in (8, 16):
            for src in range(n):
                rot = _rotate(src, n)
                sh = _shuffle(src, n)
                self.assertEqual(bitRotation(src, n, allow_self=True), rot)
                self.assertEqual(shuffle(src, n, allow_self=True), sh)
                if rot == src:
                    self.assertEqual(bitRotation(src, n), -1)
                if sh == src:
                    self.assertEqual(shuffle(src, n), -1)

    def test_transpose_matches_formula(self):
        for n in (8, 16, 64):
            for src in range(n):
                expected = _transpose(src, n)
                self.assertEqual(transpose(src, n, allow_self=True), expected)

    def test_destinations_in_range(self):
        for n in (8, 16, 32):
            for src in range(n):
                for fn in (bitReverse, bitRotation, shuffle, transpose):
                    dst = fn(src, n, allow_self=True)
                    self.assertGreaterEqual(dst, 0)
                    self.assertLess(dst, n)
                dst = bitComplement(src, n)
                self.assertGreaterEqual(dst, 0)
                self.assertLess(dst, n)


class TestDigitPermutations(unittest.TestCase):
    def test_neighbor_2d_mesh(self):
        n = 16
        for src in range(n):
            x, y = src % 4, src // 4
            expected = ((x + 1) % 4) + ((y + 1) % 4) * 4
            self.assertEqual(neighbor(src, n), expected)

    def test_tornado_equals_neighbor_when_k_even_offset_one(self):
        n = 16
        for src in range(n):
            self.assertEqual(tornado(src, n), neighbor(src, n))

    def test_neighbor_1d_ring(self):
        n = 7
        for src in range(n):
            self.assertEqual(neighbor(src, n), (src + 1) % n)

    def test_tornado_1d(self):
        n = 7
        offset = math.ceil(7 / 2) - 1
        for src in range(n):
            self.assertEqual(tornado(src, n), (src + offset) % n)


class TestNeighborTornadoBitComplementRanges(unittest.TestCase):
    SIZES = (7, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 27, 32, 36, 49, 64)

    def test_destinations_in_range_or_silent(self):
        for n in self.SIZES:
            for src in range(n):
                for fn in (neighbor, tornado, bitComplement):
                    dst = fn(src, n)
                    self.assertIn(
                        dst,
                        (-1, *range(n)),
                        msg=f"{fn.__name__}(src={src}, n={n}) -> {dst}",
                    )
                    dst_self = fn(src, n, allow_self=True)
                    self.assertGreaterEqual(dst_self, 0)
                    self.assertLess(dst_self, n)

    def test_bit_complement_formula_non_power_of_two(self):
        for n in (7, 9, 10, 12, 15, 18, 20, 24):
            for src in range(n):
                expected = _complement(src, n)
                self.assertEqual(bitComplement(src, n, allow_self=True), expected)
                self.assertLess(expected, n)

    def test_neighbor_tornado_digit_formula_varied_sizes(self):
        for n in self.SIZES:
            for src in range(n):
                root2 = int(round(math.sqrt(n)))
                root3 = int(round(n ** (1.0 / 3.0)))
                if root2 * root2 == n:
                    k, ndim = root2, 2
                elif root3**3 == n:
                    k, ndim = root3, 3
                else:
                    k, ndim = n, 1

                digits = []
                x = src
                for _ in range(ndim):
                    digits.append(x % k)
                    x //= k

                def rebuild(ds):
                    dest, mul = 0, 1
                    for d in ds:
                        dest += d * mul
                        mul *= k
                    return dest

                nb = rebuild([(d + 1) % k for d in digits])
                tor = rebuild([(d + (math.ceil(k / 2) - 1)) % k for d in digits])
                self.assertEqual(neighbor(src, n, allow_self=True), nb)
                self.assertEqual(tornado(src, n, allow_self=True), tor)
                self.assertLess(nb, n)
                self.assertLess(tor, n)

    def test_tornado_equals_neighbor_on_4x4(self):
        n = 16
        for src in range(n):
            self.assertEqual(tornado(src, n), neighbor(src, n))


class TestUniform(unittest.TestCase):
    def test_never_self(self):
        random.seed(0)
        n = 16
        for src in range(n):
            for _ in range(50):
                dst = uniform(src, n)
                self.assertNotEqual(dst, src)
                self.assertGreaterEqual(dst, 0)
                self.assertLess(dst, n)

    def test_stochastic(self):
        random.seed(1)
        n = 32
        samples = {uniform(0, n) for _ in range(40)}
        self.assertGreater(len(samples), 1)


class TestBroadcast(unittest.TestCase):
    def test_all_to_all(self):
        n = 8
        dsts = broadcast(2, n)
        self.assertEqual(dsts, [i for i in range(n) if i != 2])

    def test_all_to_one(self):
        n = 8
        hotspot = 3
        for src in range(n):
            dst = broadcast(src, n, hotspot=hotspot, direction="in")
            if src == hotspot:
                self.assertIsNone(dst)
            else:
                self.assertEqual(dst, hotspot)

    def test_one_to_all(self):
        n = 8
        hotspot = 3
        self.assertEqual(
            broadcast(hotspot, n, hotspot=hotspot, direction="out"),
            [i for i in range(n) if i != hotspot],
        )
        for src in range(n):
            if src == hotspot:
                continue
            self.assertIsNone(broadcast(src, n, hotspot=hotspot, direction="out"))


class TestGenerators(unittest.TestCase):
    def test_pairs_exact_count_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "pairs.txt"
            generatePacketsPairs(neighbor, 16, 100, outfilename=str(out), random_order=False)
            lines = out.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 100)
            for line in lines:
                src, dst = map(int, line.split())
                self.assertNotEqual(src, dst)
                self.assertEqual(dst, neighbor(src, 16))

    def test_pairs_exact_count_random(self):
        random.seed(0)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "pairs.txt"
            generatePacketsPairs(uniform, 16, 50, outfilename=str(out), random_order=True)
            lines = out.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 50)
            for line in lines:
                src, dst = map(int, line.split())
                self.assertNotEqual(src, dst)

    def test_pairs_all_to_one(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "pairs.txt"
            generatePacketsPairs(
                broadcast,
                8,
                21,
                hotspot=0,
                direction="in",
                outfilename=str(out),
                random_order=False,
            )
            lines = out.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 21)
            for line in lines:
                src, dst = map(int, line.split())
                self.assertEqual(dst, 0)
                self.assertNotEqual(src, 0)

    def test_timed_silent_hotspot(self):
        with tempfile.TemporaryDirectory() as td:
            generatePacketsTimed(
                broadcast,
                8,
                5,
                distribution="poisson",
                lam=10,
                output_dir=td,
                hotspot=2,
                direction="in",
            )
            root = Path(td)
            self.assertEqual((root / "2.txt").read_text(encoding="utf-8"), "")
            for i in range(8):
                if i == 2:
                    continue
                lines = (root / f"{i}.txt").read_text(encoding="utf-8").strip().splitlines()
                self.assertEqual(len(lines), 5)
                for line in lines:
                    dst, _delay = line.split()
                    self.assertEqual(int(dst), 2)

    def test_timed_bitreverse_self_maps_empty(self):
        n = 16
        with tempfile.TemporaryDirectory() as td:
            generatePacketsTimed(
                bitReverse, n, 3, distribution="poisson", lam=5, output_dir=td
            )
            root = Path(td)
            silent = [i for i in range(n) if bitReverse(i, n) == -1]
            self.assertTrue(silent)
            for i in silent:
                self.assertEqual((root / f"{i}.txt").read_text(encoding="utf-8"), "")
            active = [i for i in range(n) if i not in silent]
            for i in active:
                lines = (root / f"{i}.txt").read_text(encoding="utf-8").strip().splitlines()
                self.assertEqual(len(lines), 3)
                for line in lines:
                    dst, _ = line.split()
                    self.assertEqual(int(dst), bitReverse(i, n))

    def test_pairs_shuffle_preserves_multiset(self):
        random.seed(42)
        with tempfile.TemporaryDirectory() as td:
            ordered = Path(td) / "o.txt"
            shuffled = Path(td) / "s.txt"
            generatePacketsPairs(neighbor, 16, 64, outfilename=str(ordered), random_order=False)
            generatePacketsPairs(neighbor, 16, 64, outfilename=str(shuffled), random_order=True)
            a = [tuple(map(int, ln.split())) for ln in ordered.read_text().splitlines() if ln]
            b = [tuple(map(int, ln.split())) for ln in shuffled.read_text().splitlines() if ln]
            self.assertEqual(Counter(a), Counter(b))


if __name__ == "__main__":
    unittest.main()
