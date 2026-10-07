# NoCSTG scalability across traffic-pattern classes

Median of 3 runs. Peak memory via `tracemalloc`.

Patterns compared:
- **neighbor** — neighbor traffic;
- **bitReverse** — bit-permutation (power-of-two $N$);
- **tornado** — tornado traffic;
- **random** — random uniform (stochastic);
- **allToOne** — all-to-one broadcast (hotspot node 0).

## Pair generation (`generatePacketsPairs`)

| Pattern | N | Packets | Time (s) | Peak mem (MiB) | Output (MiB) |
|---|---:|---:|---:|---:|---:|
| neighbor | 16 | 10000 | 0.02429 | 0.6398 | 0.05484 |
| neighbor | 16 | 100000 | 0.2449 | 6.344 | 0.5484 |
| neighbor | 16 | 1000000 | 2.624 | 63.848 | 5.484 |
| neighbor | 64 | 10000 | 0.02478 | 0.6673 | 0.06377 |
| neighbor | 64 | 100000 | 0.2515 | 6.618 | 0.6378 |
| neighbor | 64 | 1000000 | 2.595 | 65.636 | 6.378 |
| neighbor | 256 | 10000 | 0.02595 | 0.6949 | 0.07761 |
| neighbor | 256 | 100000 | 0.2561 | 6.895 | 0.7763 |
| neighbor | 256 | 1000000 | 2.645 | 69.361 | 7.763 |
| neighbor | 1024 | 10000 | 0.03088 | 0.7549 | 0.08418 |
| neighbor | 1024 | 100000 | 0.2639 | 7.073 | 0.8422 |
| neighbor | 1024 | 1000000 | 2.674 | 70.727 | 8.423 |
| neighbor | 4096 | 10000 | 0.04713 | 1.074 | 0.09868 |
| neighbor | 4096 | 100000 | 0.2825 | 7.681 | 0.9962 |
| neighbor | 4096 | 1000000 | 2.705 | 74.126 | 9.973 |
| bitReverse | 16 | 10000 | 0.02486 | 0.651 | 0.05563 |
| bitReverse | 16 | 100000 | 0.2498 | 6.455 | 0.5563 |
| bitReverse | 16 | 1000000 | 2.615 | 64.961 | 5.563 |
| bitReverse | 64 | 10000 | 0.0243 | 0.6671 | 0.06369 |
| bitReverse | 64 | 100000 | 0.2582 | 6.616 | 0.6369 |
| bitReverse | 64 | 1000000 | 2.616 | 66.573 | 6.369 |
| bitReverse | 256 | 10000 | 0.02683 | 0.6949 | 0.07761 |
| bitReverse | 256 | 100000 | 0.2501 | 6.895 | 0.7764 |
| bitReverse | 256 | 1000000 | 2.646 | 69.363 | 7.764 |
| bitReverse | 1024 | 10000 | 0.03645 | 0.7534 | 0.08416 |
| bitReverse | 1024 | 100000 | 0.2631 | 7.072 | 0.8423 |
| bitReverse | 1024 | 1000000 | 2.663 | 70.727 | 8.423 |
| bitReverse | 4096 | 10000 | 0.05948 | 1.068 | 0.0992 |
| bitReverse | 4096 | 100000 | 0.2976 | 7.676 | 0.9972 |
| bitReverse | 4096 | 1000000 | 2.719 | 74.121 | 9.974 |
| tornado | 16 | 10000 | 0.02471 | 0.6398 | 0.05484 |
| tornado | 16 | 100000 | 0.2487 | 6.344 | 0.5484 |
| tornado | 16 | 1000000 | 2.618 | 63.848 | 5.484 |
| tornado | 64 | 10000 | 0.02619 | 0.6673 | 0.06377 |
| tornado | 64 | 100000 | 0.2512 | 6.618 | 0.6378 |
| tornado | 64 | 1000000 | 2.596 | 65.636 | 6.378 |
| tornado | 256 | 10000 | 0.02517 | 0.695 | 0.07762 |
| tornado | 256 | 100000 | 0.2524 | 6.895 | 0.7764 |
| tornado | 256 | 1000000 | 2.646 | 69.361 | 7.763 |
| tornado | 1024 | 10000 | 0.02911 | 0.7549 | 0.08417 |
| tornado | 1024 | 100000 | 0.2586 | 7.073 | 0.8422 |
| tornado | 1024 | 1000000 | 2.698 | 70.727 | 8.423 |
| tornado | 4096 | 10000 | 0.04664 | 1.076 | 0.09961 |
| tornado | 4096 | 100000 | 0.2801 | 7.683 | 0.9972 |
| tornado | 4096 | 1000000 | 2.718 | 74.127 | 9.973 |
| random | 16 | 10000 | 0.05417 | 1.072 | 0.05481 |
| random | 16 | 100000 | 0.5596 | 11.578 | 0.5485 |
| random | 16 | 1000000 | 6.214 | 117.58 | 5.484 |
| random | 64 | 10000 | 0.05102 | 1.090 | 0.06377 |
| random | 64 | 100000 | 0.5522 | 11.757 | 0.6377 |
| random | 64 | 1000000 | 6.134 | 119.36 | 6.377 |
| random | 256 | 10000 | 0.05093 | 1.117 | 0.07758 |
| random | 256 | 100000 | 0.5898 | 12.034 | 0.7762 |
| random | 256 | 1000000 | 6.426 | 122.13 | 7.764 |
| random | 1024 | 10000 | 0.07559 | 1.585 | 0.08418 |
| random | 1024 | 100000 | 0.8394 | 16.732 | 0.8422 |
| random | 1024 | 1000000 | 9.326 | 169.14 | 8.423 |
| random | 4096 | 10000 | 0.07608 | 1.728 | 0.09908 |
| random | 4096 | 100000 | 0.8915 | 18.193 | 0.9968 |
| random | 4096 | 1000000 | 9.650 | 183.75 | 9.973 |
| allToOne | 16 | 10000 | 0.02415 | 0.6464 | 0.0515 |
| allToOne | 16 | 100000 | 0.2524 | 6.372 | 0.515 |
| allToOne | 16 | 1000000 | 2.605 | 64.134 | 5.150 |
| allToOne | 64 | 10000 | 0.02596 | 0.6514 | 0.05586 |
| allToOne | 64 | 100000 | 0.2481 | 6.459 | 0.5586 |
| allToOne | 64 | 1000000 | 2.597 | 65.006 | 5.586 |
| allToOne | 256 | 10000 | 0.02751 | 0.6651 | 0.06268 |
| allToOne | 256 | 100000 | 0.2507 | 6.597 | 0.6272 |
| allToOne | 256 | 1000000 | 2.618 | 66.378 | 6.272 |
| allToOne | 1024 | 10000 | 0.02687 | 0.695 | 0.06593 |
| allToOne | 1024 | 100000 | 0.2509 | 6.685 | 0.6597 |
| allToOne | 1024 | 1000000 | 2.594 | 67.053 | 6.597 |
| allToOne | 4096 | 10000 | 0.03358 | 0.9055 | 0.07313 |
| allToOne | 4096 | 100000 | 0.2583 | 7.044 | 0.7365 |
| allToOne | 4096 | 1000000 | 2.628 | 68.805 | 7.371 |

