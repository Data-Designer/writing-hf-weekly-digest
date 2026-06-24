#!/usr/bin/env python3
"""Collect selected figures from arXiv HTML or official project pages."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser


USER_AGENT = "writing-hf-weekly-digest/1.0"


class FigureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.current: dict | None = None
        self.figures: list[dict] = []
        self.caption_depth = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "figure":
            self.current = {
                "id": values.get("id"),
                "image_src": None,
                "caption_parts": [],
            }
            self.depth = 1
            return
        if self.current is None:
            return
        self.depth += 1
        if tag == "img" and not self.current["image_src"]:
            self.current["image_src"] = values.get("src")
        if tag == "figcaption":
            self.caption_depth = self.depth

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if tag == "figure":
            self.figures.append(self.current)
            self.current = None
            self.depth = 0
            self.caption_depth = 0
            return
        if self.depth == self.caption_depth and tag == "figcaption":
            self.caption_depth = 0
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if self.current is not None and self.caption_depth:
            self.current["caption_parts"].append(data)


def _is_logo(src: str) -> bool:
    lowered = src.lower()
    return any(
        marker in lowered
        for marker in (
            "arxiv-logo",
            "/logos/",
            "github-logo",
            "hf-logo",
            "website-logo",
            "cornell",
        )
    )


def parse_arxiv_figures(html_text: str, *, page_url: str) -> list[dict]:
    parser = FigureParser()
    parser.feed(html_text)
    figures = []
    for item in parser.figures:
        src = item.get("image_src")
        if not src or src.startswith("data:") or _is_logo(src):
            continue
        caption = re.sub(
            r"\s+",
            " ",
            html.unescape(" ".join(item.get("caption_parts", []))),
        ).strip()
        figure_match = re.match(r"((?:Figure|Fig\.)\s*\d+[A-Za-z]?)\s*[:.]?", caption)
        figure = figure_match.group(1).replace("Fig.", "Figure") if figure_match else item.get("id")
        figures.append(
            {
                "figure": figure or f"Figure {len(figures)+1}",
                "original_caption": caption,
                "image_url": urllib.parse.urljoin(
                    "https://arxiv.org/html/",
                    src,
                )
                if page_url.startswith("https://arxiv.org/html/")
                else urllib.parse.urljoin(page_url.rstrip("/") + "/", src),
                "source_url": page_url,
                "source_type": "arxiv-html",
            }
        )
    return figures


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def download(url: str, path: pathlib.Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if "text/html" in content_type and path.suffix.lower() not in (".svg",):
        raise ValueError(f"Expected image but received HTML from {url}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _extension(url: str, default: str = ".png") -> str:
    suffix = pathlib.Path(urllib.parse.urlparse(url).path).suffix.lower()
    return suffix if suffix in (".png", ".jpg", ".jpeg", ".webp", ".svg") else default


def collect(selection_path: pathlib.Path, output_dir: pathlib.Path) -> list[dict]:
    selection = json.loads(pathlib.Path(selection_path).read_text(encoding="utf-8"))
    output_dir = pathlib.Path(output_dir)
    entries = []
    cache: dict[str, list[dict]] = {}
    for item in selection["figures"]:
        paper_id = item["paper_id"]
        source_type = item.get("source_type", "arxiv-html")
        if source_type == "official-project":
            chosen = {
                "figure": item["figure"],
                "original_caption": item["original_caption"],
                "image_url": item["image_url"],
                "source_url": item["source_url"],
                "source_type": source_type,
            }
        else:
            page_url = item.get("source_url") or f"https://arxiv.org/html/{paper_id}"
            if page_url not in cache:
                cache[page_url] = parse_arxiv_figures(
                    fetch_text(page_url),
                    page_url=page_url,
                )
            candidates = cache[page_url]
            if "figure" in item:
                matches = [
                    candidate
                    for candidate in candidates
                    if candidate["figure"].lower() == item["figure"].lower()
                ]
                if not matches:
                    raise ValueError(f"{paper_id}: figure not found: {item['figure']}")
                chosen = matches[0]
            else:
                index = int(item.get("index", 1)) - 1
                chosen = candidates[index]

        extension = _extension(chosen["image_url"])
        filename = item.get("filename") or (
            f"{paper_id}-{re.sub(r'[^a-z0-9]+', '-', chosen['figure'].lower()).strip('-')}{extension}"
        )
        relative = f"assets/papers/{filename}"
        download(chosen["image_url"], output_dir / "papers" / filename)
        entries.append(
            {
                "file": relative,
                "kind": "paper-native",
                "theme": item["theme"],
                "paper_id": paper_id,
                "figure": chosen["figure"],
                "original_caption": chosen["original_caption"],
                "article_caption": item["article_caption"],
                "caption": item["article_caption"],
                "source": chosen["source_type"],
                "source_url": chosen["source_url"],
                "image_url": chosen["image_url"],
                "source_type": chosen["source_type"],
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True, type=pathlib.Path)
    parser.add_argument("--assets-dir", required=True, type=pathlib.Path)
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    args = parser.parse_args()
    entries = collect(args.selection, args.assets_dir)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest["visuals"] = [
        item for item in manifest.get("visuals", []) if item.get("kind") != "paper-native"
    ] + entries
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Collected {len(entries)} native paper figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
