#!/usr/bin/env python3
"""Generate the v0.4.0 proof SVG from the live-run results.

Visual language is modeled on the ponytail benchmark chart: GitHub-dark
palette, grouped bars, a dashed reference line, value labels above bars, a
legend, and a one-line honest caption. Two panels, one per model, so the
honest split is visible at a glance: the skill lifts a capable model and
hurts a small one.

Reads tests/results/v0.4.0-live-run.json. Writes tests/results/v0.4.0-all-phases.svg.
"""
import json
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
OFF = "#8b949e"   # gray  — without skill (baseline)
ON_UP = "#2da44e"  # green — with skill, when it helps
ON_DN = "#cf222e"  # red   — with skill, when it hurts
INK = "#c9d1d9"
MUTED = "#8b949e"
GRID = "#30363d"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def panel(x0, y0, w, h, model, data):
    """One model panel: grouped bars (off vs on) per metric, 0-100% scale."""
    metrics = list(METRIC_LABELS)
    n = len(metrics)
    plot_h = h - 46           # leave room for title + axis labels
    base_y = y0 + plot_h
    group_w = w / n
    bar_w = group_w * 0.30
    gap = group_w * 0.06
    out = []

    delta = data["delta_pct"]
    on_color = ON_UP if delta >= 0 else ON_DN
    sign = "+" if delta >= 0 else ""
    title = (f"{esc(model['label'])} · {model['reasoning']} reasoning  "
             f"—  off {data['skill_off']['pct']}%  →  on {data['skill_on']['pct']}%  "
             f"({sign}{delta})")
    out.append(f'<text x="{x0}" y="{y0-10}" font-family="{FONT}" font-size="13" '
               f'font-weight="700" fill="{INK}">{title}</text>')

    # gridlines 0/25/50/75/100
    for pct in (0, 25, 50, 75, 100):
        gy = base_y - plot_h * pct / 100
        out.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0+w}" y2="{gy:.1f}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{x0-6}" y="{gy+3:.1f}" text-anchor="end" '
                   f'font-family="{FONT}" font-size="9" fill="{MUTED}">{pct}</text>')

    for i, m in enumerate(metrics):
        gx = x0 + i * group_w
        off_pct = (data["per_metric"][m]["off"] or 0) / 2 * 100
        on_pct = (data["per_metric"][m]["on"] or 0) / 2 * 100
        cx = gx + group_w / 2
        # off bar
        ox = cx - bar_w - gap / 2
        oh = plot_h * off_pct / 100
        out.append(f'<rect x="{ox:.1f}" y="{base_y-oh:.1f}" width="{bar_w:.1f}" '
                   f'height="{oh:.1f}" fill="{OFF}" rx="1.5"/>')
        # on bar
        nx = cx + gap / 2
        nh = plot_h * on_pct / 100
        out.append(f'<rect x="{nx:.1f}" y="{base_y-nh:.1f}" width="{bar_w:.1f}" '
                   f'height="{nh:.1f}" fill="{on_color}" rx="1.5"/>')
        # metric label
        out.append(f'<text x="{cx:.1f}" y="{base_y+14:.1f}" text-anchor="middle" '
                   f'font-family="{FONT}" font-size="9.5" fill="{MUTED}">'
                   f'{METRIC_LABELS[m]}</text>')
    return "\n".join(out)


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    strong = d["models"]["gpt-5.5"]
    weak = d["models"]["gpt-5.4-mini"]

    W, H = 880, 560
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">']
    out.append('<title id="t">Everything AI v0.4.0 — behavior quality, with vs without the skill</title>')
    out.append(
        '<desc id="d">Blind cross-model judge, score as percent of the rubric max, higher is better. '
        f'Top panel gpt-5.5 at medium reasoning: without skill {strong["skill_off"]["pct"]} percent, '
        f'with skill {strong["skill_on"]["pct"]} percent, a {strong["delta_pct"]} point gain, '
        'with the biggest lift on trace completeness and ask-gating. '
        f'Bottom panel gpt-5.4-mini at low reasoning: without skill {weak["skill_off"]["pct"]} percent, '
        f'with skill {weak["skill_on"]["pct"]} percent, a {weak["delta_pct"]} point drop, every metric lower. '
        'The skill helps a capable model and overloads a small one.</desc>')
    out.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

    out.append(f'<text x="{W/2}" y="30" text-anchor="middle" font-family="{FONT}" '
               f'font-size="16" font-weight="700" fill="{INK}">Behavior quality with vs without the skill '
               f'(blind cross-model judge)</text>')
    out.append(f'<text x="{W/2}" y="50" text-anchor="middle" font-family="{FONT}" '
               f'font-size="11.5" fill="{MUTED}">Score as % of rubric max, higher is better · '
               f'10 vague-request scenarios, both arms, n=20 scored runs per model</text>')

    # legend
    lx = W / 2 - 150
    out.append(f'<rect x="{lx}" y="62" width="11" height="11" fill="{OFF}" rx="2"/>')
    out.append(f'<text x="{lx+16}" y="72" font-family="{FONT}" font-size="11" fill="{MUTED}">without skill</text>')
    out.append(f'<rect x="{lx+120}" y="62" width="11" height="11" fill="{ON_UP}" rx="2"/>')
    out.append(f'<text x="{lx+136}" y="72" font-family="{FONT}" font-size="11" fill="{MUTED}">with skill (helps)</text>')
    out.append(f'<rect x="{lx+255}" y="62" width="11" height="11" fill="{ON_DN}" rx="2"/>')
    out.append(f'<text x="{lx+271}" y="72" font-family="{FONT}" font-size="11" fill="{MUTED}">with skill (hurts)</text>')

    out.append(panel(70, 120, W - 140, 170, strong, strong))
    out.append(panel(70, 360, W - 140, 170, weak, weak))

    out.append(f'<text x="{W/2}" y="{H-12}" text-anchor="middle" font-family="{FONT}" '
               f'font-size="10.5" fill="{MUTED}">The honest measurement: a real model answering real vague '
               f'requests in a neutral scratch dir, scored blind. The skill is built for capable models.</text>')
    out.append('</svg>')
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