## Timed generation (`generatePacketsTimed`)

| Pattern | N | Packets/PE | Total packets | Time (s) | Peak mem (MiB) | Output (MiB) |
|---|---:|---:|---:|---:|---:|---:|
| neighbor | 16 | 1000 | 16000 | 0.1136 | 0.0885 | 0.1208 |
| neighbor | 16 | 10000 | 160000 | 1.093 | 0.7894 | 1.208 |
| neighbor | 64 | 1000 | 64000 | 0.4482 | 0.09122 | 0.5118 |
| neighbor | 64 | 10000 | 640000 | 4.109 | 0.793 | 5.119 |
| neighbor | 256 | 1000 | 256000 | 1.712 | 0.1017 | 2.225 |
| neighbor | 256 | 10000 | 2560000 | 16.977 | 0.8342 | 22.247 |
| neighbor | 1024 | 1000 | 1024000 | 7.395 | 0.1049 | 9.236 |
| neighbor | 1024 | 10000 | 10240000 | 69.394 | 0.8713 | 92.364 |
| bitReverse | 16 | 1000 | 12000 | 0.08529 | 0.08855 | 0.09102 |
| bitReverse | 16 | 10000 | 120000 | 0.8332 | 0.7893 | 0.9107 |
| bitReverse | 64 | 1000 | 56000 | 0.3964 | 0.09294 | 0.4475 |
| bitReverse | 64 | 10000 | 560000 | 3.839 | 0.7943 | 4.476 |
| bitReverse | 256 | 1000 | 240000 | 1.602 | 0.1053 | 2.086 |
| bitReverse | 256 | 10000 | 2400000 | 15.813 | 0.8363 | 20.859 |
| bitReverse | 1024 | 1000 | 992000 | 7.195 | 0.1092 | 8.948 |
| bitReverse | 1024 | 10000 | 9920000 | 69.847 | 0.8804 | 89.479 |
| tornado | 16 | 1000 | 16000 | 0.1107 | 0.08854 | 0.1209 |
| tornado | 16 | 10000 | 160000 | 1.102 | 0.7896 | 1.208 |
| tornado | 64 | 1000 | 64000 | 0.4513 | 0.09332 | 0.5121 |
| tornado | 64 | 10000 | 640000 | 4.452 | 0.794 | 5.118 |
| tornado | 256 | 1000 | 256000 | 1.720 | 0.1013 | 2.225 |
| tornado | 256 | 10000 | 2560000 | 17.888 | 0.8352 | 22.247 |
| tornado | 1024 | 1000 | 1024000 | 7.296 | 0.1017 | 9.236 |
| tornado | 1024 | 10000 | 10240000 | 71.583 | 0.8651 | 92.366 |
| random | 16 | 1000 | 16000 | 0.1214 | 0.08572 | 0.1209 |
| random | 16 | 10000 | 160000 | 1.171 | 0.7663 | 1.208 |
| random | 64 | 1000 | 64000 | 0.4921 | 0.09031 | 0.5119 |
| random | 64 | 10000 | 640000 | 4.721 | 0.7883 | 5.118 |
| random | 256 | 1000 | 256000 | 1.900 | 0.09518 | 2.225 |
| random | 256 | 10000 | 2560000 | 20.017 | 0.8222 | 22.247 |
| random | 1024 | 1000 | 1024000 | 9.349 | 0.09543 | 9.236 |
| random | 1024 | 10000 | 10240000 | 98.809 | 0.8343 | 92.363 |
| allToOne | 16 | 1000 | 15000 | 0.1051 | 0.08401 | 0.108 |
| allToOne | 16 | 10000 | 150000 | 1.056 | 0.7505 | 1.079 |
| allToOne | 64 | 1000 | 63000 | 0.4482 | 0.08373 | 0.4531 |
| allToOne | 64 | 10000 | 630000 | 4.296 | 0.7505 | 4.531 |
| allToOne | 256 | 1000 | 255000 | 1.900 | 0.08377 | 1.834 |
| allToOne | 256 | 10000 | 2550000 | 18.447 | 0.7505 | 18.341 |
| allToOne | 1024 | 1000 | 1023000 | 7.909 | 0.08388 | 7.358 |
| allToOne | 1024 | 10000 | 10230000 | 77.487 | 0.7507 | 73.581 |

