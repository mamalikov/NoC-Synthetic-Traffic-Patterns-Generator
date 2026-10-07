#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'Testing' / 'results' / 'pyocn' / 'injections.json'
OUT = ROOT / 'Testing' / 'results' / 'pyocn' / 'figures_generation_speed'
PAPER = ROOT / 'Testing' / 'results' / 'paper_figures'
PATTERN_ORDER = ['urandom', 'bit-complement', 'bit-reverse', 'bit-rotation', 'shuffle', 'transpose', 'neighbor', 'tornado']
PATTERN_LABELS = {'urandom': 'Uniform', 'bit-complement': 'Bit-complement', 'bit-reverse': 'Bit-reverse', 'bit-rotation': 'Bit-rotation', 'shuffle': 'Shuffle', 'transpose': 'Transpose', 'neighbor': 'Neighbor', 'tornado': 'Tornado'}
TITLE = {('mesh', 16): 'Mesh 4x4', ('mesh', 64): 'Mesh 8x8', ('cmesh', 16): 'CMesh 4x2x2', ('cmesh', 64): 'CMesh 8x4x2', ('bfly', 16): 'Butterfly N=16', ('bfly', 64): 'Butterfly N=64'}
PANEL_STYLE_OVERRIDES: dict[tuple[str, int], dict[str, dict[str, object]]] = {('bfly', 16): {'bit-complement': {'marker': '+', 'markersize': 9, 'linestyle': '--'}, 'neighbor': {'marker': 's', 'markersize': 7, 'linestyle': '-'}, 'tornado': {'marker': 'x', 'markersize': 9, 'linestyle': '-.'}}}
PAPER_NAME = {('bfly', 16): 'fig20a_latency_vs_gen_speed_bfly_16.png', ('bfly', 64): 'fig20b_latency_vs_gen_speed_bfly_64.png', ('mesh', 16): 'fig21a_latency_vs_gen_speed_mesh_16.png', ('mesh', 64): 'fig21b_latency_vs_gen_speed_mesh_64.png', ('cmesh', 16): 'fig22a_latency_vs_gen_speed_cmesh_16.png', ('cmesh', 64): 'fig22b_latency_vs_gen_speed_cmesh_64.png'}

def gen_speed(n_nodes: int, inj_percent: float) -> float:
    return n_nodes * (inj_percent / 100.0)

def _panel_x_ticks(grouped: dict, topo: str, size: int) -> list[float]:
    for pat in PATTERN_ORDER:
        series = _sorted_series(grouped, topo, size, pat)
        if series:
            return [gen_speed(size, inj) for inj, _ in series]
    return []

def _gen_speed_tick_label(x: float, _pos=None) -> str:
    if abs(x - round(x)) < 1e-06:
        return str(int(round(x)))
    text = f'{x:.1f}'
    if text.endswith('.0'):
        return text[:-2]
    return text

def apply_x_at_datapoints(ax, xs: list[float]) -> None:
    if not xs:
        return
    pad = (max(xs) - min(xs)) * 0.04 or 0.2
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.xaxis.set_major_locator(FixedLocator(xs))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(_gen_speed_tick_label))

def _sorted_series(grouped: dict, topo: str, size: int, pat: str) -> list[tuple[float, float]] | None:
    series = grouped.get((topo, size, pat))
    if not series:
        return None
    return sorted(series, key=lambda p: p[0])

def _latencies_match(a: list[tuple[float, float]], b: list[tuple[float, float]], tol: float=0.001) -> bool:
    if len(a) != len(b):
        return False
    return all((abs(x[1] - y[1]) <= tol for x, y in zip(a, b)))
OVERLAP_MARKER: dict[str, tuple[str, float]] = {'neighbor': ('s', 8), 'tornado': ('x', 8), 'bit-complement': ('+', 8)}
_FALLBACK_OVERLAP_MARKERS = [('D', 8), ('v', 8), ('^', 8), ('P', 8)]

