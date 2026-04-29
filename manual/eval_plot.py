"""
Plot evaluator scores vs turn index from a conspiracy session .log file
(manual/interact.py format).

By default, figures are written to ``<log_dir>/plots/<log_stem>.png``.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from manual.log_read import _parse_turn_block, _split_turn_blocks


DIMENSIONS = [
    "sycophancy",
    "validation",
    "elaboration",
    "behavioral_advice",
    "reality_testing",
    "concern_for_wellbeing",
    "referral",
    "de_escalation",
]


def load_scored_turns(log_path: str | Path) -> list[dict]:
    raw = Path(log_path).read_text(encoding="utf-8")
    turns = []
    for block in _split_turn_blocks(raw):
        parsed = _parse_turn_block(block)
        if not parsed:
            continue
        ev = parsed["evaluator_response"]
        if isinstance(ev, dict) and all(k in ev for k in DIMENSIONS):
            turns.append(parsed)
    turns.sort(key=lambda t: t["turn"])
    return turns


def default_plot_out_path(log_path: str | Path) -> Path:
    """<log_dir>/plots/<log_stem>.png — creates plots/ if needed."""
    log_p = Path(log_path).resolve()
    plots_dir = log_p.parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    return plots_dir / f"{log_p.stem}.png"


def plot_evaluator_over_turns(log_path: str | Path, out_path: str | Path | None = None) -> Path:
    """
    Draw 2x4 subplots (one per dimension). If out_path is None, saves to
    <log_dir>/plots/<same basename as .log>.png
    Returns path to saved figure.
    """
    log_p = Path(log_path).resolve()
    turns = load_scored_turns(log_p)
    if not turns:
        raise ValueError(
            f"No scored turns found in {log_p}. "
            "Check that the log matches interact.py format and evaluator JSON includes all eight keys."
        )

    turn_indices = [t["turn"] for t in turns]

    fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharex=True)
    axes_flat = axes.flatten()

    for ax, key in zip(axes_flat, DIMENSIONS):
        ys = [int(t["evaluator_response"][key]) for t in turns]
        ax.plot(turn_indices, ys, marker="o", linewidth=1.5, markersize=5)
        ax.set_title(key.replace("_", " ").title(), fontsize=10)
        ax.set_ylim(-0.15, 3.15)
        ax.set_yticks([0, 1, 2, 3])
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("score")

    for ax in axes_flat[4:]:
        ax.set_xlabel("turn index")

    fig.suptitle(f"Evaluator scores — {log_p.name}", fontsize=12)
    fig.tight_layout()

    if out_path is None:
        out_path = default_plot_out_path(log_p)
    else:
        out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Plot 8 evaluator dimensions vs turn from a .log file.")
    parser.add_argument("log_path", type=str, help="Path to conspiracy .log")
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default="",
        help="Output image path (default: <log_dir>/plots/<log_stem>.png)",
    )
    args = parser.parse_args()
    out = plot_evaluator_over_turns(args.log_path, args.out or None)
    print(out)


if __name__ == "__main__":
    main()
