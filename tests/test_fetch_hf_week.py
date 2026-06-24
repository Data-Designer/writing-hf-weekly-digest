import importlib.util
import json
import pathlib
import tempfile
import unittest
import urllib.error


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_hf_week.py"


def load_module():
    spec = importlib.util.spec_from_file_location("fetch_hf_week", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FetchHfWeekTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        fixture_dir = ROOT / "tests" / "fixtures"
        cls.page0 = json.loads((fixture_dir / "page-0.json").read_text())
        cls.page1 = json.loads((fixture_dir / "page-1.json").read_text())

    def test_resolve_iso_week_to_inclusive_dates(self):
        start, end = self.module.resolve_iso_week("2026-W24")
        self.assertEqual(start.isoformat(), "2026-06-08")
        self.assertEqual(end.isoformat(), "2026-06-14")

    def test_normalize_filters_by_daily_submission_and_deduplicates(self):
        records = self.module.normalize_entries(
            self.page0 + self.page1,
            start_date="2026-06-08",
            end_date="2026-06-14",
        )
        self.assertEqual([record["id"] for record in records], ["2606.00001", "2606.00002"])
        self.assertEqual(records[0]["authors"], ["A. Author", "B. Author"])
        self.assertEqual(records[0]["hf_url"], "https://huggingface.co/papers/2606.00001")

    def test_aggregate_uses_frozen_records(self):
        records = self.module.normalize_entries(
            self.page0,
            start_date="2026-06-08",
            end_date="2026-06-14",
        )
        stats = self.module.aggregate(records)
        self.assertEqual(stats["paper_count"], 2)
        self.assertEqual(stats["upvotes_total"], 19)
        self.assertEqual(stats["top_paper"]["id"], "2606.00001")
        self.assertEqual(stats["daily_counts"], {"2026-06-09": 1, "2026-06-11": 1})

    def test_fetch_pages_stops_on_short_page(self):
        calls = []

        def fetch_page(page, limit):
            calls.append((page, limit))
            return self.page0 if page == 0 else []

        entries = self.module.fetch_pages(fetch_page, limit=2)
        self.assertEqual(entries, self.page0)
        self.assertEqual(calls, [(0, 2), (1, 2)])

    def test_write_bundle_preserves_raw_and_normalized_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = pathlib.Path(tmp)
            records = self.module.normalize_entries(
                self.page0,
                start_date="2026-06-08",
                end_date="2026-06-14",
            )
            self.module.write_bundle(
                output,
                raw_entries=self.page0,
                records=records,
                query={"start_date": "2026-06-08", "end_date": "2026-06-14"},
            )
            source = json.loads((output / "source.json").read_text())
            papers = json.loads((output / "papers.json").read_text())
            self.assertEqual(source["query"]["start_date"], "2026-06-08")
            self.assertEqual(len(source["entries"]), 2)
            self.assertEqual(papers["statistics"]["paper_count"], 2)
            self.assertEqual(len(papers["papers"]), 2)

    def test_load_json_retries_transient_url_errors(self):
        attempts = []

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'[{"paper": {"id": "2606.00001"}}]'

        def opener(request, timeout):
            attempts.append((request.full_url, timeout))
            if len(attempts) < 3:
                raise urllib.error.URLError("transient TLS EOF")
            return Response()

        payload = self.module.load_json_with_retry(
            "https://example.test/api",
            opener=opener,
            sleep=lambda _: None,
            attempts=3,
        )
        self.assertEqual(payload[0]["paper"]["id"], "2606.00001")
        self.assertEqual(len(attempts), 3)


if __name__ == "__main__":
    unittest.main()
