#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
import traceback
from argparse import Namespace
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean
ROOT = Path(__file__).resolve().parents[1]
PYOCN = ROOT / 'PyOCN'
OUT = ROOT / 'Testing' / 'results' / 'pyocn'
PATTERNS = ['urandom', 'bit-complement', 'bit-reverse', 'bit-rotation', 'shuffle', 'transpose', 'neighbor', 'tornado']
MESH_GEOM = {16: (4, 4), 32: (4, 8), 64: (8, 8), 128: (8, 16), 256: (16, 16)}
BFLY_NFLY = {16: 4, 32: 5, 64: 6, 128: 7, 256: 8}
CMESH_GEOM = {2: {16: (4, 2), 32: (4, 4), 64: (8, 4), 128: (8, 8), 256: (16, 8)}, 4: {16: (2, 2), 32: (2, 4), 64: (4, 4), 128: (4, 8), 256: (8, 8)}}

def _base_opts(**kwargs) -> Namespace:
    opts = Namespace(ncols=2, nrows=2, kary=2, nfly=2, nterminals=4, nterminals_each=2, channel_lat=0, channel_bw=32, injection_rate=10, pattern='urandom', warmup_ncycles=1000, measure_npackets=100, timeout_ncycles=50000, verbose=False, trace=False, dump_vcd=False, cl=False, sweep=False)
    for k, v in kwargs.items():
        setattr(opts, k, v)
    return opts

def _mesh_job(size: int, pattern: str, inj: int) -> dict:
    ncols, nrows = MESH_GEOM[size]
    return {'topo': 'mesh', 'size': size, 'terminals': None, 'pattern': pattern, 'injection_rate': inj, 'opts': dict(ncols=ncols, nrows=nrows, pattern=pattern, injection_rate=inj)}

def _bfly_job(size: int, pattern: str, inj: int) -> dict:
    return {'topo': 'bfly', 'size': size, 'terminals': None, 'pattern': pattern, 'injection_rate': inj, 'opts': dict(kary=2, nfly=BFLY_NFLY[size], pattern=pattern, injection_rate=inj)}

def _cmesh_job(size: int, terminals: int, pattern: str, inj: int) -> dict:
    ncols, nrows = CMESH_GEOM[terminals][size]
    return {'topo': 'cmesh', 'size': size, 'terminals': terminals, 'pattern': pattern, 'injection_rate': inj, 'opts': dict(ncols=ncols, nrows=nrows, nterminals_each=terminals, pattern=pattern, injection_rate=inj)}

def build_topology_jobs() -> list[dict]:
    jobs = []
    sizes = [16, 32, 64, 128, 256]
    for size in sizes:
        for pat in PATTERNS:
            jobs.append(_mesh_job(size, pat, 10))
            jobs.append(_bfly_job(size, pat, 10))
            jobs.append(_cmesh_job(size, 2, pat, 10))
            jobs.append(_cmesh_job(size, 4, pat, 10))
    return jobs

def build_injection_jobs() -> list[dict]:
    jobs = []
    rates = [10, 15, 20, 25, 30, 35, 40]
    for size in (16, 64):
        for inj in rates:
            for pat in PATTERNS:
                jobs.append(_mesh_job(size, pat, inj))
                jobs.append(_bfly_job(size, pat, inj))
                jobs.append(_cmesh_job(size, 2, pat, inj))
    return jobs

def _run_one(payload: dict) -> dict:
    os.chdir(PYOCN)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if str(PYOCN) not in sys.path:
        sys.path.insert(0, str(PYOCN))
    from random import seed as py_seed
    from pymtl3_net.ocnlib.sim import sim_utils
    sim_utils.write_result_json = False
    sim_utils.verbose = False
    opts = _base_opts(**payload['opts'])
    py_seed(payload['seed'])
    t0 = time.monotonic()
    try:
        result = sim_utils.net_simulate(payload['topo'], opts)
        err = None
        lat = float(result.avg_latency)
        cycles = int(result.sim_ncycles)
        gen = int(result.total_generated)
        recv = int(result.total_received)
        mpkt = int(result.mpkt_received)
        timeout = bool(result.timeout)
        elapsed = float(result.elapsed_time)
    except Exception as exc:
        err = f'{type(exc).__name__}: {exc}'
        lat = float('nan')
        cycles = gen = recv = mpkt = 0
        timeout = True
        elapsed = time.monotonic() - t0
    return {'topology': payload['topo'], 'size': payload['size'], 'terminals': payload['terminals'], 'traffic': payload['pattern'], 'injection rate': payload['injection_rate'], 'seed': payload['seed'], 'average latency': lat, 'simulated cycles': cycles, 'packets generated': gen, 'packets received': recv, '#measure packet': mpkt, 'elapsed time': elapsed, 'timeout': timeout, 'error': err}

