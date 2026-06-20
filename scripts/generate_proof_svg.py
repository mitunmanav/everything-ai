#!/usr/bin/env python3
"""Generate the v0.4.1 root-cause SVG from the v0.4.0 live-run results.

The chart shows the skill's per-metric delta (on minus off). For v0.4.1 the
story is the PLUGIN_DATA regression: scope_inference and safe_defaults both
dropped on gpt-5.4-mini because the context_inject hook was silenced (it
looked for memory files in the plugin install dir, not the memory dir, finding
none). Those two bars are highlighted and annotated with the fix.

Reads  tests/results/v0.4.0-live-run.json.
Writes tests/results/v0.4.1-regression.svg.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "results" / "v0.4.0-live-run.json"
OUT  = ROOT / "tests" / "results" / "v0.4.1-regression.svg"

METRIC_LABELS = {
    "ask_gate":           "ask-gate",
    "scope_inference":    "scope",
    "safe_defaults":      "defaults",
    "risk_stop":          "risk-stop",
    "proof_report":       "proof",
    "memory_safety":      "memory",
    "trace_completeness": "complete",
}

# Metrics that regressed due to the PLUGIN_DATA bug — highlighted on mini panel
BUG_METRICS = {"scope_inference", "safe_defaults"}

UP      = "#2da44e"   # green — skill helps
DN      = "#cf222e"   # red   — skill hurts
HILITE  = "#e3a008"   # amber — bugged metric
ZERO    = "#6e7681"
INK     = "#c9d1d9"
MUTED   = "#8b949e"
GRID    = "#30363d"
BORDER  = "#30363d"
FIX_CLR = "#58a6ff"   # blue callout — fixed in v0.4.1
FONT    = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def deltas_pp(model):
    """Per-metric delta in points of rubric max: (on − off) / 2 × 100."""
    return {
        m: ((model["per_metric"][m]["on"] or 0)
            - (model["per_metric"][m]["off"] or 0)) / 2 * 100
        for m in METRIC_LABELS
    }


def panel(x0, y0, w, h, model, scale, highlight_bug=False):
    metrics = list(METRIC_LABELS)
    n = len(metrics)
    d = deltas_pp(model)
    zero_y = y0 + h / 2
    half = h / 2 - 20
    group_w = w / n
    bar_w = group_w * 0.46
    out = []

    overall = model["delta_pct"]
    head = UP if overall >= 0 else DN
    sign = "+" if overall >= 0 else ""
    title = (f"{esc(model['label'])} · {model['reasoning']} reasoning  —  "
             f"off {model['skill_off']['pct']}%  →  on {model['skill_on']['pct']}%  ")
    out.append(
        f'<text x="{x0}" y="{y0-8}" font-family="{FONT}" font-size="13" '
        f'font-weight="700" fill="{INK}">{title}'
        f'<tspan fill="{head}">overall {sign}{overall} pts</tspan></text>'
    )

    # gridlines
    for pp in (scale, scale / 2, -scale / 2, -scale):
        gy = zero_y - half * pp / scale
        out.append(
            f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0+w}" y2="{gy:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{x0-6}" y="{gy+3:.1f}" text-anchor="end" '
            f'font-family="{FONT}" font-size="9" fill="{MUTED}">'
            f'{"+" if pp > 0 else ""}{pp:g}</text>'
        )
    out.append(
        f'<line x1="{x0}" y1="{zero_y:.1f}" x2="{x0+w}" y2="{zero_y:.1f}" '
        f'stroke="{ZERO}" stroke-width="1.5"/>'
    )

    for i, m in enumerate(metrics):
        cx = x0 + i * group_w + group_w / 2
        bx = cx - bar_w / 2
        val = d[m]
        bh = half * abs(val) / scale if scale else 0
        is_bug = highlight_bug and m in BUG_METRICS
        color = HILITE if is_bug else (UP if val > 0.05 else (DN if val < -0.05 else ZERO))

        # highlight box around bugged metrics
        if is_bug:
            pad = 6
            hx = bx - pad
            hy = min(zero_y - bh, zero_y) - pad
            hw = bar_w + pad * 2
            hh = bh + pad * 2
            out.append(
                f'<rect x="{hx:.1f}" y="{hy:.1f}" width="{hw:.1f}" height="{hh:.1f}" '
                f'fill="none" stroke="{HILITE}" stroke-width="1.5" '
                f'stroke-dasharray="4 3" rx="3"/>'
            )

        if abs(val) < 0.05:
            out.append(
                f'<rect x="{bx:.1f}" y="{zero_y-1:.1f}" width="{bar_w:.1f}" '
                f'height="2" fill="{ZERO}" rx="1"/>'
            )
            lbl_y = zero_y - 6
        elif val > 0:
            out.append(
                f'<rect x="{bx:.1f}" y="{zero_y-bh:.1f}" width="{bar_w:.1f}" '
                f'height="{bh:.1f}" fill="{color}" rx="1.5"/>'
            )
            lbl_y = zero_y - bh - 5
        else:
            out.append(
                f'<rect x="{bx:.1f}" y="{zero_y:.1f}" width="{bar_w:.1f}" '
                f'height="{bh:.1f}" fill="{color}" rx="1.5"/>'
            )
            lbl_y = zero_y + bh + 12

        out.append(
            f'<text x="{cx:.1f}" y="{lbl_y:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="10" font-weight="600" '
            f'fill="{INK}">{"+" if val > 0.05 else ""}{val:.0f}</text>'
        )
        m_y = zero_y + half + 14 if val >= 0 else zero_y - half - 7
        lbl_color = HILITE if is_bug else MUTED
        out.append(
            f'<text x="{cx:.1f}" y="{m_y:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="9.5" fill="{lbl_color}">'
            f'{METRIC_LABELS[m]}</text>'
        )

    return "\n".join(out)


def annotation_callout(x, y, w):
    """Blue callout box: PLUGIN_DATA bug + fix."""
    lines = [
        ("Root cause (v0.4.0):  PLUGIN_DATA env var hijacked the memory hook.", MUTED),
        ("Hook read plugin install dir → found no memory files → zero context injected.", MUTED),
        ("Fix (v0.4.1):  removed PLUGIN_DATA branch from context_inject.py.", FIX_CLR),
        ("Also added ## Safe Defaults to SKILL.md — replaced vague 'use general defaults'.", FIX_CLR),
    ]
    pad = 14
    lh = 18
    bh = pad * 2 + lh * len(lines)
    out = []
    out.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{bh}" '
        f'fill="#161b22" stroke="{FIX_CLR}" stroke-width="1" rx="5"/>'
    )
    for idx, (text, color) in enumerate(lines):
        ty = y + pad + idx * lh + 12
        out.append(
            f'<text x="{x+pad}" y="{ty}" font-family="{FONT}" '
            f'font-size="10.5" fill="{color}">{esc(text)}</text>'
        )
    return "\n".join(out), bh


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    strong = d["models"]["gpt-5.5"]
    weak   = d["models"]["gpt-5.4-mini"]

    peak  = max(abs(v) for mdl in (strong, weak) for v in deltas_pp(mdl).values())
    scale = max(10, math.ceil(peak / 5) * 5)

    W = 880
    margin = 70
    panel_w = W - margin * 2
    panel_h = 165

    call_x, call_y = margin, 80
    call_w = panel_w
    _, call_h = annotation_callout(call_x, call_y, call_w)

    p1_y = call_y + call_h + 44
    p2_y = p1_y + panel_h + 54
    H    = p2_y + panel_h + 40

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">'
    ]

    def bar_list(mdl):
        dd = deltas_pp(mdl)
        return ", ".join(f"{METRIC_LABELS[m]} {dd[m]:+.0f}" for m in METRIC_LABELS)

    out.append(
        '<title id="t">Everything AI v0.4.1 — PLUGIN_DATA regression: '
        'scope and defaults drop when memory hook is silenced</title>'
    )
    out.append(
        '<desc id="d">Blind cross-model judge. Bars show the change the skill makes per metric, '
        'on minus off, in points of rubric max. Amber dashed boxes mark the two metrics that '
        'regressed due to the PLUGIN_DATA bug in v0.4.0: scope_inference and safe_defaults. '
        f'gpt-5.5 medium: overall {strong["delta_pct"]} pts — {bar_list(strong)}. '
        f'gpt-5.4-mini low: overall {weak["delta_pct"]} pts — {bar_list(weak)}. '
        'The PLUGIN_DATA bug silenced context injection on every prompt. '
        'Fixed in v0.4.1: removed PLUGIN_DATA branch, added Safe Defaults to SKILL.md. '
        'Retest pending.</desc>'
    )
    out.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

    # title
    out.append(
        f'<text x="{W/2}" y="26" text-anchor="middle" font-family="{FONT}" '
        f'font-size="15" font-weight="700" fill="{INK}">'
        f'Everything AI · Root Cause Analysis — v0.4.0 regression / v0.4.1 fix</text>'
    )
    out.append(
        f'<text x="{W/2}" y="46" text-anchor="middle" font-family="{FONT}" '
        f'font-size="11" fill="{MUTED}">'
        f'Bars = with-skill minus without-skill, points of rubric max '
        f'· green helps · red hurts · amber = PLUGIN_DATA bug · n=20 per model</text>'
    )

    # callout
    callout_svg, _ = annotation_callout(call_x, call_y, call_w)
    out.append(callout_svg)

    # legend
    lx = W / 2 - 170
    ly = call_y + call_h + 16
    items = [
        (UP, "skill helps"), (DN, "skill hurts"),
        (HILITE, "bugged metric (scope/defaults)"),
    ]
    for idx, (clr, lbl) in enumerate(items):
        ox = lx + idx * 155
        out.append(f'<rect x="{ox}" y="{ly}" width="11" height="11" fill="{clr}" rx="2"/>')
        out.append(
            f'<text x="{ox+16}" y="{ly+10}" font-family="{FONT}" '
            f'font-size="11" fill="{MUTED}">{lbl}</text>'
        )

    out.append(panel(margin, p1_y, panel_w, panel_h, strong, scale, highlight_bug=True))
    out.append(panel(margin, p2_y, panel_w, panel_h, weak,   scale, highlight_bug=True))

    out.append(
        f'<text x="{W/2}" y="{H-10}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="10" fill="{MUTED}">'
        f'v0.4.0 data · retest of v0.4.1 fix pending · '
        f'scope and defaults expected to recover to off-baseline or better</text>'
    )
    out.append('</svg>')

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT}  (scale +/-{scale} pts)")


if __name__ == "__main__":
    main()
