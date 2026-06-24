#!/usr/bin/env python3
"""Fetch and normalize Hugging Face Daily Papers for an auditable digest."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Callable, Iterable


API_URL = "https://huggingface.co/api/daily_papers"
USER_AGENT = "writing-hf-weekly-digest/1.0"


def resolve_iso_week(value: str) -> tuple[dt.date, dt.date]:
    try:
        year_text, week_text = value.upper().split("-W", 1)
        start = dt.date.fromisocalendar(int(year_text), int(week_text), 1)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid ISO week: {value!r}; expected YYYY-Www") from exc
    return start, start + dt.timedelta(days=6)


def _date_from_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    return value[:10]


def _author_name(author: object) -> str | None:
    if not isinstance(author, dict):
        return None
    return author.get("name") or (author.get("user") or {}).get("fullname")


def normalize_entries(
    entries: Iterable[dict],
    *,
    start_date: str,
    end_date: str,
) -> list[dict]:
    """Normalize, date-filter, and deduplicate API entries by paper ID."""
    records: dict[str, dict] = {}
    for entry in entries:
        paper = entry.get("paper", entry) if isinstance(entry, dict) else {}
        if not isinstance(paper, dict):
            continue
        paper_id = paper.get("id")
        daily_date = _date_from_timestamp(paper.get("submittedOnDailyAt"))
        if not paper_id or not daily_date or not (start_date <= daily_date <= end_date):
            continue
        if paper_id in records:
            continue

        authors = [
            name
            for name in (_author_name(author) for author in paper.get("authors", []))
            if name
        ]
        organization = paper.get("organization")
        if isinstance(organization, dict):
            organization = organization.get("fullname") or organization.get("name")

        records[paper_id] = {
            "id": paper_id,
            "title": paper.get("title"),
            "authors": authors,
            "organization": organization,
            "published_at": paper.get("publishedAt"),
            "submitted_on_daily_at": paper.get("submittedOnDailyAt"),
            "daily_date": daily_date,
            "summary": paper.get("summary"),
            "ai_summary": paper.get("ai_summary"),
            "ai_keywords": paper.get("ai_keywords") or [],
            "upvotes": int(paper.get("upvotes") or 0),
            "github_repo": paper.get("githubRepo"),
            "project_page": paper.get("projectPage"),
            "hf_url": f"https://huggingface.co/papers/{paper_id}",
            "arxiv_url": f"https://arxiv.org/abs/{paper_id}",
        }
    return sorted(records.values(), key=lambda item: (-item["upvotes"], item["id"]))


def aggregate(records: Iterable[dict]) -> dict:
    records = list(records)
    daily_counts = Counter(record["daily_date"] for record in records)
    top = max(records, key=lambda item: item["upvotes"], default=None)
    return {
        "paper_count": len(records),
        "upvotes_total": sum(record["upvotes"] for record in records),
        "daily_counts": dict(sorted(daily_counts.items())),
        "top_paper": (
            {"id": top["id"], "title": top["title"], "upvotes": top["upvotes"]}
            if top
            else None
        ),
    }


def fetch_pages(
    fetch_page: Callable[[int, int], list[dict]],
    *,
    limit: int = 100,
) -> list[dict]:
    """Fetch numbered pages until the API returns a short or repeated page."""
    entries: list[dict] = []
    seen_signatures: set[tuple[str | None, ...]] = set()
    page = 0
    while True:
        batch = fetch_page(page, limit)
        if not isinstance(batch, list):
            raise ValueError("Hugging Face Daily Papers API did not return a JSON list")
        signature = tuple(
            (item.get("paper", item) or {}).get("id")
            for item in batch
            if isinstance(item, dict)
        )
        if batch and signature in seen_signatures:
            raise RuntimeError("Daily Papers API repeated a page; pagination stopped")
        seen_signatures.add(signature)
        entries.extend(batch)
        if len(batch) < limit:
            return entries
        page += 1


def load_json_with_retry(
    url: str,
    *,
    opener: Callable = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
    attempts: int = 3,
) -> object:
    """Load JSON, retrying transient connection failures with short backoff."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(attempts):
        try:
            with opener(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt + 1 == attempts:
                raise
            sleep(2**attempt)
    raise RuntimeError("unreachable")


def _request_json(params: dict[str, object]) -> list[dict]:
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    payload = load_json_with_retry(url)
    if not isinstance(payload, list):
        raise ValueError(f"Unexpected API response from {url}")
    return payload


def fetch_api_entries(
    *,
    week: str | None,
    start_date: str,
    end_date: str,
    sort: str,
    limit: int,
) -> list[dict]:
    if week:
        return fetch_pages(
            lambda page, page_limit: _request_json(
                {
                    "p": page,
                    "limit": page_limit,
                    "week": week,
                    "sort": sort,
                }
            ),
            limit=limit,
        )

    start = dt.date.fromisoformat(start_date)
    end = dt.date.fromisoformat(end_date)
    entries: list[dict] = []
    current = start
    while current <= end:
        date_text = current.isoformat()
        entries.extend(
            fetch_pages(
                lambda page, page_limit, date_text=date_text: _request_json(
                    {
                        "p": page,
                        "limit": page_limit,
                        "date": date_text,
                        "sort": sort,
                    }
                ),
                limit=limit,
            )
        )
        current += dt.timedelta(days=1)
    return entries


def write_bundle(
    output_dir: pathlib.Path,
    *,
    raw_entries: list[dict],
    records: list[dict],
    query: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
    source = {
        "retrieved_at": retrieved_at,
        "query": query,
        "entries": raw_entries,
    }
    normalized = {
        "retrieved_at": retrieved_at,
        "query": query,
        "statistics": aggregate(records),
        "papers": records,
    }
    (output_dir / "source.json").write_text(
        json.dumps(source, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "papers.json").write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    period = parser.add_mutually_exclusive_group(required=True)
    period.add_argument("--week", help="ISO week, for example 2026-W24")
    period.add_argument("--start", help="Inclusive YYYY-MM-DD start date")
    parser.add_argument("--end", help="Inclusive YYYY-MM-DD end date; required with --start")
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    parser.add_argument("--sort", choices=("publishedAt", "trending"), default="publishedAt")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if args.start and not args.end:
        parser.error("--end is required with --start")
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    return args


def main() -> int:
    args = parse_args()
    if args.week:
        start, end = resolve_iso_week(args.week)
        start_date, end_date = start.isoformat(), end.isoformat()
    else:
        start_date, end_date = args.start, args.end
        if dt.date.fromisoformat(start_date) > dt.date.fromisoformat(end_date):
            raise SystemExit("--start must not be after --end")

    query = {
        "week": args.week,
        "start_date": start_date,
        "end_date": end_date,
        "sort": args.sort,
    }
    raw_entries = fetch_api_entries(
        week=args.week,
        start_date=start_date,
        end_date=end_date,
        sort=args.sort,
        limit=args.limit,
    )
    records = normalize_entries(
        raw_entries,
        start_date=start_date,
        end_date=end_date,
    )
    write_bundle(
        args.output_dir,
        raw_entries=raw_entries,
        records=records,
        query=query,
    )
    print(
        f"Wrote {len(records)} unique papers for {start_date}..{end_date} "
        f"to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
