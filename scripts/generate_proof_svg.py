#!/usr/bin/env python3
"""Generate the v0.4.0 proof SVG from the live-run results.

The chart plots the *change* the skill makes — on minus off, in points of the
rubric max — as bars from a zero line: green above zero where the skill helps,
red below where it hurts. Grouped 0-100% bars hid the story because every score
sat at 75-100 and a few-point gain was invisible; a delta chart makes a small
but real effect obvious without truncating an axis to fake it. Two panels, one
per model: a capable model goes mostly green, a small one goes all red.

Reads tests/results/v0.4.0-live-run.json. Writes tests/results/v0.4.0-all-phases.svg.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "results" / "v0.4.0-live-run.json"
OUT = ROOT / "tests" / "results" / "v0.4.0-all-phases.svg"

METRIC_LABELS = {
    "ask_gate": "ask-gate",
    "scope_inference": "scope",
    "safe_defaults": "defaults",
    "risk_stop": "risk-stop",
    "proof_report": "proof",
    "memory_safety": "memory",
    "trace_completeness": "complete",
}
UP = "#2da44e"    # green — skill helps (delta > 0)
DN = "#cf222e"    # red   — skill hurts (delta < 0)
ZERO = "#6e7681"  # gray  — no change
INK = "#c9d1d9"
MUTED = "#8b949e"
GRID = "#30363d"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def deltas_pp(model):
    """Per-metric delta in points of rubric max: (on - off) / 2 * 100."""
    return {m: ((model["per_metric"][m]["on"] or 0)
                - (model["per_metric"][m]["off"] or 0)) / 2 * 100
            for m in METRIC_LABELS}


def panel(x0, y0, w, h, model, scale):
    """One model panel: signed delta bars from a centered zero line."""
    metrics = list(METRIC_LABELS)
    n = len(metrics)
    d = deltas_pp(model)
    zero_y = y0 + h / 2
    half = h / 2 - 16          # px for the tallest possible bar
    group_w = w / n
    bar_w = group_w * 0.46
    out = []

    overall = model["delta_pct"]
    head = UP if overall >= 0 else DN
    sign = "+" if overall >= 0 else ""
    title = (f"{esc(model['label'])} · {model['reasoning']} reasoning  —  "
             f"off {model['skill_off']['pct']}%  →  on {model['skill_on']['pct']}%  ")
    out.append(f'<text x="{x0}" y="{y0-8}" font-family="{FONT}" font-size="13" '
               f'font-weight="700" fill="{INK}">{title}'
               f'<tspan fill="{head}">overall {sign}{overall} pts</tspan></text>')

    # gridlines at +/- scale and +/- scale/2, plus the bold zero line
    for pp in (scale, scale / 2, -scale / 2, -scale):
        gy = zero_y - half * pp / scale
        out.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0+w}" y2="{gy:.1f}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{x0-6}" y="{gy+3:.1f}" text-anchor="end" '
                   f'font-family="{FONT}" font-size="9" fill="{MUTED}">'
                   f'{"+" if pp > 0 else ""}{pp:g}</text>')
    out.append(f'<line x1="{x0}" y1="{zero_y:.1f}" x2="{x0+w}" y2="{zero_y:.1f}" '
               f'stroke="{ZERO}" stroke-width="1.5"/>')

    for i, m in enumerate(metrics):
        cx = x0 + i * group_w + group_w / 2
        bx = cx - bar_w / 2
        val = d[m]
        bh = half * abs(val) / scale
        if abs(val) < 0.05:    # exactly flat — draw a thin marker on zero
            out.append(f'<rect x="{bx:.1f}" y="{zero_y-1:.1f}" width="{bar_w:.1f}" '
                       f'height="2" fill="{ZERO}" rx="1"/>')
            lbl_y = zero_y - 6
        elif val > 0:
            out.append(f'<rect x="{bx:.1f}" y="{zero_y-bh:.1f}" width="{bar_w:.1f}" '
                       f'height="{bh:.1f}" fill="{UP}" rx="1.5"/>')
            lbl_y = zero_y - bh - 5
        else:
            out.append(f'<rect x="{bx:.1f}" y="{zero_y:.1f}" width="{bar_w:.1f}" '
                       f'height="{bh:.1f}" fill="{DN}" rx="1.5"/>')
            lbl_y = zero_y + bh + 12
        # signed value label at the bar tip
        out.append(f'<text x="{cx:.1f}" y="{lbl_y:.1f}" text-anchor="middle" '
                   f'font-family="{FONT}" font-size="10" font-weight="600" '
                   f'fill="{INK}">{"+" if val > 0.05 else ""}{val:.0f}</text>')
        # metric label, kept clear of the zero line on whichever side is empty
        m_y = zero_y + half + 13 if val >= 0 else zero_y - half - 6
        out.append(f'<text x="{cx:.1f}" y="{m_y:.1f}" text-anchor="middle" '
                   f'font-family="{FONT}" font-size="9.5" fill="{MUTED}">'
                   f'{METRIC_LABELS[m]}</text>')
    return "\n".join(out)


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    strong = d["models"]["gpt-5.5"]
    weak = d["models"]["gpt-5.4-mini"]

    # shared symmetric scale so both panels are directly comparable
    peak = max(abs(v) for mdl in (strong, weak) for v in deltas_pp(mdl).values())
    scale = max(10, math.ceil(peak / 5) * 5)

    W, H = 880, 580
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">']
    def bar_list(mdl):
        d = deltas_pp(mdl)
        return ", ".join(f"{METRIC_LABELS[m]} {d[m]:+.0f}" for m in METRIC_LABELS)

    out.append('<title id="t">Everything AI v0.4.0 — what the skill changes, per metric</title>')
    out.append(
        '<desc id="d">Blind cross-model judge. Bars show the change the skill makes per metric, '
        'on minus off, in points of the rubric max: green above the zero line where it helps, red below where it hurts. '
        f'Top panel gpt-5.5 at medium reasoning, overall {strong["delta_pct"]} points — {bar_list(strong)}. '
        f'Bottom panel gpt-5.4-mini at low reasoning, overall {weak["delta_pct"]} points — {bar_list(weak)}. '
        'The skill helps a capable model and overloads a small one.</desc>')
    out.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

    out.append(f'<text x="{W/2}" y="30" text-anchor="middle" font-family="{FONT}" '
               f'font-size="16" font-weight="700" fill="{INK}">What the skill changes, metric by metric '
               f'(blind cross-model judge)</text>')
    out.append(f'<text x="{W/2}" y="50" text-anchor="middle" font-family="{FONT}" '
               f'font-size="11.5" fill="{MUTED}">Bars = with-skill minus without-skill, in points of rubric max · '
               f'above 0 the skill helps, below 0 it hurts · n=20 scored runs per model</text>')

    # legend
    lx = W / 2 - 110
    out.append(f'<rect x="{lx}" y="62" width="11" height="11" fill="{UP}" rx="2"/>')
    out.append(f'<text x="{lx+16}" y="72" font-family="{FONT}" font-size="11" fill="{MUTED}">skill helps</text>')
    out.append(f'<rect x="{lx+115}" y="62" width="11" height="11" fill="{DN}" rx="2"/>')
    out.append(f'<text x="{lx+131}" y="72" font-family="{FONT}" font-size="11" fill="{MUTED}">skill hurts</text>')

    out.append(panel(70, 130, W - 140, 175, strong, scale))
    out.append(panel(70, 385, W - 140, 175, weak, scale))

    out.append(f'<text x="{W/2}" y="{H-12}" text-anchor="middle" font-family="{FONT}" '
               f'font-size="10.5" fill="{MUTED}">A real model answering vague "do everything" requests in a '
               f'neutral scratch dir, scored blind. The skill is built for capable models.</text>')
    out.append('</svg>')
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT}  (scale +/-{scale} pts)")


if __name__ == "__main__":
    main()
