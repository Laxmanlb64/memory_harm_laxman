"""
Plot evaluator scores vs turn index from a conspiracy session .log file
(manual/interact.py format).

By default, figures are written to ``<log_dir>/plots/<log_stem>.png``.

Pass a **directory** containing three ``.log`` files (memory modes ``none``,
``summary``, ``full_context`` inferable from filenames) to overlay all modes
in one figure (line plots per dimension).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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

MEMORY_MODES = ("none", "summary", "full_context")

# Distinct colors for overlay (matplotlib tab10-like).
MODE_COLORS = {
    "none": "#1f77b4",
    "summary": "#ff7f0e",
    "full_context": "#2ca02c",
}


def infer_memory_mode_from_stem(stem: str) -> str | None:
    """Map ``*.log`` basename (no extension) to a memory mode, or None."""
    s = stem.lower()
    if "full_context" in s:
        return "full_context"
    if "summary" in s:
        return "summary"
    if re.search(r"(^|_)none(_|$)", s):
        return "none"
    return None


def collect_mode_logs(log_dir: Path) -> dict[str, Path]:
    """
    Find exactly one ``.log`` per memory mode under ``log_dir``.
    Filenames must contain ``none``, ``summary``, or ``full_context`` as used
    in stems like ``conspiracy_none_*``, ``conspiracy_summary_*``,
    ``conspiracy_full_context_*``.
    """
    log_dir = log_dir.resolve()
    found: dict[str, Path] = {}
    ambiguous: list[Path] = []
    for p in sorted(log_dir.glob("*.log")):
        mode = infer_memory_mode_from_stem(p.stem)
        if mode is None:
            ambiguous.append(p)
            continue
        if mode in found:
            raise ValueError(
                f"Two logs map to mode {mode!r}: {found[mode].name} and {p.name}"
            )
        found[mode] = p
    missing = [m for m in MEMORY_MODES if m not in found]
    if missing:
        hint = ""
        if ambiguous:
            hint = f" Unmatched files: {[x.name for x in ambiguous]}."
        raise ValueError(
            f"Directory {log_dir} is missing logs for mode(s): {missing}.{hint}"
        )
    return found


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
    Draw 4×2 subplots (one per dimension). If out_path is None, saves to
    ``<log_dir>/plots/<same basename as .log>.png``. Returns path to saved figure.
    """
    log_p = Path(log_path).resolve()
    turns = load_scored_turns(log_p)
    if not turns:
        raise ValueError(
            f"No scored turns found in {log_p}. "
            "Check that the log matches interact.py format and evaluator JSON includes all eight keys."
        )

    turn_indices = [t["turn"] for t in turns]

    fig, axes = plt.subplots(4, 2, figsize=(22, 16), sharex=True)
    axes_flat = axes.flatten()

    for ax, key in zip(axes_flat, DIMENSIONS):
        ys = [int(t["evaluator_response"][key]) for t in turns]
        ax.plot(turn_indices, ys, marker="o", linewidth=1.5, markersize=5)
        ax.set_title(key.replace("_", " ").title(), fontsize=10)
        ax.set_ylim(-0.15, 3.15)
        ax.set_yticks([0, 1, 2, 3])
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("score")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=12, integer=True, prune=None))

    for ax in axes_flat[-2:]:
        ax.set_xlabel("turn")

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


def default_compare_plot_path(log_dir: Path) -> Path:
    plots_dir = log_dir.resolve() / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    return plots_dir / "evaluator_compare_memory_modes.png"


def plot_evaluator_modes_comparison(
    log_dir: str | Path,
    out_path: str | Path | None = None,
) -> Path:
    """
    One 4×2 figure: each subplot is a dimension; three line series per subplot
    (none, summary, full_context) vs turn index.
    """
    log_dir_p = Path(log_dir).resolve()
    mode_to_log = collect_mode_logs(log_dir_p)
    mode_turns: dict[str, list[dict]] = {
        m: load_scored_turns(mode_to_log[m]) for m in MEMORY_MODES
    }
    for m in MEMORY_MODES:
        if not mode_turns[m]:
            raise ValueError(f"No scored turns in {mode_to_log[m]}")

    # Wide figure: more horizontal space per subplot (2 columns × 4 rows).
    fig, axes = plt.subplots(4, 2, figsize=(22, 16), sharex=True)
    axes_flat = axes.flatten()

    for ax, key in zip(axes_flat, DIMENSIONS):
        for mode in MEMORY_MODES:
            turns = mode_turns[mode]
            xs = [t["turn"] for t in turns]
            ys = [int(t["evaluator_response"][key]) for t in turns]
            ax.plot(
                xs,
                ys,
                marker="o",
                linewidth=1.5,
                markersize=4,
                color=MODE_COLORS[mode],
                label=mode,
                alpha=0.95,
            )
        ax.set_title(key.replace("_", " ").title(), fontsize=10)
        ax.set_ylim(-0.15, 3.15)
        ax.set_yticks([0, 1, 2, 3])
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("score")
        ax.xaxis.set_major_locator(MaxNLocator(nbins=12, integer=True, prune=None))

    for ax in axes_flat[-2:]:
        ax.set_xlabel("turn")

    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=9, frameon=True)
    fig.suptitle(
        "Evaluator scores vs turn — memory modes (none / summary / full_context)",
        fontsize=12,
        y=1.005,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.98))

    if out_path is None:
        out_path = default_compare_plot_path(log_dir_p)
    else:
        out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Plot 8 evaluator dimensions vs turn: one .log, or a folder with three mode logs."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to a conspiracy .log file, or a directory with three .log files (none, summary, full_context).",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default="",
        help="Output image path (defaults: single → <log_dir>/plots/<stem>.png; "
        "compare → <dir>/plots/evaluator_compare_memory_modes.png)",
    )
    args = parser.parse_args()
    p = Path(args.path)
    if not p.exists():
        raise SystemExit(f"Not found: {p}")
    if p.is_dir():
        out = plot_evaluator_modes_comparison(p, args.out or None)
    else:
        out = plot_evaluator_over_turns(p, args.out or None)
    print(out)


if __name__ == "__main__":
    main()
