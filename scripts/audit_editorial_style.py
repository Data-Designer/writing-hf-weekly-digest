#!/usr/bin/env python3
"""Audit a digest for the PaperScope-style editorial narrative engine."""

from __future__ import annotations

import argparse
import json
import pathlib
import re


PROFILES = {
    "paperscope-partial": {
        "min_chars": 12000,
        "themes": 5,
        "min_cards": 10,
        "min_insights": 10,
        "min_transitions": 4,
    },
    "paperscope-complete": {
        "min_chars": 15000,
        "themes": 5,
        "min_cards": 12,
        "min_insights": 12,
        "min_transitions": 4,
    },
}

ENGINE_MARKERS = (
    "判断：",
    "为什么这件事现在发生",
    "代表论文",
    "🔍 技术综观",
    "💼 落地实战",
)

CLOSING_MARKERS = (
    "本周可以做什么",
    "给你的三个思考问题",
    "一句话总结",
    "关于这篇",
)

QUOTE_SECTION_MARKERS = (
    "五句带走",
    "五句可以直接截图",
)


def error(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def audit_text(text: str, *, profile: str) -> dict:
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    rules = PROFILES[profile]
    errors: list[dict] = []

    nonspace = len(re.sub(r"\s+", "", text))
    if nonspace < rules["min_chars"]:
        errors.append(
            error(
                "too-short",
                f"Article has {nonspace} non-whitespace characters; "
                f"minimum is {rules['min_chars']}",
            )
        )

    theme_numbers = re.findall(r"^##\s+0([1-5])\s*$", text, re.MULTILINE)
    if len(theme_numbers) != rules["themes"] or sorted(theme_numbers) != list("12345"):
        errors.append(
            error(
                "too-few-themes",
                f"Expected numbered themes 01–05; found {theme_numbers}",
            )
        )

    missing_engine = {
        marker: text.count(marker)
        for marker in ENGINE_MARKERS
        if text.count(marker) < rules["themes"]
    }
    if missing_engine:
        errors.append(
            error(
                "missing-theme-engine",
                f"Each theme needs the repeated editorial engine: {missing_engine}",
            )
        )

    cards = len(re.findall(r"^### .+?(?:票|Paper Card)", text, re.MULTILINE))
    if cards < rules["min_cards"]:
        errors.append(
            error(
                "too-few-paper-cards",
                f"Found {cards} paper cards; minimum is {rules['min_cards']}",
            )
        )

    insights = text.count("真正的 insight")
    if insights < rules["min_insights"]:
        errors.append(
            error(
                "too-few-insights",
                f"Found {insights} insight passages; minimum is {rules['min_insights']}",
            )
        )

    transitions = len(
        re.findall(r"(?:下一节|下一条|接下来).{0,40}(?:↓|告诉你|看看)", text)
    )
    if transitions < rules["min_transitions"]:
        errors.append(
            error(
                "too-few-transitions",
                f"Found {transitions} forward transitions; "
                f"minimum is {rules['min_transitions']}",
            )
        )

    missing_closing = [marker for marker in CLOSING_MARKERS if marker not in text]
    if not any(marker in text for marker in QUOTE_SECTION_MARKERS):
        missing_closing.append("五句带走")
    question_section = ""
    match = re.search(
        r"给你的三个思考问题(.*?)(?:一句话总结|\Z)",
        text,
        re.DOTALL,
    )
    if match:
        question_section = match.group(1)
    if missing_closing or question_section.count("？") + question_section.count("?") < 3:
        errors.append(
            error(
                "missing-closing-modules",
                f"Missing closing modules: {missing_closing or 'fewer than three questions'}",
            )
        )

    observation_position = text.find("三个被票数掩盖")
    snapshot_position = text.find("数据快照")
    first_theme_position = text.find("## 01")
    if not (
        0 <= observation_position < snapshot_position < first_theme_position
    ):
        errors.append(
            error(
                "weak-opening-order",
                "Expected structural observations before data snapshot and numbered themes",
            )
        )

    about_position = text.find("关于这篇")
    if about_position < int(len(text) * 0.75):
        errors.append(
            error(
                "caveat-too-early",
                "Methodology/caveats must appear in the final quarter",
            )
        )

    conflict_markers = sum(
        text.count(marker)
        for marker in (
            "不是",
            "真正的变化",
            "票数掩盖",
            "这不是巧合",
            "脏秘密",
            "正式",
            "作废",
            "卷",
        )
    )
    if conflict_markers < 8:
        errors.append(
            error(
                "weak-rhetorical-density",
                f"Found only {conflict_markers} conflict/judgment markers; minimum is 8",
            )
        )

    metrics = {
        "nonspace_characters": nonspace,
        "numbered_themes": len(theme_numbers),
        "paper_cards": cards,
        "insights": insights,
        "transitions": transitions,
        "conflict_markers": conflict_markers,
    }
    return {"profile": profile, "passed": not errors, "metrics": metrics, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article", type=pathlib.Path)
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default="paperscope-complete",
    )
    args = parser.parse_args()
    result = audit_text(args.article.read_text(encoding="utf-8"), profile=args.profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
