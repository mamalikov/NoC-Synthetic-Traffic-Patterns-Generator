import matplotlib.pyplot as plt
import os
import numpy as np

# data = {}
# with open("Testing/results/pyocn/injections.json", "r") as fh:
#     data = json.load(fh)
#     data = data["data"]

# (
#     x,
#     uniform,
#     bitComplement,
#     bitReverse,
#     bitRotation,
#     shuffle,
#     transpose,
#     neighbor,
#     tornado,
# ) = ([10, 15, 20, 25, 30, 35, 40], [], [], [], [], [], [], [], [])
# for i in data:
#     for rate in x:
#         if i["topology"] == "cmesh" and i["size"] == 64 and i["injection rate"] == rate:
#             pattern = i["traffic"]
#             if pattern == "urandom":
#                 uniform.append(i["average latency"])
#             elif pattern == "bit-complement":
#                 bitComplement.append(i["average latency"])
#             elif pattern == "bit-reverse":
#                 bitReverse.append(i["average latency"])
#             elif pattern == "bit-rotation":
#                 bitRotation.append(i["average latency"])
#             elif pattern == "shuffle":
#                 shuffle.append(i["average latency"])
#             elif pattern == "transpose":
#                 transpose.append(i["average latency"])
#             elif pattern == "neighbor":
#                 neighbor.append(i["average latency"])
#             elif pattern == "tornado":
#                 tornado.append(i["average latency"])

# y = [
#     uniform,
#     bitComplement,
#     bitReverse,
#     bitRotation,
#     shuffle,
#     transpose,
#     neighbor,
#     tornado,
# ]
# labels = [
#     "Uniform",
#     "Bit-complement",
#     "Bit-reverse",
#     "Bit-rotation",
#     "Shuffle",
#     "Transpose",
#     "Neighbor",
#     "Tornado",
# ]

# for y_arr, label in zip(y, labels):
#     plt.plot(x, y_arr, label=label, marker=".")


# plt.legend()
# plt.xticks(x)
# plt.title("CMesh 8x4x2")
# plt.yscale('log', base=10)
# plt.xlabel('Injection rate')
# plt.ylabel('Средняя задержка (циклов)')
# plt.grid(True)
# plt.show()
def smooth(x_data, y_data, win=4):
    filt = np.ones(win) / win
    mov = win // 2
    return x_data[mov:-mov], np.convolve(y_data, filt, mode="same")[mov:-mov]


x = [i / 1000 * 64 for i in range(10, 501)]
labels = [
    "uniform",
    "bitcomplement",
    "bitreverse",
    "bitrotation",
    "shuffle",
    "transpose",
    "tornado",
    "neighbor",
]
for label in labels:
    y = []
    y_res = []
    y_arr = []
    files = []
    for file in os.listdir("Testing/results/noxim/packets_count"):
        if label in file:
            files.append(file)
    for file in files:
        with open("Testing/results/noxim/packets_count/" + file, "r", encoding="utf-8") as f:
            for line in f:
                if "Network throughput" in line:
                    y.append(
                        [
                            int(file.split("_")[-1].split(".")[0][1:]),
                            float(line.split()[-1]),
                        ]
                    )
                    break
    for val in x:
        for data in y:
            if data[0] == val / 64 * 1000:
                y_res.append(data[1])
                break
    y_arr.append(y_res)

    X, Y = smooth(x, y_arr[0], 20)
    X, Y = smooth(X, Y, 20)
    plt.plot(X, Y, label=label)
# mx_y = max(Y)
# mx_x = X[np.where(Y == mx_y)[0][0]]


# for y, label in zip(y_arr, labels):
#     X, Y = smooth(x, y, 30)
#     plt.plot(X, Y, label=label)

for x, y in zip(X, Y):
    if y < x:
        mx_x = x
        mx_y = y
        break

# grad = np.gradient(Y)
# res = {i: grad[i] for i in range(len(grad))}
# res = sorted(res.items(), key=lambda item: item[1])
# c = 0
# min_idx = 0
# for key, val in res:
#     if val > 0:
#         c += 1
#         if c == 4:
#             min_idx = key
#             break

# Поиск точки насыщения (по производной)
# dy = np.gradient(Y)
# threshold = 0.01
# saturation_idx = np.where((dy < threshold) & (Y > 0.98 * max(Y)))[0][0]
# mx_x_2 = X[saturation_idx]
# mx_y_2 = Y[saturation_idx]

# for i in range(len(Y) - 50):
#     if i < len(Y) - 200:
#         if Y[i + 20] <= Y[i] and Y[i + 50] <= Y[i] and Y[i + 200] <= Y[i]:
#             mx_x_2 = X[i]
#             mx_y_2 = Y[i]
#             break
#     else:
#         if Y[i + 20] <= Y[i] and Y[i + 50] <= Y[i]:
#             mx_x_2 = X[i]
#             mx_y_2 = Y[i]
#             break

plt.legend()
plt.title("Зависимость пропускной способности сети от скорости генерации пакетов")
plt.xlabel("Скорость генерации (флит/цикл)")
plt.ylabel("Пропускная способность сети (флит/цикл)")
plt.grid(True)

arrowprops = {
    "arrowstyle": "->",
}
# plt.annotate(
#     "Максимум",
#     xy=(mx_x, round(mx_y, 2)),
#     xytext=(mx_x - 130, mx_y - 2.5),
#     arrowprops=arrowprops,
# )
# plt.annotate(
#     f"({round(mx_x, 2)};{round(mx_y, 2)})", xy=(round(mx_x, 2) + 0.5, round(mx_y, 2))
# )
# plt.annotate(
#     f"({round(mx_x_2, 2)};{round(mx_y_2, 2)})",
#     xy=(round(mx_x_2, 2) + 0.3, round(mx_y_2, 2) - 0.3),
# )

# plt.scatter(mx_x, mx_y, color="red", s=15, marker="o")
# plt.scatter(mx_x_2, mx_y_2, color="red", s=15, marker="o")
# plt.yticks(list(plt.yticks()[0][:-2]) + [round(mx_y, 2)])
plt.show()
