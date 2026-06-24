#!/usr/bin/env python3
"""Build original SVG visuals for an HF weekly digest."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import textwrap


WIDTH = 1080
ACCENT = "#e8590c"
INK = "#1c1917"
MUTED = "#78716c"
PAPER = "#fffdf9"
SOFT = "#f6f2ec"
NAVY = "#14213d"


def esc(value: object) -> str:
    return html.escape(str(value))


def svg_document(title: str, body: str, *, height: int = 680, background: str = PAPER) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
<title>{esc(title)}</title>
<rect width="{WIDTH}" height="{height}" fill="{background}"/>
<style>
text {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif; }}
.title {{ font-size: 48px; font-weight: 800; fill: {INK}; }}
.subtitle {{ font-size: 25px; fill: {MUTED}; }}
.label {{ font-size: 25px; fill: {INK}; }}
.small {{ font-size: 20px; fill: {MUTED}; }}
.value {{ font-size: 30px; font-weight: 800; fill: {ACCENT}; }}
</style>
{body}
</svg>
"""


def save_svg(path: pathlib.Path, title: str, body: str, *, height: int = 680, background: str = PAPER) -> None:
    path.write_text(svg_document(title, body, height=height, background=background), encoding="utf-8")


def cover_svg(editorial: dict, path: pathlib.Path) -> None:
    title_lines = textwrap.wrap(editorial["title"], width=16)[:3]
    title_markup = "".join(
        f'<text x="74" y="{230 + index * 74}" class="title">{esc(line)}</text>'
        for index, line in enumerate(title_lines)
    )
    body = f"""
<rect x="0" y="0" width="18" height="680" fill="{ACCENT}"/>
<circle cx="905" cy="140" r="150" fill="{ACCENT}" opacity=".12"/>
<circle cx="940" cy="160" r="92" fill="{ACCENT}" opacity=".18"/>
<text x="74" y="92" font-size="22" font-weight="800" letter-spacing="5" fill="{ACCENT}">HF PAPERS · WEEKLY SIGNAL</text>
{title_markup}
<text x="76" y="505" class="subtitle">{esc(editorial['subtitle'])}</text>
<line x1="76" y1="545" x2="210" y2="545" stroke="{ACCENT}" stroke-width="6"/>
<text x="76" y="605" class="small">{esc(editorial['period'])}</text>
<text x="840" y="594" font-size="72" font-weight="900" fill="{NAVY}" opacity=".92">AI</text>
"""
    save_svg(path, editorial["title"], body)


def daily_svg(papers: dict, path: pathlib.Path) -> None:
    counts = papers["statistics"]["daily_counts"]
    maximum = max(counts.values()) if counts else 1
    bars = []
    for index, (day, count) in enumerate(counts.items()):
        x = 150 + index * 250
        height = 330 * count / maximum
        y = 540 - height
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="120" height="{height:.1f}" rx="18" fill="{ACCENT}" opacity="{.72 + index*.08}"/>'
            f'<text x="{x+60}" y="{y-20:.1f}" text-anchor="middle" class="value">{count}</text>'
            f'<text x="{x+60}" y="584" text-anchor="middle" class="small">{esc(day[5:])}</text>'
        )
    body = f"""
<text x="72" y="78" class="title">本期论文收录节奏</text>
<text x="72" y="120" class="subtitle">按 Hugging Face Daily Papers 提交日期统计</text>
<line x1="105" y1="540" x2="990" y2="540" stroke="#d6d3d1" stroke-width="2"/>
{''.join(bars)}
"""
    save_svg(path, "本期论文收录节奏", body)


def themes_svg(editorial: dict, path: pathlib.Path) -> None:
    themes = editorial["themes"]
    maximum = max(item["upvotes"] for item in themes) if themes else 1
    rows = []
    for index, item in enumerate(themes):
        y = 185 + index * 92
        width = 590 * item["upvotes"] / maximum
        rows.append(
            f'<text x="72" y="{y+28}" class="label">{esc(item["name"])}</text>'
            f'<rect x="320" y="{y}" width="{width:.1f}" height="42" rx="12" fill="{ACCENT}" opacity="{.9-index*.1}"/>'
            f'<text x="{335+width:.1f}" y="{y+29}" class="small">{item["papers"]} 篇 · {item["upvotes"]} 票</text>'
        )
    body = f"""
<text x="72" y="78" class="title">高热度论文的主题重心</text>
<text x="72" y="120" class="subtitle">主题可重叠；用于编辑观察，不代表全量互斥分类</text>
{''.join(rows)}
"""
    save_svg(path, "高热度论文的主题重心", body, height=max(620, 220 + len(themes) * 92))


def top_papers_svg(papers: dict, path: pathlib.Path) -> None:
    top = papers["papers"][:8]
    maximum = max(item["upvotes"] for item in top) if top else 1
    rows = []
    for index, item in enumerate(top):
        y = 155 + index * 67
        width = 390 * item["upvotes"] / maximum
        title = item["title"]
        if len(title) > 36:
            title = title[:35] + "…"
        rows.append(
            f'<text x="70" y="{y+26}" class="small">{index+1:02d}</text>'
            f'<text x="120" y="{y+26}" class="label" style="font-size:21px">{esc(title)}</text>'
            f'<rect x="610" y="{y}" width="{width:.1f}" height="34" rx="9" fill="{ACCENT}" opacity="{.92-index*.06}"/>'
            f'<text x="{625+width:.1f}" y="{y+25}" class="small">{item["upvotes"]}</text>'
        )
    body = f"""
<text x="72" y="72" class="title">本期高热度论文 Top 8</text>
<text x="72" y="112" class="subtitle">票数是冻结快照中的社区参与度，不是论文质量排名</text>
{''.join(rows)}
"""
    save_svg(path, "本期高热度论文 Top 8", body, height=735)


