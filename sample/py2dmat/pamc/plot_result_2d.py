import os.path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors


def read_result(filename):
    fs = []
    xs = []
    ys = []
    with open(filename) as f:
        for line in f:
            line = line.split("#")[0].strip()
            if len(line) == 0:
                continue
            data = line.split()
            fs.append(float(data[3]))
            xs.append(float(data[4]))
            ys.append(float(data[5]))
    return fs, xs, ys


fs = []
xs = []
ys = []
fig_T = plt.figure()
ax_T = fig_T.add_subplot(1, 1, 1)
fig_fx = plt.figure()
ax_fx = fig_fx.add_subplot(1, 1, 1)
for T in range(21):
    for mpirank in range(4):
        filename = os.path.join("output", str(mpirank), f"result_T{T}.txt")
        f, x, y = read_result(filename)
        fs += f
        xs += x
        ys += y
        ax_T.scatter(
            x,
            y,
            c=10.0 * T * np.ones(len(x)),
            s=20,
            marker="o",
            vmin=0,
            vmax=200.0,
            cmap="plasma",
        )

fmin = np.min(fs)
fmax = np.max(fs)
ax_fx.scatter(
    xs, ys, c=fs, s=20, marker="o", vmin=fmin, vmax=fmax, cmap="plasma",
)
for ax in (ax_T, ax_fx):
    ax.set_xlabel("z1")
    ax.set_ylabel("z2")
    ax.set_xlim((3.0, 6.0))
    ax.set_ylim((3.0, 6.0))
    ax.axis("square")
cb_T = fig_T.colorbar(
    cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=0.0, vmax=200.0), cmap="plasma"),
    ax=ax_T,
    label="β",
)
cb_fx = fig_fx.colorbar(
    cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=fmin, vmax=fmax), cmap="plasma"),
    ax=ax_fx,
    label="f(x)",
)
fig_T.savefig("result_T.pdf")
fig_T.savefig("result_T.png")
fig_fx.savefig("result_fx.pdf")
fig_fx.savefig("result_fx.png")
