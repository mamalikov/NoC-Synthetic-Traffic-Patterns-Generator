import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random


def arrow(startNum, endNum, cols, ax):
    x1 = (startNum) % cols + 0.5
    y1 = (startNum) // cols + 0.5
    x2 = (endNum) % cols + 0.5
    y2 = (endNum) // cols + 0.5
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops={
            "facecolor": "orange",
            "width": 2,
            "headwidth": 7,
            "connectionstyle": "angle3",
        },
    )


def uniform(src, n):
    dst = src
    while dst == src:
        dst = random.randint(0, n - 1)
    # print(
    #     f"Random uniform pattern. \nCores count: {n}. Source: {bin(src)}, Destination: {bin(dst)}\n"
    # )
    return dst


def bitReverse(src, n):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[b - digit - 1]
    dst = int(dst, 2)
    if src_start != (dst % n):
        # print(
        #     f"Bit-reverse pattern. d[i] = S[b-i-1] \nCores count: {n}. Source: {bin(src_start)}, Destination: {bin(dst%n)}\n"
        # )
        return dst % n
    return -1


def bitComplement(src, n):
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        if src[digit] == "0":
            dst += "1"
        else:
            dst += "0"
    dst = int(dst, 2)
    # print(
    #     f"Bit-complement pattern. d[i] = ¬S[i] \nCores count: {n}. Source: 0b{src}, Destination: {bin(dst)}\n"
    # )
    return dst


def bitRotation(src, n):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[(digit + 1) % b]
    dst = int(dst, 2)
    if src_start != (dst % n):
        # print(
        #     f"Bit-rotation pattern. d[i] = S[(i+1) mod b] \nCores count: {n}. Source: {bin(src_start)}, Destination: {bin(dst%n)}\n"
        # )
        return dst % n
    return -1


def shuffle(src, n):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[(digit - 1) % b]
    dst = int(dst, 2)
    if src_start != (dst % n):
        # print(
        #     f"Shuffle pattern. d[i] = S[(i-1) mod b] \nCores count: {n}. Source: {bin(src_start)}, Destination: {bin(dst%n)}\n"
        # )
        return dst % n
    return -1


def transpose(src, n):
    src_start = src
    b = len(bin(n - 1)[2:])
    dst = ""
    src = bin(src)[2:]
    src = "0" * (b - len(src)) + src
    for digit in range(b):
        dst += src[(digit + round(b / 2)) % b]
    dst = int(dst, 2)
    if src_start != (dst % n):
        print(
            f"Transpose pattern. d[i] = S[(i+b/2) mod b] \nCores count: {n}. Source: {bin(src_start)}, Destination: {bin(dst%n)}\n"
        )
        return dst % n
    return -1


def tornado(src, n):
    dst = (src + (n // 2) - 1) % n
    # print(
    #     f"Tornado pattern. d[x] = (S[x] + k/2 - 1) mod k \nCores count: {n}. Source: {src}, Destination: {dst}\n"
    # )
    return dst


def neighbor(src, n):
    dst = (src + 1) % n
    # print(
    #     f"Neighbor pattern. d[x] = (S[x] + 1) mod k \nCores count: {n}. Source: {src}, Destination: {dst}\n"
    # )
    return dst


def broadcast(src, n, hotspot=-1, direction="in"):
    if hotspot == -1:
        return [i for i in range(n) if i != src]
    else:
        if direction == "in" and src != hotspot:
            return hotspot
        else:
            if direction != "in" and src == hotspot:
                return [i for i in range(n) if i != src]


def graph(rows, cols, pattern=uniform, hotspot=None, direction="in", label=""):
    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(6, 6))

    # Рисуем квадраты и номера
    for i in range(rows):
        for j in range(cols):
            x, y = j, rows - i - 1
            rect = patches.Rectangle(
                (x, y), 1, 1, edgecolor="black", facecolor="white", linewidth=2
            )
            ax.add_patch(rect)
            # Номер внутри квадрата
            num = rows * cols - cols + j - i * cols
            ax.text(
                x + 0.5,
                y + 0.5,
                str(num),
                ha="center",
                va="center",
                fontsize=14,
                color="black",
            )

    # Заполняем стрелки нужным образом
    if hotspot is None:
        # Не broadcast
        for i in range(0, rows * cols):
            dst = pattern(i, rows * cols)
            if dst != -1:
                arrow(i, dst, cols, ax)
        plt.title(label)
    else:
        # broadcast
        for i in range(0, rows * cols):
            dst = pattern(i, rows * cols, hotspot, direction)
            if type(dst) == list:
                for j in dst:
                    arrow(i, j, cols, ax)
            elif dst is not None:
                arrow(i, dst, cols, ax)

    plt.title(label)
    # Устанавливаем ограничения осей и скрываем их
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.axis("off")

    # Показываем рисунок
    plt.show()


def generatePacketsTimed(
    pattern,
    N,
    count,
    distribution="normal",
    mean=10,
    scale=1,
    lam=10,
    output_dir="result",
):
    for i in range(N):
        delays = []
        res = ""
        if distribution == "normal":
            delays = np.random.normal(mean, scale, count)
        elif distribution == "poisson":
            delays = np.random.poisson(lam, count)
        for j in range(count):
            dst = pattern(i, N)
            if dst != -1:
                res += f"{dst} {round(delays[j], 1)}\n"
        with open(output_dir + "/" + str(i) + ".txt", "w+") as f:
            f.write(res)


def generatePacketsPairs(
    pattern,
    N,
    count,
    hotspot=None,
    direction="in",
    outfilename="result/generation.txt",
    random_order=True,
):
    res = ""
    for i in range(count):
        if random_order:
            src = random.randint(0, N - 1)
        else:
            src = i % N
        if hotspot is None:
            dst = pattern(src, N)
            if dst != -1:
                res += f"{src} {dst}\n"
        else:
            if direction == "in":
                res += f"{src} {hotspot}\n"
            else:
                res += f"{hotspot} {src}\n"
    with open(outfilename, "w+") as f:
        f.write(res)


# Размеры сети
rows, cols = 4, 4
# generatePacketsTimed(tornado, rows * cols, 200, distribution="normal")
# Рисуем трафик

# generatePacketsTimed(tornado, rows*cols, count=100, distribution='poisson', lam=0.6)
# uniform, bitcomplement, bitreverse, bitrotation, shuffle, transpose, tornado, neighbor
pattern = "uniform"
for i in range(16, 321):
    generatePacketsPairs(
        uniform,
        rows * cols,
        i,
        outfilename=f"Testing/patterns/noxim/gen_order_testing/{pattern}-{rows}x{cols}-random-n{i}.txt",
    )
    generatePacketsPairs(
        uniform,
        rows * cols,
        i,
        outfilename=f"Testing/patterns/noxim/gen_order_testing/{pattern}-{rows}x{cols}-ordered-n{i}.txt",
        random_order=False,
    )
# graph(rows, cols, pattern=bitReverse, label="Bit-Reverse Pattern")
