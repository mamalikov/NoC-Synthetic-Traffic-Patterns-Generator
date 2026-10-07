# NoCSTG — NoC Synthetic Traffic Patterns Generator

Python library for generating canonical synthetic traffic patterns for Networks-on-Chip (NoCs), with integration hooks used in Noxim and PyOCN experiments.

## Features

- Spatial patterns: uniform, bit-reverse, bit-complement, bit-rotation, shuffle, transpose, neighbor, tornado, broadcast
- Mesh visualization of source–destination maps
- Table export (`src dst`) for simulators
- Timed per-node export (`dst delay`) for simulators

## Repository layout

| Path | Contents |
|------|----------|
| `patterns.py` | NoCSTG library |
| `tests/` | Unit tests for patterns and exporters |
| `Testing/results/` | Current paper results (PyOCN, Noxim 8×8, NoCSTG scalability, figures) |
| `experiments/` | Scripts to reproduce the paper experiments and plots |
| `noxim/` | Modified Noxim used in the study |
| `PyOCN/` | Modified PyOCN (`pymtl3-net`) with NoCSTG integration |

## Install

```bash
pip install -r requirements.txt
```

## Quick start

```python
from patterns import neighbor, generatePacketsPairs, graph

print(neighbor(0, 16))
generatePacketsPairs(neighbor, 16, 100, outfilename="pairs.txt", random_order=False)
graph(4, 4, pattern=neighbor, label="Neighbor 4x4")
```

## Tests

```bash
python -m unittest discover -s tests -v
```
