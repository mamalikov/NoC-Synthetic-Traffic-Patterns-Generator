#!/usr/bin/env python3
from __future__ import annotations
import csv
import random
import statistics
import sys
import tempfile
import time
import tracemalloc
from functools import partial
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

def _pow10_label(x: float, _pos=None) -> str:
    if x <= 0:
        return ''
    exp = int(round(np.log10(x)))
    if abs(x - 10 ** exp) <= 0.5 * 10 ** max(exp - 1, 0):
        return f'$10^{{{exp}}}$'
    return f'{x:g}'

def _pow2_label(x: float, _pos=None) -> str:
    if x <= 0:
        return ''
    exp = int(round(np.log2(x)))
    if abs(x - 2 ** exp) < 1e-09:
        return f'$2^{{{exp}}}$'
    return f'{x:g}'

def _apply_grid(ax=None, x_ticks=None, x_label_mode: str | None=None, x_scale: str | None=None) -> None:
    ax = ax or plt.gca()
    if x_scale == 'log2':
        ax.set_xscale('log', base=2)
    elif x_scale == 'log10':
        ax.set_xscale('log', base=10)
    ax.yaxis.set_minor_locator(NullLocator())
    ax.grid(False)
    ax.grid(True, which='major', axis='y', linestyle='--', alpha=0.4)
    if x_ticks is not None:
        ticks = list(x_ticks)
        ax.xaxis.set_major_locator(FixedLocator(ticks))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xticks(ticks)
        if x_label_mode == 'pow10':
            ax.xaxis.set_major_formatter(FuncFormatter(_pow10_label))
        elif x_label_mode == 'pow2':
            ax.xaxis.set_major_formatter(FuncFormatter(_pow2_label))
        for x in ticks:
            ax.axvline(x, linestyle='--', alpha=0.4, color='0.75', zorder=0)
    else:
        ax.xaxis.set_minor_locator(NullLocator())
        ax.grid(True, which='major', axis='x', linestyle='--', alpha=0.4)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from patterns import bitReverse, broadcast, generatePacketsPairs, generatePacketsTimed, neighbor, tornado, uniform
OUT = ROOT / 'Testing' / 'results' / 'nocstg' / 'scalability'
OUT.mkdir(parents=True, exist_ok=True)
ALL_TO_ONE_HOTSPOT = 0
PATTERNS = {'neighbor': neighbor, 'bitReverse': bitReverse, 'tornado': tornado, 'random': uniform, 'allToOne': partial(broadcast, hotspot=ALL_TO_ONE_HOTSPOT, direction='in')}
PATTERN_LABELS = {'neighbor': 'Neighbor', 'bitReverse': 'Bit-reverse', 'tornado': 'Tornado', 'random': 'Random uniform', 'allToOne': 'All-to-one'}
PATTERN_STYLES = {'neighbor': {'marker': 'o', 'linestyle': '-'}, 'bitReverse': {'marker': 's', 'linestyle': '--'}, 'tornado': {'marker': '^', 'linestyle': '-.'}, 'random': {'marker': 'D', 'linestyle': '-'}, 'allToOne': {'marker': 'v', 'linestyle': ':'}}
TIMED_PATTERNS = tuple(PATTERNS.keys())
TIMED_LABELS = dict(PATTERN_LABELS)
PAIR_SIZES = [16, 64, 256, 1024, 4096]
PAIR_COUNTS = [10000, 100000, 1000000]
TIMED_SIZES = [16, 64, 256, 1024]
TIMED_COUNTS_PER_PE = [1000, 10000]
REPEATS = 3

def _dir_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum((p.stat().st_size for p in path.rglob('*') if p.is_file()))

def bench_pairs(pattern_name: str, n: int, count: int, work: Path) -> dict:
    out = work / f'pairs_{pattern_name}_n{n}_c{count}.txt'
    fn = PATTERNS[pattern_name]
    tracemalloc.start()
    t0 = time.perf_counter()
    generatePacketsPairs(fn, n, count, outfilename=str(out), random_order=True)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    size = out.stat().st_size
    lines = sum((1 for _ in out.open('r', encoding='utf-8')))
    return {'mode': 'pairs', 'pattern': pattern_name, 'N': n, 'count': count, 'total_packets': count, 'time_s': elapsed, 'peak_mem_mib': peak / (1024 * 1024), 'output_mib': size / (1024 * 1024), 'lines': lines}