def pipeline_svg(editorial: dict, path: pathlib.Path) -> None:
    stages = editorial["pipeline"]
    boxes = []
    for index, stage in enumerate(stages):
        x = 55 + index * 250
        boxes.append(
            f'<rect x="{x}" y="250" width="205" height="130" rx="24" fill="{SOFT}" stroke="{ACCENT}" stroke-width="3"/>'
            f'<text x="{x+102}" y="308" text-anchor="middle" class="label">{esc(stage)}</text>'
            f'<text x="{x+102}" y="346" text-anchor="middle" class="small">0{index+1}</text>'
        )
        if index < len(stages) - 1:
            boxes.append(
                f'<path d="M {x+210} 315 L {x+242} 315" stroke="{ACCENT}" stroke-width="5"/>'
                f'<path d="M {x+235} 306 L {x+246} 315 L {x+235} 324" fill="none" stroke="{ACCENT}" stroke-width="5"/>'
            )
    body = f"""
<text x="72" y="82" class="title">Agent 系统工程闭环</text>
<text x="72" y="126" class="subtitle">本期多篇论文共同补齐的不是单点能力，而是一条可运行链路</text>
{''.join(boxes)}
<text x="540" y="470" text-anchor="middle" class="small">评测暴露失败 → 状态可追溯 → 环境可扩展 → 策略学习恢复</text>
"""
    save_svg(path, "Agent 系统工程闭环", body)


def paper_diagram_svg(item: dict, path: pathlib.Path) -> None:
    steps = item["steps"]
    columns = []
    step_width = 900 / max(1, len(steps))
    for index, step in enumerate(steps):
        x = 70 + index * step_width
        columns.append(
            f'<circle cx="{x+step_width/2:.1f}" cy="310" r="62" fill="{ACCENT}" opacity="{.17 + index*.06}"/>'
            f'<text x="{x+step_width/2:.1f}" y="305" text-anchor="middle" class="label">{esc(step)}</text>'
            f'<text x="{x+step_width/2:.1f}" y="345" text-anchor="middle" class="small">0{index+1}</text>'
        )
        if index < len(steps) - 1:
            columns.append(
                f'<line x1="{x+step_width-24:.1f}" y1="310" x2="{x+step_width+24:.1f}" y2="310" stroke="{NAVY}" stroke-width="4"/>'
            )
    body = f"""
<text x="72" y="76" class="title">{esc(item["title"])}</text>
<text x="72" y="120" class="subtitle">{esc(item["subtitle"])}</text>
{''.join(columns)}
<rect x="72" y="455" width="936" height="105" rx="18" fill="{NAVY}"/>
<text x="540" y="520" text-anchor="middle" font-size="25" fill="white">{esc(item["takeaway"])}</text>
"""
    save_svg(path, item["title"], body)


def build_visuals(
    papers_path: pathlib.Path,
    editorial_path: pathlib.Path,
    output_dir: pathlib.Path,
) -> dict:
    papers_path = pathlib.Path(papers_path)
    editorial_path = pathlib.Path(editorial_path)
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    papers = json.loads(papers_path.read_text(encoding="utf-8"))
    editorial = json.loads(editorial_path.read_text(encoding="utf-8"))

    specs = [
        ("cover.svg", "封面：本期核心判断", "original", cover_svg, editorial),
        ("daily-counts.svg", "图1：本期每日收录论文数量", "original-data", daily_svg, papers),
        ("theme-heat.svg", "图2：高热度论文主题重心", "original-data", themes_svg, editorial),
        ("top-papers.svg", "图3：本期高热度论文Top 8", "original-data", top_papers_svg, papers),
        ("agent-loop.svg", "图4：Agent系统工程研究闭环", "original-synthesis", pipeline_svg, editorial),
    ]
    for index, item in enumerate(editorial.get("paper_diagrams", []), start=1):
        specs.append(
            (
                f"paper-mechanism-{index}.svg",
                item["caption"],
                f"original-explanation:{item.get('paper_id', 'unknown')}",
                paper_diagram_svg,
                item,
            )
        )

    allowed_originals = set(editorial.get("include_originals", []))
    if allowed_originals:
        specs = [spec for spec in specs if spec[0] in allowed_originals]

    visuals = []
    for filename, caption, source, builder, payload in specs:
        path = output_dir / filename
        builder(payload, path)
        visuals.append(
            {
                "file": f"assets/{filename}",
                "kind": "original-editorial",
                "caption": caption,
                "source": source,
            }
        )
    manifest = {"visuals": visuals}
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--papers", required=True, type=pathlib.Path)
    parser.add_argument("--editorial", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()
    manifest = build_visuals(args.papers, args.editorial, args.output_dir)
    print(f"Wrote {len(manifest['visuals'])} visuals to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
