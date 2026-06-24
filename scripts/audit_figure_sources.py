#!/usr/bin/env python3
"""Audit native-paper figure coverage and provenance metadata."""

from __future__ import annotations

import argparse
import json
import pathlib


REQUIRED_NATIVE_FIELDS = (
    "paper_id",
    "figure",
    "original_caption",
    "article_caption",
    "source_url",
    "image_url",
    "source_type",
)


def err(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def audit_manifest(root: pathlib.Path) -> dict:
    root = pathlib.Path(root)
    manifest_path = root / "assets" / "manifest.json"
    errors: list[dict] = []
    if not manifest_path.exists():
        return {
            "passed": False,
            "metrics": {},
            "errors": [err("missing-manifest", "assets/manifest.json is missing")],
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    visuals = manifest.get("visuals", [])
    non_cover = [
        item
        for item in visuals
        if "cover" not in pathlib.Path(item.get("file", "")).stem.lower()
    ]
    native = [item for item in non_cover if item.get("kind") == "paper-native"]
    ratio = len(native) / len(non_cover) if non_cover else 0.0
    if ratio < 0.70:
        errors.append(
            err(
                "native-ratio",
                f"Native paper figures are {len(native)}/{len(non_cover)} "
                f"({ratio:.1%}); minimum is 70%",
            )
        )

    paper_ids = {item.get("paper_id") for item in native if item.get("paper_id")}
    if len(paper_ids) < 5:
        errors.append(
            err(
                "too-few-source-papers",
                f"Native figures come from {len(paper_ids)} papers; minimum is 5",
            )
        )

    covered_themes = {
        int(item["theme"])
        for item in native
        if str(item.get("theme", "")).isdigit()
    }
    missing_themes = sorted(set(range(1, 6)) - covered_themes)
    if missing_themes:
        errors.append(
            err(
                "theme-without-native-figure",
                f"Numbered themes without a native paper figure: {missing_themes}",
            )
        )

    for item in native:
        missing = [field for field in REQUIRED_NATIVE_FIELDS if not item.get(field)]
        if missing:
            errors.append(
                err(
                    "incomplete-provenance",
                    f"{item.get('file')} is missing: {', '.join(missing)}",
                )
            )
        relative = item.get("file")
        if not relative or not (root / relative).exists():
            errors.append(err("missing-figure-file", f"Missing file: {relative}"))

    metrics = {
        "visuals": len(visuals),
        "non_cover_visuals": len(non_cover),
        "native_figures": len(native),
        "native_ratio": ratio,
        "source_papers": len(paper_ids),
        "covered_themes": sorted(covered_themes),
    }
    return {"passed": not errors, "metrics": metrics, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=pathlib.Path)
    args = parser.parse_args()
    result = audit_manifest(args.bundle)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
