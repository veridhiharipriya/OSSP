#!/usr/bin/env python3
"""Disk Scheduling Algorithm Visualizer: FCFS, SSTF, SCAN, C-SCAN."""
import argparse
import sys

NAMES = ["FCFS", "SSTF", "SCAN", "C-SCAN"]
COLORS = ["#7c3aed", "#0f766e", "#2563eb", "#c2410c"]


def fcfs(head, reqs, max_cyl, direction):
    return [(head, False)] + [(r, False) for r in reqs]


def sstf(head, reqs, max_cyl, direction):
    path, rem, cur = [(head, False)], list(reqs), head
    while rem:
        cur = min(rem, key=lambda x: abs(x - cur))
        rem.remove(cur)
        path.append((cur, False))
    return path


def _split(head, reqs, direction):
    up = sorted(r for r in reqs if r >= head)
    down = sorted((r for r in reqs if r < head), reverse=True)
    return (up, down) if direction == "up" else (down, up)


def scan(head, reqs, max_cyl, direction):
    path = [(head, False)]
    first, second = _split(head, reqs, direction)
    edge = max_cyl if direction == "up" else 0
    path += [(r, False) for r in first]
    if second:
        if path[-1][0] != edge:
            path.append((edge, False))
        path += [(r, False) for r in second]
    return path


def cscan(head, reqs, max_cyl, direction):
    path = [(head, False)]
    first, second = _split(head, reqs, direction)
    edge, opposite = (max_cyl, 0) if direction == "up" else (0, max_cyl)
    path += [(r, False) for r in first]
    if second:
        if path[-1][0] != edge:
            path.append((edge, False))
        path.append((opposite, True))  # return sweep
        # continue in the original direction from the opposite end
        second = sorted(second, reverse=(direction == "down"))
        path += [(r, False) for r in second]
    return path


ALGORITHMS = [fcfs, sstf, scan, cscan]


def total_seek(path, count_jump=True):
    total = 0
    for i in range(1, len(path)):
        if path[i][1] and not count_jump:
            continue
        total += abs(path[i][0] - path[i - 1][0])
    return total


def run_all(head, reqs, size, direction="up", count_jump=True):
    results = []
    for name, fn in zip(NAMES, ALGORITHMS):
        path = fn(head, reqs, size - 1, direction)
        t = total_seek(path, count_jump)
        results.append({"name": name, "path": path, "total": t, "avg": t / len(reqs)})
    return results


def print_table(results):
    best = min(r["total"] for r in results)
    print(f"\n{'Algorithm':<9}{'Total seek':>11}{'Avg/request':>13}  Service order")
    print("-" * 78)
    for r in results:
        order = " -> ".join(str(c) for c, _ in r["path"])
        mark = "  <- lowest" if r["total"] == best else ""
        print(f"{r['name']:<9}{r['total']:>11}{r['avg']:>13.2f}  {order}{mark}")
    print()


def plot(results, size, save=None, show=True):
    import matplotlib
    if save and not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig = plt.figure(figsize=(13, 9))
    fig.suptitle("Disk Scheduling Algorithm Visualizer", fontsize=15, fontweight="bold")
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.55], hspace=0.45)
    axes = [fig.add_subplot(gs[i // 2, i % 2]) for i in range(4)]
    axb = fig.add_subplot(gs[2, :])
    steps = max(len(r["path"]) for r in results) - 1

    def draw(f):
        for ax, r, col in zip(axes, results, COLORS):
            ax.clear()
            p, n = r["path"], len(r["path"]) - 1
            upto = min(f, n)
            ax.set_xlim(-size * 0.03, size)
            ax.set_ylim(n + 0.5, -0.7)
            ax.set_xlabel("Cylinder")
            ax.set_ylabel("Step")
            ax.grid(alpha=0.3)
            ax.set_title(f"{r['name']}  (total seek = {r['total']})", color=col, fontweight="bold")
            for i in range(1, upto + 1):
                style = "--" if p[i][1] else "-"
                ax.plot([p[i - 1][0], p[i][0]], [i - 1, i], style, color=col, lw=2)
            for i in range(upto + 1):
                ax.plot(p[i][0], i, "o", color=col if i == upto else "white",
                        mec=col, ms=9 if i == upto else 6)
                if n <= 16 or i in (0, upto):
                    ax.annotate(str(p[i][0]), (p[i][0], i), xytext=(6, 3),
                                textcoords="offset points", fontsize=8)

    axb.bar(NAMES, [r["total"] for r in results], color=COLORS)
    axb.set_ylabel("Total seek (cylinders)")
    axb.set_title("Comparison")
    for i, r in enumerate(results):
        axb.text(i, r["total"], str(r["total"]), ha="center", va="bottom")

    if save:
        draw(steps)
        fig.savefig(save, dpi=130, bbox_inches="tight")
        print(f"Saved chart to {save}")
    if show:
        anim = FuncAnimation(fig, draw, frames=steps + 1, interval=700, repeat=False)
        plt.show()
        return anim


def parse_args(argv):
    ap = argparse.ArgumentParser(description="Compare FCFS, SSTF, SCAN and C-SCAN disk scheduling.")
    ap.add_argument("-r", "--requests", type=int, nargs="+",
                    default=[98, 183, 37, 122, 14, 124, 65, 67], help="request queue")
    ap.add_argument("-H", "--head", type=int, default=53, help="initial head position")
    ap.add_argument("-s", "--size", type=int, default=200, help="total cylinders (0..size-1)")
    ap.add_argument("-d", "--direction", choices=["up", "down"], default="up")
    ap.add_argument("--no-jump-count", action="store_true", help="do not count the C-SCAN return sweep")
    ap.add_argument("--no-gui", action="store_true", help="print the table only")
    ap.add_argument("--save", metavar="PNG", help="save the final chart to a PNG file")
    return ap.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    if a.size < 2:
        sys.exit("Error: --size must be at least 2.")
    if not 0 <= a.head < a.size:
        sys.exit(f"Error: head must be between 0 and {a.size - 1}.")
    if any(not 0 <= r < a.size for r in a.requests):
        sys.exit(f"Error: every request must be between 0 and {a.size - 1}.")
    results = run_all(a.head, a.requests, a.size, a.direction, not a.no_jump_count)
    print_table(results)
    if a.no_gui and not a.save:
        return
    plot(results, a.size, save=a.save, show=not (a.no_gui or a.save))


if __name__ == "__main__":
    main()