def bench_timed(pattern_name: str, n: int, count_per_pe: int, work: Path) -> dict:
    out_dir = work / f'timed_{pattern_name}_n{n}_c{count_per_pe}'
    out_dir.mkdir(parents=True, exist_ok=True)
    fn = PATTERNS[pattern_name]
    kwargs = {}
    if pattern_name == 'allToOne':
        kwargs = {'hotspot': ALL_TO_ONE_HOTSPOT, 'direction': 'in'}
    tracemalloc.start()
    t0 = time.perf_counter()
    generatePacketsTimed(broadcast if pattern_name == 'allToOne' else fn, n, count_per_pe, distribution='poisson', lam=10, output_dir=str(out_dir), **kwargs)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    size = _dir_size(out_dir)
    total_lines = 0
    for p in out_dir.glob('*.txt'):
        total_lines += sum((1 for _ in p.open('r', encoding='utf-8')))
    return {'mode': 'timed', 'pattern': pattern_name, 'N': n, 'count': count_per_pe, 'total_packets': total_lines, 'time_s': elapsed, 'peak_mem_mib': peak / (1024 * 1024), 'output_mib': size / (1024 * 1024), 'lines': total_lines}

def median_run(fn, *args) -> dict:
    runs = [fn(*args) for _ in range(REPEATS)]
    out = dict(runs[0])
    out['time_s'] = statistics.median((r['time_s'] for r in runs))
    out['peak_mem_mib'] = statistics.median((r['peak_mem_mib'] for r in runs))
    out['output_mib'] = statistics.median((r['output_mib'] for r in runs))
    out['total_packets'] = int(statistics.median((r['total_packets'] for r in runs)))
    out['lines'] = int(statistics.median((r['lines'] for r in runs)))
    out['repeats'] = REPEATS
    return out

def plot_pairs_time_vs_count(rows: list[dict], n_fixed: int=1024) -> None:
    plt.figure(figsize=(6, 6))
    for name in PATTERNS:
        xs, ys = ([], [])
        for r in rows:
            if r['mode'] == 'pairs' and r['pattern'] == name and (r['N'] == n_fixed):
                xs.append(r['count'])
                ys.append(r['time_s'])
        if xs:
            order = np.argsort(xs)
            xs = np.array(xs)[order]
            ys = np.array(ys)[order]
            style = PATTERN_STYLES[name]
            plt.plot(xs, ys, marker=style['marker'], linestyle=style['linestyle'], markersize=7, label=PATTERN_LABELS[name])
    plt.xlabel('Number of packets')
    plt.ylabel('Generation time (s)')
    plt.title(f'Pair generation time vs packets (N={n_fixed})')
    _apply_grid(x_ticks=PAIR_COUNTS, x_label_mode='pow10')
    plt.legend()
    plt.tight_layout()
    path = OUT / f'pairs_time_vs_count_N{n_fixed}.png'
    plt.savefig(path, dpi=150)
    plt.close()

def plot_pairs_time_vs_n(rows: list[dict], count_fixed: int=1000000) -> None:
    plt.figure(figsize=(6, 6))
    for name in PATTERNS:
        xs, ys = ([], [])
        for r in rows:
            if r['mode'] == 'pairs' and r['pattern'] == name and (r['count'] == count_fixed):
                xs.append(r['N'])
                ys.append(r['time_s'])
        if xs:
            order = np.argsort(xs)
            xs = np.array(xs)[order]
            ys = np.array(ys)[order]
            style = PATTERN_STYLES[name]
            plt.plot(xs, ys, marker=style['marker'], linestyle=style['linestyle'], markersize=7, label=PATTERN_LABELS[name])
    plt.xlabel('Network size N')
    plt.ylabel('Generation time (s)')
    _apply_grid(x_ticks=PAIR_SIZES, x_label_mode='pow2', x_scale='log2')
    plt.legend()
    plt.tight_layout()
    path = OUT / f'pairs_time_vs_N_c{count_fixed}.png'
    plt.savefig(path, dpi=150)
    plt.close()

def plot_pairs_mem_vs_count(rows: list[dict], n_fixed: int=1024) -> None:
    plt.figure(figsize=(6, 6))
    for name in PATTERNS:
        xs, ys = ([], [])
        for r in rows:
            if r['mode'] == 'pairs' and r['pattern'] == name and (r['N'] == n_fixed):
                xs.append(r['count'])
                ys.append(r['peak_mem_mib'])
        if xs:
            order = np.argsort(xs)
            xs = np.array(xs)[order]
            ys = np.array(ys)[order]
            style = PATTERN_STYLES[name]
            plt.plot(xs, ys, marker=style['marker'], linestyle=style['linestyle'], markersize=7, label=PATTERN_LABELS[name])
    plt.xlabel('Number of packets')
    plt.ylabel('Peak memory (MiB)')
    plt.title(f'Pair generation peak memory vs packets (N={n_fixed})')
    _apply_grid(x_ticks=PAIR_COUNTS, x_label_mode='pow10')
    plt.legend()
    plt.tight_layout()
    path = OUT / f'pairs_mem_vs_count_N{n_fixed}.png'
    plt.savefig(path, dpi=150)
    plt.close()

