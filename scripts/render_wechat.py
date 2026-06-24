#!/usr/bin/env python3
"""Render the digest's constrained Markdown into a WeChat-friendly HTML file."""

from __future__ import annotations

import argparse
import html
import pathlib
import re


def inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r'<code style="background:#f3f0eb;padding:1px 5px;border-radius:4px;">\1</code>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" style="color:#e8590c;text-decoration:none;border-bottom:1px solid #f3b493;">\1</a>',
        escaped,
    )
    return escaped


def _table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        tag = "th" if not rows else "td"
        rows.append(
            "<tr>"
            + "".join(
                f'<{tag} style="border:1px solid #ece7df;padding:8px 9px;text-align:left;">{inline(cell)}</{tag}>'
                for cell in cells
            )
            + "</tr>"
        )
    return '<div style="overflow-x:auto;margin:16px 0;"><table style="border-collapse:collapse;width:100%;font-size:13px;">' + "".join(rows) + "</table></div>"


def render_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    parts: list[str] = []
    list_items: list[str] = []
    ordered = False
    paper_card_open = False

    def flush_list() -> None:
        nonlocal list_items, ordered
        if list_items:
            tag = "ol" if ordered else "ul"
            parts.append(
                f'<{tag} style="margin:10px 0 18px;padding-left:24px;color:#292524;line-height:1.85;">'
                + "".join(f"<li>{item}</li>" for item in list_items)
                + f"</{tag}>"
            )
            list_items = []

    index = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        if not line:
            flush_list()
            index += 1
            continue

        if line.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|"):
            flush_list()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            parts.append(_table(table_lines))
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if image_match:
            flush_list()
            alt, src = image_match.groups()
            escaped_src = html.escape(src, quote=True)
            caption = ""
            lookahead = index + 1
            while lookahead < len(lines) and not lines[lookahead].strip():
                lookahead += 1
            if lookahead < len(lines):
                candidate = lines[lookahead].strip()
                if candidate.startswith("*") and candidate.endswith("*"):
                    caption = candidate[1:-1]
                    index = lookahead
            is_native_paper_figure = src.startswith("assets/papers/")
            image_html = (
                f'<img src="{escaped_src}" alt="{html.escape(alt, quote=True)}" '
                'style="display:block;width:100%;max-width:100%;height:auto;border-radius:12px;"/>'
            )
            if is_native_paper_figure:
                image_html = (
                    f'<a href="{escaped_src}" target="_blank" rel="noopener" '
                    'style="display:block;text-decoration:none;" title="点击查看高清原图">'
                    f"{image_html}</a>"
                )
            caption_html = inline(caption) if caption else ""
            if is_native_paper_figure:
                caption_html += (
                    f'<br/><a href="{escaped_src}" target="_blank" rel="noopener" '
                    'style="color:#e8590c;text-decoration:none;">点击查看高清原图 ↗</a>'
                )
            parts.append(
                '<figure style="margin:22px 0 26px;">'
                + image_html
                + (
                    f'<figcaption style="margin-top:8px;text-align:center;font-size:12px;color:#8b8178;line-height:1.6;">{caption_html}</figcaption>'
                    if caption_html
                    else ""
                )
                + "</figure>"
            )
        elif line.startswith("# "):
            flush_list()
            parts.append(
                f'<h1 style="font-size:27px;line-height:1.45;margin:18px 0 12px;color:#1c1917;font-weight:850;">{inline(line[2:])}</h1>'
            )
        elif re.fullmatch(r"## 0[1-5]", line):
            flush_list()
            if paper_card_open:
                parts.append("</section>")
                paper_card_open = False
            number = line[3:]
            parts.append(
                '<div style="margin:38px 0 4px;font-size:46px;line-height:1;font-weight:900;'
                'color:#e8590c;letter-spacing:-2px;">'
                f"{number}</div>"
            )
        elif line.startswith("## "):
            flush_list()
            if paper_card_open:
                parts.append("</section>")
                paper_card_open = False
            parts.append(
                '<section style="margin:34px 0 12px;">'
                f'<h2 style="font-size:20px;line-height:1.5;margin:0;color:#1c1917;font-weight:800;">{inline(line[3:])}</h2>'
                '<div style="width:38px;height:3px;background:#e8590c;border-radius:2px;margin-top:8px;"></div></section>'
            )
        elif line.startswith("### ") and ("票" in line or "Paper Card" in line):
            flush_list()
            if paper_card_open:
                parts.append("</section>")
            paper_card_open = True
            parts.append(
                '<section class="paper-card" style="margin:20px 0;padding:18px 17px;background:#faf8f4;border:1px solid #eee8df;border-radius:12px;">'
                f'<h3 style="font-size:17px;line-height:1.55;margin:0 0 10px;color:#1c1917;font-weight:800;">{inline(line[4:])}</h3>'
            )
        elif line.startswith("### "):
            flush_list()
            if paper_card_open:
                parts.append("</section>")
                paper_card_open = False
            heading = line[4:]
            if heading.startswith("🔍"):
                parts.append(
                    '<section style="margin:18px 0;padding:15px 16px;background:#0d1426;'
                    'border-radius:10px;color:#e8edf5;">'
                    f'<h3 style="font-size:16px;margin:0;color:#ffffff;">{inline(heading)}</h3></section>'
                )
            elif heading.startswith("💼"):
                parts.append(
                    '<section style="margin:18px 0;padding:15px 16px;background:#f5f3ff;'
                    'border-left:4px solid #7c3aed;border-radius:0 10px 10px 0;">'
                    f'<h3 style="font-size:16px;margin:0;color:#4c1d95;">{inline(heading)}</h3></section>'
                )
            else:
                parts.append(
                    f'<h3 style="font-size:16px;line-height:1.55;margin:20px 0 10px;color:#57534e;font-weight:800;">{inline(heading)}</h3>'
                )
        elif line.startswith("> "):
            flush_list()
            parts.append(
                f'<blockquote style="margin:16px 0;padding:13px 15px;background:#f7f3ed;border-left:4px solid #e8590c;color:#57534e;line-height:1.8;">{inline(line[2:])}</blockquote>'
            )
        elif re.match(r"^[-*] ", line):
            if ordered:
                flush_list()
            ordered = False
            list_items.append(inline(line[2:]))
        elif re.match(r"^\d+\. ", line):
            if list_items and not ordered:
                flush_list()
            ordered = True
            list_items.append(inline(re.sub(r"^\d+\. ", "", line)))
        elif line == "---":
            flush_list()
            parts.append('<hr style="border:0;height:1px;background:#eee8df;margin:30px 12%;"/>')
        elif line.startswith("*") and line.endswith("*"):
            pass
        else:
            flush_list()
            parts.append(
                f'<p style="font-size:15px;line-height:1.9;margin:0 0 14px;color:#292524;text-align:left;">{inline(line)}</p>'
            )
        index += 1

    flush_list()
    if paper_card_open:
        parts.append("</section>")
    article = "".join(parts)
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;background:#f2efe9;">
<main style="box-sizing:border-box;max-width:720px;margin:0 auto;padding:24px 20px 50px;background:#fffdf9;overflow-wrap:anywhere;">
{article}
</main>
</body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    args.output.write_text(render_markdown(args.input.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
