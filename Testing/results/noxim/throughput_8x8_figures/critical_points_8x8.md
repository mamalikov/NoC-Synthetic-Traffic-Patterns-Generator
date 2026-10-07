# Critical points (8x8 mesh, mean of 10 seeds, smoothed)

Breakpoint: first point where local slope dY/dX drops below 1.
Saturation: leftmost point with Y ≥ 97% of max Y.

Table values are **throughput** (flit/cycle), matching Table 2 style.

| Traffic pattern | Breakpoint thr (flit/cycle) | Saturation thr (flit/cycle) |
|---|---:|---:|
| Neighbor | 30.162 | 31.070 |
| Bit-rotation | 5.911 | 10.119 |
| Shuffle | 5.093 | 9.707 |
| Random uniform | 5.012 | 8.593 |
| Transpose | 4.200 | 6.799 |
| Tornado | 5.438 | 6.226 |
| Bit-complement | 5.082 | 5.240 |
| Bit-reverse | 4.165 | 5.019 |
