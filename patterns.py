import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random


def arrow(startNum, endNum, cols, ax, color="orange"):
    x1 = (startNum) % cols + 0.5
    y1 = (startNum) // cols + 0.5
    x2 = (endNum) % cols + 0.5
    y2 = (endNum) // cols + 0.5
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops={
            "arrowstyle": "-|>",
            "color": color,
            "lw": 1.5,
            "mutation_scale": 10,
            "connectionstyle": "angle3",
        },
        zorder=6,
    )


def uniform(src, n):
    dst = src
    while dst == src:
        dst = random.randint(0, n - 1)
    return dst


def bitReverse(src, n, allow_self=False):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[b - digit - 1]
    dst = int(dst, 2) % n
    if allow_self or src_start != dst:
        return dst
    return -1


def bitComplement(src, n, allow_self=False):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        if src[digit] == "0":
            dst += "1"
        else:
            dst += "0"
    dst = int(dst, 2) % n
    if allow_self or src_start != dst:
        return dst
    return -1


def bitRotation(src, n, allow_self=False):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[(digit + 1) % b]
    dst = int(dst, 2) % n
    if allow_self or src_start != dst:
        return dst
    return -1


def shuffle(src, n, allow_self=False):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[(digit - 1) % b]
    dst = int(dst, 2) % n
    if allow_self or src_start != dst:
        return dst
    return -1


def transpose(src, n, allow_self=False):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[(digit + round(b / 2)) % b]
    dst = int(dst, 2) % n
    if allow_self or src_start != dst:
        return dst
    return -1


def _infer_k_ndim(N, k=None, ndim=None):
    if N <= 0:
        raise ValueError(f"N must be positive, got {N}")
    if k is not None and ndim is not None:
        if k**ndim != N:
            raise ValueError(f"N={N} is not a {k}-ary {ndim}-cube (k**ndim={k**ndim})")
        return int(k), int(ndim)
    if k is not None:
        if k <= 1 or N % k != 0:
            raise ValueError(f"Cannot factor N={N} as k={k}**ndim")
        rem, dims = N, 0
        while rem > 1:
            if rem % k != 0:
                raise ValueError(f"Cannot factor N={N} as k={k}**ndim")
            rem //= k
            dims += 1
        return int(k), dims
    if ndim is not None:
        if ndim <= 0:
            raise ValueError(f"ndim must be positive, got {ndim}")
        root = int(round(N ** (1.0 / ndim)))
        if root**ndim != N:
            raise ValueError(f"N={N} is not a perfect {ndim}-D hypercube")
        return root, int(ndim)
    root2 = int(round(math.sqrt(N)))
    if root2 * root2 == N:
        return root2, 2
    root3 = int(round(N ** (1.0 / 3.0)))
    if root3**3 == N:
        return root3, 3
    return int(N), 1


def _id_to_digits(src, k, ndim):
    digits = []
    x = int(src)
    for _ in range(ndim):
        digits.append(x % k)
        x //= k
    return digits


def _digits_to_id(digits, k):
    dest, mul = 0, 1
    for d in digits:
        dest += int(d) * mul
        mul *= k
    return dest


def tornado(src, n, k=None, ndim=None, allow_self=False):
    kk, nd = _infer_k_ndim(n, k, ndim)
    offset = math.ceil(kk / 2) - 1
    digits = _id_to_digits(src, kk, nd)
    dst = _digits_to_id([(d + offset) % kk for d in digits], kk)
    if allow_self or src != dst:
        return dst
    return -1


def neighbor(src, n, k=None, ndim=None, allow_self=False):
    kk, nd = _infer_k_ndim(n, k, ndim)
    digits = _id_to_digits(src, kk, nd)
    dst = _digits_to_id([(d + 1) % kk for d in digits], kk)
    if allow_self or src != dst:
        return dst
    return -1


def broadcast(src, n, hotspot=-1, direction="in"):
    if hotspot == -1:
        return [i for i in range(n) if i != src]
    if direction == "in" and src != hotspot:
        return hotspot
    if direction != "in" and src == hotspot:
        return [i for i in range(n) if i != src]


