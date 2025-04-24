import matplotlib.pyplot as plt
import os
import pandas as pd
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


x = [i / 1000 * 32 for i in range(16, 321)]
# x = [i for i in range(16, 321)]
labels = [
    # "uniform",
    # "bitcomplement",
    # "bitreverse",
    # "bitrotation",
    # "shuffle",
    # "transpose",
    # "tornado",
    # "neighbor",
]
pattern = "uniform"
labels = ["ordered", "random"]
y_arr = []
for label in labels:
    y = []
    y_res = []
    files = []
    for file in os.listdir("Testing/results/noxim/orders_counts_4x4"):
        if label in file and pattern in file:
            files.append(file)
    for file in files:
        with open(
            "Testing/results/noxim/orders_counts_4x4/" + file, "r", encoding="utf-8"
        ) as f:
            for line in f:
                if "Global average delay" in line:
                    y.append(
                        [
                            int(file.split("-")[-1].split(".")[0][1:]),
                            float(line.split()[-1]),
                        ]
                    )
                    break
    for val in x:
        for data in y:
            if data[0] == val * 1000 / 32:
                y_res.append(data[1])
                break
    y_arr.append(y_res)

    # X, Y = smooth(x, y_arr[0], 20)
    # X, Y = smooth(X, Y, 20)
    # plt.plot(X, Y, label=label)
# mx_y = max(Y)
# mx_x = X[np.where(Y == mx_y)[0][0]]

mx_x = 0
mx_y = 0
x_mx = []
y_mx = []
# print(len(y_arr))
for y, label in zip(y_arr, labels):
    X, Y = smooth(x, y, 20)
    X, Y = smooth(X, Y, 20)
    x_mx.append(X)
    y_mx.append(Y)
    if label == "random":
        plt.plot(X, Y, label="Случайный отправитель")
    else:
        plt.plot(X, Y, label="Отправители по порядку")

for i in range(len(y_mx[0])):
    if y_mx[0][i] >= y_mx[1][i]:
        mx_x = x_mx[0][i]
        mx_y = y_mx[0][i]
        break

print(mx_x, mx_y)

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

# # Поиск точки насыщения (по производной)
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
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
plt.yscale("log", base=10)
plt.title(f"Зависимость задержки от порядка генерации пакетов\nТрафик: {pattern}")
plt.xlabel("Скорость генерации пакетов (флит/цикл)")
plt.ylabel("Средняя задержка (циклы)")
plt.grid(True)

# arrowprops = {
#     "arrowstyle": "->",
# }
# plt.annotate(
#     "Максимум",
#     xy=(mx_x, round(mx_y, 2)),
#     xytext=(mx_x - 130, mx_y - 2.5),
#     arrowprops=arrowprops,
# )

plt.annotate(
    f"{round(mx_x, 2)};{round(mx_y, 2)}",
    xy=(round(mx_x, 2) + 0.2, round(mx_y, 2) - 250),
)
# plt.annotate(
#     f"({round(max(max(y_mx[0]), max(y_mx[1])), 2)})",
#     xy=(1.1, round(max(max(y_mx[0]), max(y_mx[1])), 2) - 1000),
# )

plt.scatter(mx_x, mx_y, color="red", s=15, marker="o")
# # plt.scatter(mx_x_2, mx_y_2, color="red", s=15, marker="o")
plt.yticks(list(plt.yticks()[0][:-2]) + [max(max(y_mx[0]), max(y_mx[1]))])
plt.ylim(120)
plt.show()
# res = {}
# for file in os.listdir("Testing/results/noxim/gen_order_testing"):
#     s = {"Avg delay": 0, "Max delay": 0, "Throughput": 0, "Total energy": 0}
#     with open("Testing/results/noxim/gen_order_testing/" + file, "r") as f:
#         for line in f:
#             if "Global average delay" in line:
#                 s["Avg delay"] = float(line.split()[-1])
#             if "Max delay" in line:
#                 s["Max delay"] = int(line.split()[-1])
#             if "Network throughput" in line:
#                 s["Throughput"] = float(line.split()[-1])
#             if "Total energy (J)" in line:
#                 s["Total energy"] = float(line.split()[-1])
#     if file.split("-")[0] not in list(res.keys()):
#         res[file.split("-")[0]] = {f"{file.split("-")[1]}-{file.split("-")[2]}": s}
#     else:
#         res[file.split("-")[0]][f"{file.split("-")[1]}-{file.split("-")[2]}"] = s

# df = {
#     "Pattern": [],
#     "Size": [],
#     "Avg delay ordered": [],
#     "Avg delay random": [],
#     "Avg delay diff": [],
#     "Max delay ordered": [],
#     "Max delay random": [],
#     "Max delay diff": [],
#     "Throughput ordered": [],
#     "Throughput random": [],
#     "Throughput diff": [],
#     "Total energy ordered": [],
#     "Total energy random": [],
#     "Total energy diff": [],
# }
# for i in res:
#     c = 0
#     for j in res[i]:
#         if j.split("-")[1][:-4] == "ordered":
#             df["Avg delay ordered"].append(res[i][j]["Avg delay"])
#             df["Max delay ordered"].append(res[i][j]["Max delay"])
#             df["Throughput ordered"].append(res[i][j]["Throughput"])
#             df["Total energy ordered"].append(res[i][j]["Total energy"])
#         else:
#             df["Avg delay random"].append(res[i][j]["Avg delay"])
#             df["Max delay random"].append(res[i][j]["Max delay"])
#             df["Throughput random"].append(res[i][j]["Throughput"])
#             df["Total energy random"].append(res[i][j]["Total energy"])
#         if c == 0:
#             df["Pattern"].append(i)
#             df["Size"].append(j.split("-")[0])
#             c = 1
#         else:
#             c = 0
#             df["Avg delay diff"].append(
#                 (df["Avg delay random"][-1] - df["Avg delay ordered"][-1])
#                 / df["Avg delay ordered"][-1]
#             )
#             df["Max delay diff"].append(
#                 (df["Max delay random"][-1] - df["Max delay ordered"][-1])
#                 / df["Max delay ordered"][-1]
#             )
#             df["Throughput diff"].append(
#                 (df["Throughput random"][-1] - df["Throughput ordered"][-1])
#                 / df["Throughput ordered"][-1]
#             )
#             df["Total energy diff"].append(
#                 (df["Total energy random"][-1] - df["Total energy ordered"][-1])
#                 / df["Total energy ordered"][-1]
#             )


# df = pd.DataFrame(df)
# print(df)
# df.to_excel("res.xlsx", index=False)
