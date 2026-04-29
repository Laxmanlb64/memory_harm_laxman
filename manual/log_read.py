"""
Read conspiracy session .log files (from manual/interact.py) and render clear Markdown.

Logs are plain text (separator lines, labeled sections, JSON). They are not Markdown
until passed through read_log_as_markdown().

By default, rendered .md files are written under a ``markdown/`` folder next to the
.log (``<log_dir>/markdown/<log_stem>.md``). That folder is only created if missing;
existing files are left in place. If the target .md name already exists, a numeric
suffix is used (``<stem>_1.md``, ...) so nothing is overwritten.
"""

import argparse
import json
import re
from pathlib import Path


SEP = "=" * 60


def default_markdown_out_path(log_path: str | Path) -> Path:
    """
    Path for Markdown next to the .log: <log_dir>/markdown/<log_stem>.md

    Creates the markdown/ directory if needed (never removes existing files).
    If that .md already exists, uses <log_stem>_1.md, <log_stem>_2.md, ...
    """
    log_p = Path(log_path).resolve()
    markdown_dir = log_p.parent / "markdown"
    markdown_dir.mkdir(parents=True, exist_ok=True)
    stem = log_p.stem
    candidate = markdown_dir / f"{stem}.md"
    if not candidate.exists():
        return candidate
    n = 1
    while True:
        alt = markdown_dir / f"{stem}_{n}.md"
        if not alt.exists():
            return alt
        n += 1


def _split_turn_blocks(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.split(SEP) if p.strip()]
    return parts


def _parse_turn_block(block: str) -> dict | None:
    """Parse one turn block into turn index, messages, and evaluator dict."""
    m_turn = re.search(r"^turn:\s*(\d+)\s*$", block, re.MULTILINE)
    if not m_turn:
        return None
    turn_index = int(m_turn.group(1))

    u_start = block.find("user_message:\n")
    a_start = block.find("assistant_reply:\n")
    e_start = block.find("evaluator_response:\n")
    if u_start == -1 or a_start == -1 or e_start == -1:
        return None

    user_message = block[u_start + len("user_message:\n") : a_start].strip()
    assistant_reply = block[a_start + len("assistant_reply:\n") : e_start].strip()
    json_str = block[e_start + len("evaluator_response:\n") :].strip()
    try:
        evaluator = json.loads(json_str)
    except json.JSONDecodeError:
        evaluator = {"_raw": json_str, "_error": "invalid JSON"}

    return {
        "turn": turn_index,
        "user_message": user_message,
        "assistant_reply": assistant_reply,
        "evaluator_response": evaluator,
    }


def read_log_as_markdown(log_path: str) -> str:
    """
    Open a .log file, parse turns, return a single Markdown document string.
    """
    path = Path(log_path)
    raw = path.read_text(encoding="utf-8")
    blocks = _split_turn_blocks(raw)
    turns = []
    for b in blocks:
        parsed = _parse_turn_block(b)
        if parsed:
            turns.append(parsed)
    turns.sort(key=lambda t: t["turn"])

    lines: list[str] = []
    lines.append(f"# Session log: `{path.name}`\n")
    lines.append(f"_Source: `{path}`_\n")

    score_keys = [
        "sycophancy",
        "validation",
        "elaboration",
        "behavioral_advice",
        "reality_testing",
        "concern_for_wellbeing",
        "referral",
        "de_escalation",
    ]

    for t in turns:
        lines.append(f"## Turn {t['turn']}\n")
        lines.append("### User\n")
        lines.append("```text\n")
        lines.append(t["user_message"])
        lines.append("\n```\n")
        lines.append("### Assistant\n")
        lines.append("```text\n")
        lines.append(t["assistant_reply"])
        lines.append("\n```\n")
        lines.append("### Evaluator\n")
        ev = t["evaluator_response"]
        if isinstance(ev, dict) and all(k in ev for k in score_keys):
            lines.append("| Dimension | Score |\n")
            lines.append("| --- | :---: |\n")
            for k in score_keys:
                lines.append(f"| {k} | {ev.get(k, '')} |\n")
            notes = ev.get("notes", "")
            if notes:
                lines.append(f"\n**Notes:** {notes}\n")
        else:
            lines.append("```json\n")
            lines.append(json.dumps(ev, indent=2))
            lines.append("\n```\n")
        lines.append("\n---\n")

    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render a conspiracy .log file as Markdown.")
    parser.add_argument("log_path", type=str, help="Path to .log file")
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default=None,
        help="Output .md path (default: <log_dir>/markdown/<log_stem>.md, non-overwriting)",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print Markdown to stdout instead of writing a file",
    )
    args = parser.parse_args()
    md = read_log_as_markdown(args.log_path)
    if args.print:
        print(md)
    else:
        out_path = Path(args.out) if args.out is not None else default_markdown_out_path(args.log_path)
        if args.out is not None:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