def graph(rows, cols, pattern=uniform, hotspot=None, direction="in", label="", outfile=None):
    n = rows * cols
    side = max(6.0, 0.7 * max(rows, cols))
    fig, ax = plt.subplots(figsize=(side, side))
    fs = 14 if max(rows, cols) <= 4 else (11 if max(rows, cols) <= 6 else 8)

    for i in range(rows):
        for j in range(cols):
            x, y = j, rows - i - 1
            rect = patches.Rectangle(
                (x, y),
                1,
                1,
                edgecolor="black",
                facecolor="#fafafa",
                linewidth=1.2,
                zorder=1,
            )
            ax.add_patch(rect)

    edges = []
    if hotspot is None:
        for src in range(n):
            dst = pattern(src, n)
            if isinstance(dst, (list, tuple)):
                for d in dst:
                    if d is not None and d != -1:
                        edges.append((src, d))
            elif dst is not None and dst != -1:
                edges.append((src, dst))
    else:
        for src in range(n):
            dst = pattern(src, n, hotspot, direction)
            if isinstance(dst, (list, tuple)):
                for d in dst:
                    if d is not None and d != -1:
                        edges.append((src, d))
            elif dst is not None and dst != -1:
                edges.append((src, dst))

    for i in range(rows):
        for j in range(cols):
            x, y = j, rows - i - 1
            num = rows * cols - cols + j - i * cols
            ax.text(
                x + 0.5,
                y + 0.5,
                str(num),
                ha="center",
                va="center",
                fontsize=fs,
                color="black",
                zorder=3,
            )

    palette = ("red", "blue", "green", "orange")
    for src, dst in edges:
        color = palette[(src % cols) % len(palette)]
        arrow(src, dst, cols, ax, color=color)

    if label:
        plt.title(label)
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    if outfile:
        fig.savefig(outfile, dpi=200, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


def _sample_delay(distribution, mean, scale, lam):
    if distribution == "normal":
        return float(np.random.normal(mean, scale))
    if distribution == "poisson":
        return float(np.random.poisson(lam))
    raise ValueError(f"Unknown distribution: {distribution}")


def _normalize_dests(dst):
    if dst is None or dst == -1:
        return None
    if isinstance(dst, (list, tuple)):
        dests = [d for d in dst if d is not None and d != -1]
        return dests or None
    return [dst]


def _pattern_is_stochastic(pattern, N, hotspot=None, direction="in", probes=8):
    if hotspot is not None:
        return False
    state = random.getstate()
    try:
        for src in range(min(N, probes)):
            a = pattern(src, N)
            b = pattern(src, N)
            if a != b:
                return True
    finally:
        random.setstate(state)
    return False


def _pair_period(pattern, N, hotspot=None, direction="in"):
    period = []
    for src in range(N):
        if hotspot is None:
            dst = pattern(src, N)
            if isinstance(dst, (list, tuple)):
                period.extend((src, d) for d in dst if d is not None and d != -1)
            elif dst is not None and dst != -1:
                period.append((src, dst))
        elif direction == "in":
            if src != hotspot:
                period.append((src, hotspot))
        else:
            if src != hotspot:
                period.append((hotspot, src))
    return period


def _tile_pairs(period, count):
    n = len(period)
    if n == 0:
        raise ValueError("Pattern produced no valid source-destination pairs")
    reps, rem = divmod(count, n)
    if reps == 0:
        return period[:count]
    pairs = period * reps
    if rem:
        pairs.extend(period[:rem])
    return pairs


def _generate_pairs_stream(pattern, N, count, hotspot=None, direction="in"):
    pairs = []
    i = 0
    attempts = 0
    max_attempts = max(count * max(N, 1) * 4, count + N)

    def _append_dest(src, dst) -> None:
        if isinstance(dst, (list, tuple)):
            for d in dst:
                if len(pairs) >= count:
                    return
                if d == -1 or d is None:
                    continue
                pairs.append((src, d))
        elif dst != -1 and dst is not None:
            pairs.append((src, dst))

    while len(pairs) < count:
        if attempts >= max_attempts:
            raise ValueError(
                f"Could not generate {count} valid pairs for the given pattern "
                f"(got {len(pairs)} after {attempts} attempts)"
            )
        src = i % N
        i += 1
        attempts += 1
        if hotspot is None:
            _append_dest(src, pattern(src, N))
        elif direction == "in":
            if src != hotspot:
                pairs.append((src, hotspot))
        elif src != hotspot:
            pairs.append((hotspot, src))
    del pairs[count:]
    return pairs


def generatePacketsTimed(
    pattern,
    N,
    count,
    distribution="normal",
    mean=10,
    scale=1,
    lam=10,
    output_dir="result",
    hotspot=None,
    direction="in",
):
    stochastic = _pattern_is_stochastic(pattern, N, hotspot, direction)
    for i in range(N):
        lines = []
        if stochastic:
            while len(lines) < count:
                dst = (
                    pattern(i, N)
                    if hotspot is None
                    else pattern(i, N, hotspot, direction)
                )
                dests = _normalize_dests(dst)
                if dests is None:
                    break
                for d in dests:
                    if len(lines) >= count:
                        break
                    delay = _sample_delay(distribution, mean, scale, lam)
                    lines.append(f"{d} {round(delay, 1)}\n")
        else:
            dst = (
                pattern(i, N)
                if hotspot is None
                else pattern(i, N, hotspot, direction)
            )
            dests = _normalize_dests(dst)
            if dests is not None:
                n_dest = len(dests)
                for k in range(count):
                    delay = _sample_delay(distribution, mean, scale, lam)
                    lines.append(f"{dests[k % n_dest]} {round(delay, 1)}\n")
        with open(output_dir + "/" + str(i) + ".txt", "w+") as f:
            f.write("".join(lines))


def generatePacketsPairs(
    pattern,
    N,
    count,
    hotspot=None,
    direction="in",
    outfilename="result/generation.txt",
    random_order=True,
):
    if hotspot is not None or not _pattern_is_stochastic(pattern, N):
        pairs = _tile_pairs(_pair_period(pattern, N, hotspot, direction), count)
    else:
        pairs = _generate_pairs_stream(pattern, N, count, hotspot, direction)
    if random_order:
        random.shuffle(pairs)
    res = "".join(f"{src} {dst}\n" for src, dst in pairs)
    with open(outfilename, "w+") as f:
        f.write(res)
