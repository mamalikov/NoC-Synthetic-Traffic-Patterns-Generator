#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import image as mpimg
from patterns import bitComplement, bitReverse, bitRotation, broadcast, graph, neighbor, shuffle, tornado, transpose
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Testing' / 'results' / 'pattern_figures'
PAPER = ROOT / 'Testing' / 'results' / 'paper_figures'

def panel(rows, cols, **kwargs) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    name = kwargs.pop('name')
    path = OUT / name
    graph(rows, cols, outfile=str(path), **kwargs)
    return path

def side_by_side(paths: list[Path], out: Path, titles: list[str]) -> None:
    n = len(paths)
    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 5.0))
    if n == 1:
        axes = [axes]
    for ax, p, title in zip(axes, paths, titles):
        ax.imshow(mpimg.imread(p))
        ax.set_title(title, fontsize=11)
        ax.axis('off')
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)

def main() -> None:
    p1a = panel(4, 4, pattern=bitComplement, label='Bit-complement (4x4)', name='fig01a_bitcomplement_4x4.png')
    p1b = panel(4, 4, pattern=bitReverse, label='Bit-reverse (4x4)', name='fig01b_bitreverse_4x4.png')
    p1c = panel(4, 4, pattern=bitRotation, label='Bit-rotation (4x4)', name='fig01c_bitrotation_4x4.png')
    p2a = panel(4, 4, pattern=shuffle, label='Shuffle (4x4)', name='fig02a_shuffle_4x4.png')
    p2b = panel(4, 4, pattern=transpose, label='Transpose (4x4)', name='fig02b_transpose_4x4.png')
    p3a = panel(8, 8, pattern=tornado, label='Tornado (8x8)', name='fig03a_tornado_8x8.png')
    p3b = panel(8, 8, pattern=neighbor, label='Neighbor (8x8)', name='fig03b_neighbor_8x8.png')
    p4a = panel(4, 4, pattern=broadcast, hotspot=4, direction='in', label='All-to-one (hotspot=4)', name='fig04a_all_to_one_4x4.png')
    p4b = panel(4, 4, pattern=broadcast, hotspot=10, direction='out', label='One-to-all (hotspot=10)', name='fig04b_one_to_all_4x4.png')
    p4c = panel(4, 4, pattern=broadcast, hotspot=-1, direction='in', label='All-to-all', name='fig04c_all_to_all_4x4.png')
    p5a = panel(4, 2, pattern=bitReverse, label='Bit-reverse (4x2)', name='fig05a_bitreverse_4x2.png')
    p5b = panel(4, 8, pattern=bitReverse, label='Bit-reverse (4x8)', name='fig05b_bitreverse_4x8.png')
    p6a = panel(3, 4, pattern=bitReverse, label='Bit-reverse (3x4)', name='fig06a_bitreverse_3x4.png')
    p6b = panel(5, 2, pattern=bitReverse, label='Bit-reverse (5x2)', name='fig06b_bitreverse_5x2.png')
    p6c = panel(6, 6, pattern=bitReverse, label='Bit-reverse (6x6)', name='fig06c_bitreverse_6x6.png')
    PAPER.mkdir(parents=True, exist_ok=True)
    for p in (p1a, p1b, p1c, p2a, p2b, p3a, p3b, p4a, p4b, p4c, p5a, p5b, p6a, p6b, p6c):
        dest = PAPER / p.name
        dest.write_bytes(p.read_bytes())
    side_by_side([p1a, p1b, p1c], PAPER / 'fig01_bit_permutations_4x4.png', ['(a) Bit-complement', '(b) Bit-reverse', '(c) Bit-rotation'])
    side_by_side([p2a, p2b], PAPER / 'fig02_shuffle_transpose_4x4.png', ['(a) Shuffle', '(b) Transpose'])
    side_by_side([p3a, p3b], PAPER / 'fig03_tornado_neighbor_8x8.png', ['(a) Tornado', '(b) Neighbor'])
    side_by_side([p4a, p4b, p4c], PAPER / 'fig04_broadcast_4x4.png', ['(a) All-to-one', '(b) One-to-all', '(c) All-to-all'])
    side_by_side([p5a, p5b], PAPER / 'fig05_bitreverse_power2.png', ['(a) 4×2', '(b) 4×8'])
    side_by_side([p6a, p6b, p6c], PAPER / 'fig06_bitreverse_other.png', ['(a) 3×4', '(b) 5×2', '(c) 6×6'])
if __name__ == '__main__':
    main()
