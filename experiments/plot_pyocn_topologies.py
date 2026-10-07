#!/usr/bin/env python3
from __future__ import annotations
import json
import math
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, MaxNLocator, NullLocator
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Testing' / 'results' / 'pyocn' / 'topologies.json'
OUT = ROOT / 'Testing' / 'results' / 'pyocn' / 'figures_topologies'
LINEAR_Y_TOPOS = {'mesh', 'bfly'}
PATTERN_ORDER = ['urandom', 'bit-complement', 'bit-reverse', 'bit-rotation', 'shuffle', 'transpose', 'neighbor', 'tornado']
PATTERN_LABELS = {'urandom': 'Uniform', 'bit-complement': 'Bit-complement', 'bit-reverse': 'Bit-reverse', 'bit-rotation': 'Bit-rotation', 'shuffle': 'Shuffle', 'transpose': 'Transpose', 'neighbor': 'Neighbor', 'tornado': 'Tornado'}

def title_for(topo: str, terminals: int | None) -> str:
    if topo == 'cmesh' and terminals is not None:
        return f'CMesh {terminals} terminals'
    if topo == 'mesh':
        return 'Mesh'
    if topo == 'bfly':
        return 'Butterfly'
    return topo

def out_stem(topo: str, terminals: int | None) -> str:
    if topo == 'cmesh' and terminals is not None:
        return f'latency_vs_cores_cmesh_{terminals}term'
    return f'latency_vs_cores_{topo}'

def pow2_label(x: float, _pos=None) -> str:
    if x <= 0:
        return ''
    exp = int(round(math.log2(x)))
    if abs(x - 2 ** exp) / x > 1e-06:
        return ''
    return f'$2^{{{exp}}}$'

def apply_log2_x(ax, xs: list[int]) -> None:
    ax.set_xscale('log', base=2)
    ax.xaxis.set_major_locator(FixedLocator(xs))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(pow2_label))

def apply_log2_y(ax, ys_all: list[float]) -> None:
    ax.set_yscale('log', base=2)
    y_min = min(ys_all)
    y_max = max(ys_all)
    e_hi = int(math.floor(math.log2(max(y_max, 2))))
    if e_hi % 2 == 0:
        e_hi -= 1
    e_hi = max(e_hi, 1)
    y_ticks = [2 ** e for e in range(1, e_hi + 1, 2)]
    ax.yaxis.set_major_locator(FixedLocator(y_ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(pow2_label))
    ax.set_ylim(bottom=min(y_min * 0.85, 2 ** 0.5), top=max(y_max * 1.2, y_ticks[-1]))

def apply_linear_y(ax, ys_all: list[float]) -> None:
    ax.set_yscale('linear')
    y_min = min(ys_all)
    y_max = max(ys_all)
    pad = max(0.5, 0.08 * (y_max - y_min))
    ax.set_ylim(bottom=max(0.0, y_min - pad), top=y_max + pad)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))

def main() -> None:
    records = json.loads(DATA.read_text(encoding='utf-8'))['data']
    grouped: dict[tuple, list[tuple[int, float]]] = defaultdict(list)
    configs: set[tuple[str, int | None]] = set()
    for r in records:
        topo = r['topology']
        terminals = int(r['terminals']) if 'terminals' in r else None
        key = (topo, terminals, r['traffic'])
        grouped[key].append((int(r['size']), float(r['average latency'])))
        configs.add((topo, terminals))
    OUT.mkdir(parents=True, exist_ok=True)
    ordered = sorted(configs, key=lambda c: (0 if c[0] == 'cmesh' else 1, c[0], c[1] if c[1] is not None else -1))
    for topo, terminals in ordered:
        fig, ax = plt.subplots(figsize=(6.0, 4.8))
        plotted = False
        ys_all: list[float] = []
        for pat in PATTERN_ORDER:
            series = grouped.get((topo, terminals, pat))
            if not series:
                continue
            series = sorted(series, key=lambda p: p[0])
            xs = [size for size, _ in series]
            ys = [lat for _, lat in series]
            ys_all.extend(ys)
            ax.plot(xs, ys, marker='o', markersize=4, label=PATTERN_LABELS.get(pat, pat))
            plotted = True
        if not plotted:
            plt.close()
            continue
        xs_all = sorted({size for pat in PATTERN_ORDER for size, _ in grouped.get((topo, terminals, pat), [])})
        apply_log2_x(ax, xs_all)
        if topo in LINEAR_Y_TOPOS:
            apply_linear_y(ax, ys_all)
        else:
            apply_log2_y(ax, ys_all)
        ax.set_xlabel('Number of cores')
        ax.set_ylabel('Average latency (cycles)')
        ax.set_title(title_for(topo, terminals))
        ax.grid(True, which='major', linestyle='-', alpha=0.35)
        ax.legend()
        fig.tight_layout()
        stem = out_stem(topo, terminals)
        out_path = OUT / f'{stem}.png'
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        csv_path = OUT / f'{stem}.csv'
        lines = ['pattern,number_of_cores,average_latency\n']
        for pat in PATTERN_ORDER:
            series = grouped.get((topo, terminals, pat))
            if not series:
                continue
            for size, lat in sorted(series, key=lambda p: p[0]):
                lines.append(f'{pat},{size},{lat:.6g}\n')
        csv_path.write_text(''.join(lines), encoding='utf-8')
if __name__ == '__main__':
    main()