def _aggregate(raw: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for r in raw:
        key = (r['topology'], r['size'], r['terminals'], r['traffic'], r['injection rate'])
        groups.setdefault(key, []).append(r)
    out = []
    for key, rows in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 0, kv[0][3], kv[0][4])):
        lats = [r['average latency'] for r in rows if not math.isnan(r['average latency'])]
        rec = {'topology': key[0], 'size': key[1], 'traffic': key[3], 'injection rate': key[4], 'average latency': mean(lats) if lats else float('nan'), 'simulated cycles': mean((r['simulated cycles'] for r in rows)), 'packets generated': mean((r['packets generated'] for r in rows)), 'packets received': mean((r['packets received'] for r in rows)), '#measure packet': mean((r['#measure packet'] for r in rows)), 'elapsed time': mean((r['elapsed time'] for r in rows)), 'n_seeds': len(rows), 'n_ok': len(lats), 'n_timeout': sum((1 for r in rows if r.get('timeout'))), 'latency_std': (sum(((x - mean(lats)) ** 2 for x in lats)) / len(lats)) ** 0.5 if len(lats) > 1 else 0.0}
        if key[2] is not None:
            rec['terminals'] = key[2]
        out.append(rec)
    return out

def run_campaign(name: str, jobs: list[dict], n_seeds: int, workers: int, seed0: int) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_dir = OUT / f'{name}_raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    tasks = []
    for job in jobs:
        for s in range(1, n_seeds + 1):
            payload = dict(job)
            payload['seed'] = seed0 + s
            tasks.append(payload)
    raw_path = raw_dir / 'all_runs.jsonl'
    done: set[tuple] = set()
    existing: list[dict] = []
    if raw_path.exists():
        with raw_path.open(encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                existing.append(r)
                done.add((r['topology'], r['size'], r['terminals'], r['traffic'], r['injection rate'], r['seed']))
    pending = [t for t in tasks if (t['topo'], t['size'], t['terminals'], t['pattern'], t['injection_rate'], t['seed']) not in done]
    t_start = time.monotonic()
    finished = 0
    with raw_path.open('a', encoding='utf-8') as out_fh:
        if workers <= 1:
            for payload in pending:
                rec = _run_one(payload)
                out_fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
                out_fh.flush()
                existing.append(rec)
                finished += 1
                if finished % 5 == 0 or finished == len(pending):
                    dt = time.monotonic() - t_start
        else:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                futs = {ex.submit(_run_one, p): p for p in pending}
                for fut in as_completed(futs):
                    rec = fut.result()
                    out_fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
                    out_fh.flush()
                    existing.append(rec)
                    finished += 1
                    if finished % 10 == 0 or finished == len(pending):
                        dt = time.monotonic() - t_start
    aggregated = _aggregate(existing)
    out_json = OUT / f'{name}.json'
    out_json.write_text(json.dumps({'data': aggregated, 'n_seeds': n_seeds, 'seed0': seed0}, indent=4), encoding='utf-8')
    return out_json

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--campaign', choices=('topologies', 'injections', 'both', 'smoke'), default='both')
    ap.add_argument('--seeds', type=int, default=10)
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 4) // 2))
    ap.add_argument('--seed0', type=int, default=1000)
    args = ap.parse_args()
    os.chdir(PYOCN)
    if args.campaign == 'smoke':
        jobs = [_mesh_job(16, 'urandom', 10), _mesh_job(16, 'bit-reverse', 10), _mesh_job(16, 'neighbor', 10)]
        run_campaign('smoke', jobs, n_seeds=min(2, args.seeds), workers=1, seed0=args.seed0)
        return
    if args.campaign in ('topologies', 'both'):
        run_campaign('topologies', build_topology_jobs(), n_seeds=args.seeds, workers=args.workers, seed0=args.seed0)
    if args.campaign in ('injections', 'both'):
        run_campaign('injections', build_injection_jobs(), n_seeds=args.seeds, workers=args.workers, seed0=args.seed0 + 10000)
if __name__ == '__main__':
    main()
