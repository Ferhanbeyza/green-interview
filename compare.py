import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

R = "results"


def last_run(name):
    path = os.path.join(R, f"emissions_{name}.csv")
    if not os.path.exists(path):
        raise SystemExit(f"{path} yok. Once {name}.py calistirin.")
    return pd.read_csv(path).iloc[-1]


def label_stats():
    frames = calls = same = 0
    for base_path in glob.glob(os.path.join(R, "labels_baseline_*.csv")):
        opt_path = base_path.replace("labels_baseline_", "labels_optimized_")
        if not os.path.exists(opt_path):
            continue
        b, o = pd.read_csv(base_path), pd.read_csv(opt_path)
        n = min(len(b), len(o))
        frames += n
        calls += int(o["analyzed"][:n].sum())
        same += int((b["emotion"][:n] == o["emotion"][:n]).sum())
    return frames, calls, same


def pct_drop(before, after):
    return 100 * (before - after) / before if before else 0.0


def main():
    b, o = last_run("baseline"), last_run("optimized")
    frames, calls, same = label_stats()

    rows = [
        ("Sure (sn)", b["duration"], o["duration"]),
        ("Enerji (kWh)", b["energy_consumed"], o["energy_consumed"]),
        ("CO2 (g)", b["emissions"] * 1000, o["emissions"] * 1000),
    ]
    lines = ["# Baseline vs Optimize", "",
             "| Metrik | Baseline | Optimize | Dusus |", "|---|---|---|---|"]
    for name, x, y in rows:
        lines.append(f"| {name} | {x:.6f} | {y:.6f} | %{pct_drop(x, y):.1f} |")
    if frames:
        lines.append(f"| Model cagrisi (kare) | {frames} | {calls} | %{pct_drop(frames, calls):.1f} |")
        lines += ["", f"Duygu sonucu uyumu (optimize = baseline): %{100 * same / frames:.1f} "
                      f"({same}/{frames} kare)"]
    summary = "\n".join(lines)
    with open(os.path.join(R, "summary.md"), "w") as f:
        f.write(summary + "\n")
    print(summary)

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
    for ax, (name, x, y) in zip(axes, rows):
        ax.bar(["Baseline", "Optimize"], [x, y], color=["#9aa0a6", "#0b8043"])
        ax.set_title(f"{name}\n-%{pct_drop(x, y):.1f}")
    fig.tight_layout()
    fig.savefig(os.path.join(R, "comparison.png"), dpi=200)
    print(f"\nGrafik: {R}/comparison.png")


if __name__ == "__main__":
    main()
