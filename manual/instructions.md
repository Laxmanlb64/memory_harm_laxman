# Instructions

## What this study does

We use a **ladder** design: each **ladder** is one **conspiracy scenario** (a distinct opening prompt from the ladder file). The model is run through a fixed number of **turns** per scenario. We then score assistant replies with the **universal codebook** dimensions (see `manual/Codebook.txt` / `manual/Codebook.md`).

The goal is to see whether **memory mode** (`none`, `summary`, or `full_context`) changes **harmful-in-context** patterns—risk-oriented scores (e.g. validation, elaboration, behavioral advice) versus safety-oriented scores (e.g. reality testing, referral)—**across ladders** when memory is varied.

---

Before running the scripts, export your OpenAI API key in the shell, e.g. `export OPENAI_API_KEY=your_key_here`.

## One command: `.log`, `.md`, and `.png` together

From the **repository root**, with `PYTHONPATH=.`:

```bash
PYTHONPATH=. python manual/interact.py \
  --model_id YOUR_MODEL \
  --memory_mode none \
  --n_turns 10 \
  --ladders manual/conspiracy.json
```

Use `--memory_mode summary` or `--memory_mode full_context` for other modes.

**Outputs** (paths printed at the end):

| Output | Location |
|--------|----------|
| **`.log`** | `manual/logs/conspiracy_<memory_mode>_<timestamp>.log` |
| **`.md`** | `manual/logs/markdown/<same_stem>.md` (written automatically after the run) |
| **`.png`** | `manual/logs/plots/<same_stem>.png` (single-session evaluator plot; written automatically if plotting succeeds) |

**Note:** After turn 1 of each ladder, `interact.py` prompts for **stdin** (`Enter your message`). Plan scripted turns accordingly, or use only `--n_turns 1` if you want a single scripted turn per ladder without typing.

---

## If you already have a `.log`: Markdown only

```bash
PYTHONPATH=. python manual/log_read.py manual/logs/your_session.log
```

Default Markdown path: `manual/logs/markdown/<log_stem>.md`. Use `-o /path/to/out.md` to choose the file.

---

## Plots: individual session vs three memory modes

All commands assume **repository root** and `PYTHONPATH=.`.

### Individual plot (one memory mode, one session)

Eight dimensions vs turn index in a **4×2** figure:

```bash
PYTHONPATH=. python manual/eval_plot.py manual/logs/conspiracy_none_20260501_103340.log
```

Default image: `manual/logs/plots/<log_stem>.png`. Optional: `-o path/to/out.png`.

### Comparison plot (overlay `none`, `summary`, `full_context`)

Put **three** `.log` files in one folder—filenames must distinguish modes (e.g. `..._none_...`, `..._summary_...`, `..._full_context_...` as in `manual/logs/`). Then:

```bash
PYTHONPATH=. python manual/eval_plot.py manual/logs
```

If the path is a **directory**, the script expects **exactly one log per mode** and writes:

`manual/logs/plots/evaluator_compare_memory_modes.png` (override with `-o`).

---

## Quick reference

| Goal | Command |
|------|---------|
| New session → `.log` + `.md` + `.png` | `python manual/interact.py --model_id … --memory_mode … --n_turns … --ladders manual/conspiracy.json` |
| `.log` → `.md` only | `python manual/log_read.py <path/to.log>` |
| `.log` → evaluator plot | `python manual/eval_plot.py <path/to.log>` |
| Three mode logs → comparison plot | `python manual/eval_plot.py <directory>` |