def _overlap_groups(grouped: dict, topo: str, size: int, tol: float=0.001) -> list[list[str]]:
    pats = [p for p in PATTERN_ORDER if _sorted_series(grouped, topo, size, p)]
    parent = {p: p for p in pats}

    def find(p: str) -> str:
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def union(a: str, b: str) -> None:
        ra, rb = (find(a), find(b))
        if ra != rb:
            parent[rb] = ra
    for i, p in enumerate(pats):
        sp = _sorted_series(grouped, topo, size, p)
        for q in pats[i + 1:]:
            sq = _sorted_series(grouped, topo, size, q)
            if _latencies_match(sp, sq, tol):
                union(p, q)
    clusters: dict[str, list[str]] = defaultdict(list)
    for p in pats:
        clusters[find(p)].append(p)
    return [sorted(g, key=lambda x: PATTERN_ORDER.index(x)) for g in clusters.values() if len(g) > 1]

def _line_style(pat: str, topo: str, size: int, overlap_groups: list[list[str]]) -> tuple[str, float, str]:
    panel = PANEL_STYLE_OVERRIDES.get((topo, size), {}).get(pat)
    if panel:
        return (str(panel['marker']), float(panel['markersize']), str(panel.get('linestyle', '-')))
    in_group = next((g for g in overlap_groups if pat in g), None)
    if not in_group:
        return ('.', 6.0, '-')
    if pat in OVERLAP_MARKER:
        m, ms = OVERLAP_MARKER[pat]
        return (m, ms, '-')
    idx = in_group.index(pat)
    used = {p for p in in_group if p in OVERLAP_MARKER}
    fallback_i = idx - sum((1 for p in in_group[:idx] if p in used))
    m, ms = _FALLBACK_OVERLAP_MARKERS[fallback_i % len(_FALLBACK_OVERLAP_MARKERS)]
    return (m, ms, '-')

def main() -> None:
    records = json.loads(DATA.read_text(encoding='utf-8'))['data']
    grouped: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for r in records:
        key = (r['topology'], int(r['size']), r['traffic'])
        grouped[key].append((float(r['injection rate']), float(r['average latency'])))
    configs = sorted({(t, s) for t, s, _ in grouped})
    OUT.mkdir(parents=True, exist_ok=True)
    PAPER.mkdir(parents=True, exist_ok=True)
    for topo, size in configs:
        overlap_groups = _overlap_groups(grouped, topo, size)
        fig, ax = plt.subplots(figsize=(6, 6))
        final_by_pat: dict[str, float] = {}
        for pat in PATTERN_ORDER:
            series = _sorted_series(grouped, topo, size, pat)
            if not series:
                continue
            xs = [gen_speed(size, inj) for inj, _ in series]
            ys = [lat for _, lat in series]
            final_by_pat[pat] = ys[-1]
            marker, msize, linestyle = _line_style(pat, topo, size, overlap_groups)
            ax.plot(xs, ys, marker=marker, markersize=msize, linestyle=linestyle, label=PATTERN_LABELS[pat])
        ranked_pats = sorted(final_by_pat.keys(), key=lambda p: final_by_pat[p], reverse=True)
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend([by_label[PATTERN_LABELS[p]] for p in ranked_pats], [PATTERN_LABELS[p] for p in ranked_pats])
        x_ticks = _panel_x_ticks(grouped, topo, size)
        apply_x_at_datapoints(ax, x_ticks)
        ax.set_xlabel('Generation speed (flit/cycle)')
        ax.set_ylabel('Average latency (cycles)')
        ax.set_title(TITLE.get((topo, size), f'{topo} N={size}'))
        ax.grid(True, linestyle='--', alpha=0.4)
        fig.tight_layout()
        out_path = OUT / f'latency_vs_gen_speed_{topo}_{size}.png'
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        paper_name = PAPER_NAME.get((topo, size))
        if paper_name:
            (PAPER / paper_name).write_bytes(out_path.read_bytes())
        csv_path = OUT / f'latency_vs_gen_speed_{topo}_{size}.csv'
        lines = ['pattern,injection_rate_percent,generation_speed_flit_cycle,average_latency\n']
        for pat in PATTERN_ORDER:
            series = _sorted_series(grouped, topo, size, pat)
            if not series:
                continue
            for inj, lat in series:
                lines.append(f'{pat},{inj:g},{gen_speed(size, inj):.6g},{lat:.6g}\n')
        csv_path.write_text(''.join(lines), encoding='utf-8')
if __name__ == '__main__':
    main()