def plot_timed_time_vs_total(rows: list[dict]) -> None:
    plt.figure(figsize=(6, 6))
    for name in TIMED_PATTERNS:
        xs, ys = ([], [])
        for r in rows:
            if r['mode'] == 'timed' and r['pattern'] == name:
                xs.append(r['total_packets'])
                ys.append(r['time_s'])
        if xs:
            order = np.argsort(xs)
            xs = np.array(xs)[order]
            ys = np.array(ys)[order]
            style = PATTERN_STYLES[name]
            plt.plot(xs, ys, marker=style['marker'], linestyle=style['linestyle'], markersize=7, label=TIMED_LABELS[name])
    plt.xlabel('Total packets written')
    plt.ylabel('Generation time (s)')
    plt.title('Timed-trace generation time vs total packets')
    _apply_grid(x_ticks=[10000, 100000, 1000000, 10000000], x_label_mode='pow10', x_scale='log10')
    plt.legend()
    plt.tight_layout()
    path = OUT / 'timed_time_vs_total_packets.png'
    plt.savefig(path, dpi=150)
    plt.close()

def write_summary(rows: list[dict]) -> None:
    csv_path = OUT / 'scalability_results.csv'
    fields = ['mode', 'pattern', 'N', 'count', 'total_packets', 'time_s', 'peak_mem_mib', 'output_mib', 'lines', 'repeats']
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})

    def fmt(x: float) -> str:
        if x >= 100:
            return f'{x:.2f}'
        if x >= 1:
            return f'{x:.3f}'
        return f'{x:.4g}'
    md = ['# NoCSTG scalability across traffic-pattern classes', '', f'Median of {REPEATS} runs. Peak memory via `tracemalloc`.', '', 'Patterns compared:', '- **neighbor** — neighbor traffic;', '- **bitReverse** — bit-permutation (power-of-two $N$);', '- **tornado** — tornado traffic;', '- **random** — random uniform (stochastic);', '- **allToOne** — all-to-one broadcast (hotspot node 0).', '', '## Pair generation (`generatePacketsPairs`)', '', '| Pattern | N | Packets | Time (s) | Peak mem (MiB) | Output (MiB) |', '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        if r['mode'] != 'pairs':
            continue
        md.append(f"| {r['pattern']} | {r['N']} | {r['count']} | {fmt(r['time_s'])} | {fmt(r['peak_mem_mib'])} | {fmt(r['output_mib'])} |")
    md += ['', '## Timed generation (`generatePacketsTimed`)', '', '| Pattern | N | Packets/PE | Total packets | Time (s) | Peak mem (MiB) | Output (MiB) |', '|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        if r['mode'] != 'timed':
            continue
        md.append(f"| {r['pattern']} | {r['N']} | {r['count']} | {r['total_packets']} | {fmt(r['time_s'])} | {fmt(r['peak_mem_mib'])} | {fmt(r['output_mib'])} |")
    md_path = OUT / 'scalability_summary.md'
    md_path.write_text('\n'.join(md) + '\n', encoding='utf-8')

def load_rows_from_csv(csv_path: Path) -> list[dict]:
    rows: list[dict] = []
    with csv_path.open('r', encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            rows.append({'mode': r['mode'], 'pattern': r['pattern'], 'N': int(r['N']), 'count': int(r['count']), 'total_packets': int(float(r['total_packets'])), 'time_s': float(r['time_s']), 'peak_mem_mib': float(r['peak_mem_mib']), 'output_mib': float(r['output_mib']), 'lines': int(float(r['lines'])), 'repeats': int(float(r.get('repeats', REPEATS)))})
    return rows

def make_plots(rows: list[dict]) -> None:
    plot_pairs_time_vs_count(rows, n_fixed=1024)
    plot_pairs_time_vs_n(rows, count_fixed=1000000)
    plot_pairs_mem_vs_count(rows, n_fixed=1024)
    plot_timed_time_vs_total(rows)

def main() -> None:
    if '--plots-only' in sys.argv:
        csv_path = OUT / 'scalability_results.csv'
        rows = load_rows_from_csv(csv_path)
        make_plots(rows)
        return
    np.random.seed(0)
    random.seed(0)
    rows: list[dict] = []
    with tempfile.TemporaryDirectory(prefix='nocstg_pairs_') as td:
        work = Path(td)
        for pname in PATTERNS:
            for n in PAIR_SIZES:
                for count in PAIR_COUNTS:
                    row = median_run(bench_pairs, pname, n, count, work)
                    rows.append(row)
    with tempfile.TemporaryDirectory(prefix='nocstg_timed_') as td:
        work = Path(td)
        for pname in TIMED_PATTERNS:
            for n in TIMED_SIZES:
                for count in TIMED_COUNTS_PER_PE:
                    row = median_run(bench_timed, pname, n, count, work)
                    rows.append(row)
    write_summary(rows)
    make_plots(rows)
if __name__ == '__main__':
    main()
