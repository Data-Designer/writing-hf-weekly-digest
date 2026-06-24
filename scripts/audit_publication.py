#!/usr/bin/env python3
"""Audit an HF weekly digest bundle against publication-grade requirements."""

from __future__ import annotations

import argparse
import json
import pathlib
import re


PROFILES = {
    "publication-partial": {
        "min_chars": 7000,
        "min_visuals": 6,
        "min_cards": 8,
        "min_insights": 8,
    },
    "publication-complete": {
        "min_chars": 10000,
        "min_visuals": 6,
        "min_cards": 8,
        "min_insights": 8,
    },
}

REQUIRED_FILES = (
    "digest.md",
    "digest-wechat.html",
    "audit.md",
    "source.json",
    "papers.json",
    "assets/manifest.json",
)


def _error(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def audit_bundle(root: pathlib.Path, *, profile: str) -> dict:
    root = pathlib.Path(root)
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    rules = PROFILES[profile]
    errors: list[dict] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            code = "missing-html" if relative == "digest-wechat.html" else "missing-file"
            errors.append(_error(code, f"Missing required file: {relative}"))

    digest_path = root / "digest.md"
    digest = digest_path.read_text(encoding="utf-8") if digest_path.exists() else ""
    nonspace = len(re.sub(r"\s+", "", digest))
    if nonspace < rules["min_chars"]:
        errors.append(
            _error(
                "too-short",
                f"Digest has {nonspace} non-whitespace characters; "
                f"minimum is {rules['min_chars']}",
            )
        )

    image_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", digest)
    if len(image_refs) < rules["min_visuals"]:
        errors.append(
            _error(
                "too-few-visuals",
                f"Digest references {len(image_refs)} visuals; "
                f"minimum is {rules['min_visuals']}",
            )
        )

    card_headings = re.findall(r"^### .+?(?:票|Paper Card)", digest, re.MULTILINE)
    if len(card_headings) < rules["min_cards"]:
        errors.append(
            _error(
                "too-few-paper-cards",
                f"Digest has {len(card_headings)} paper cards; "
                f"minimum is {rules['min_cards']}",
            )
        )

    insight_count = digest.count("真正的 insight")
    if insight_count < rules["min_insights"]:
        errors.append(
            _error(
                "too-few-insights",
                f"Digest has {insight_count} editorial insights; "
                f"minimum is {rules['min_insights']}",
            )
        )

    card_label_counts = {
        "💡 机制": digest.count("💡 机制"),
        "📈 结果": digest.count("📈 结果"),
        "⚠️ 局限": digest.count("⚠️ 局限"),
        "🛠 启示/你能学到什么": digest.count("🛠 启示")
        + digest.count("🛠 你能学到什么"),
    }
    for label, count in card_label_counts.items():
        if count < rules["min_cards"]:
            errors.append(
                _error(
                    "incomplete-paper-cards",
                    f"Only {count} cards contain {label}",
                )
            )

    caption_count = len(
        re.findall(r"^\*(?:图|封面)\s*\d*[^*]*?(?:来源|原创)[^*]*\*$", digest, re.MULTILINE)
    )
    if caption_count < len(image_refs):
        errors.append(
            _error(
                "missing-captions",
                f"Found {caption_count} attributed captions for {len(image_refs)} visuals",
            )
        )

    for reference in image_refs:
        if reference.startswith(("http://", "https://", "data:")):
            continue
        if not (root / reference).exists():
            errors.append(_error("broken-asset", f"Missing image asset: {reference}"))

    manifest_path = root / "assets" / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            visuals = manifest.get("visuals", [])
            if len(visuals) < rules["min_visuals"]:
                errors.append(
                    _error(
                        "manifest-too-small",
                        f"Manifest contains {len(visuals)} visuals; "
                        f"minimum is {rules['min_visuals']}",
                    )
                )
            for item in visuals:
                relative = item.get("file")
                if not relative or not (root / relative).exists():
                    errors.append(
                        _error("manifest-broken-asset", f"Missing manifest asset: {relative}")
                    )
                if not item.get("caption") or not item.get("source"):
                    errors.append(
                        _error("manifest-metadata", f"Incomplete manifest item: {relative}")
                    )
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(_error("invalid-manifest", str(exc)))

    html_path = root / "digest-wechat.html"
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")
        if html.count("<img ") < rules["min_visuals"]:
            errors.append(_error("html-too-few-images", "HTML does not contain enough images"))
        if html.count("<figcaption") < rules["min_visuals"]:
            errors.append(
                _error("html-too-few-captions", "HTML does not contain enough captions")
            )

    return {
        "profile": profile,
        "passed": not errors,
        "metrics": {
            "nonspace_characters": nonspace,
            "visuals": len(image_refs),
            "paper_cards": len(card_headings),
            "insights": insight_count,
            "captions": caption_count,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=pathlib.Path)
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default="publication-complete",
    )
    args = parser.parse_args()
    result = audit_bundle(args.bundle, profile=args.profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