## Interpretation for the manuscript

1. **Packet count dominates pair generation.** For a fixed $N$, wall time and peak memory grow approximately linearly with the number of emitted pairs for all five pattern classes (see `pairs_time_vs_count_N1024.png`, `pairs_mem_vs_count_N1024.png`).
2. **Network size has a weak effect on pairs (deterministic patterns).** At $10^6$ packets, increasing $N$ from 16 to 4096 changes runtime only modestly (`pairs_time_vs_N_c1000000.png`) once destinations are tiled from a single period.
3. **Deterministic patterns are cost-equivalent after period tiling.** At $N=1024$, $10^6$ packets, neighbor / bit-reverse / tornado / all-to-one all finish in $\approx 2.6$–$2.7\,\mathrm{s}$ with $\approx 67$–$71\,\mathrm{MiB}$ peak memory. Random uniform is $\approx 3.5\times$ slower ($\approx 9.3\,\mathrm{s}$, $169\,\mathrm{MiB}$) because it cannot reuse a fixed period.
4. **All-to-one broadcast** yields $(N-1)$ valid sources per period; the hotspot PE is silent in timed mode (total lines $(N-1)\times C_{\mathrm{PE}}$).
5. **Timed traces scale with $N \times$ packets/PE and filesystem I/O.** Memory stays low (per-PE buffers, $<1\,\mathrm{MiB}$). At $N=1024$, $10^4$/PE: deterministic patterns $\approx 69$–$77\,\mathrm{s}$; random $\approx 99\,\mathrm{s}$.

## Figures

- `pairs_time_vs_count_N1024.png`
- `pairs_time_vs_N_c1000000.png`
- `pairs_mem_vs_count_N1024.png`
- `timed_time_vs_total_packets.png`

