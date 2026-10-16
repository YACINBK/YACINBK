import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from xml.etree import ElementTree

from scripts.github_metrics import (
    collect, collect_activity, generate, generate_activity,
    render, render_activity, request_json,
)


def repo(identifier, stars=1):
    return dict(id=identifier, stargazers_count=stars, fork=False, private=False)


class MetricsTests(unittest.TestCase):
    def test_paginates_and_excludes_forks_and_private_repos(self):
        calls = []
        first = [repo(i) for i in range(100)]
        first[0]["fork"] = True
        first[1]["private"] = True

        def fetch(path):
            calls.append(path)
            if path == "/users/YACINBK":
                return {"followers": 7}
            return first if path.endswith("&page=1") else [repo(100, stars=4)]

        self.assertEqual(collect("YACINBK", fetch), (99, 102, 7))
        self.assertEqual(len(calls), 3)
        self.assertTrue(calls[-1].endswith("page=2"))

    def test_failed_or_invalid_fetch_preserves_previous_asset(self):
        responses = [URLError("offline"), {"message": "API rate limit exceeded"},
                     {"followers": -1}, {"followers": True}]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "metrics.svg"
            for response in responses:
                with self.subTest(response=response):
                    output.write_text("previous valid snapshot")

                    def fetch(path):
                        if isinstance(response, Exception):
                            raise response
                        return response

                    with self.assertRaises((URLError, ValueError, KeyError)):
                        generate("YACINBK", output, fetch)
                    self.assertEqual(output.read_text(), "previous valid snapshot")

    def test_later_page_failure_does_not_publish_partial_counts(self):
        def fetch(path):
            if path == "/users/YACINBK":
                return {"followers": 7}
            if path.endswith("&page=1"):
                return [repo(i) for i in range(100)]
            raise URLError("second page unavailable")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "metrics.svg"
            output.write_text("previous valid snapshot")
            with self.assertRaises(URLError):
                generate("YACINBK", output, fetch)
            self.assertEqual(output.read_text(), "previous valid snapshot")

    def test_success_produces_accessible_svg_with_timestamp(self):
        svg = render("A&B", (12, 1234, 5), datetime(2026, 10, 16, 12, tzinfo=timezone.utc))
        root = ElementTree.fromstring(svg)
        self.assertEqual(root.attrib["role"], "img")
        self.assertIn("A&amp;B", svg)
        self.assertIn("1,234", svg)
        self.assertIn("16 Oct 2026, 12:00 UTC", svg)

    def test_empty_account_is_a_valid_snapshot(self):
        def fetch(path):
            return [] if "/repos?" in path else {"followers": 0}

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "metrics.svg"
            generate("YACINBK", output, fetch)
            ElementTree.parse(output)
            self.assertIn("0 original public repositories", output.read_text())

    @patch("scripts.github_metrics.time.sleep")
    @patch("scripts.github_metrics.urlopen")
    def test_transient_failures_retry_but_auth_failures_do_not(self, open_url, sleep):
        open_url.side_effect = HTTPError("https://api.github.com", 503, "unavailable", {}, None)
        with self.assertRaises(HTTPError):
            request_json("/users/YACINBK")
        self.assertEqual(open_url.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        open_url.reset_mock()
        sleep.reset_mock()
        open_url.side_effect = HTTPError("https://api.github.com", 401, "unauthorized", {}, None)
        with self.assertRaises(HTTPError):
            request_json("/users/YACINBK")
        self.assertEqual(open_url.call_count, 1)
        sleep.assert_not_called()


def calendar(days):
    return {"data": {"user": {"contributionsCollection": {
        "contributionCalendar": {"weeks": [{"contributionDays": days}]}
    }}}}


class ActivityTests(unittest.TestCase):
    def test_aggregates_calendar_and_uses_query_variables(self):
        def fetch(path, payload):
            self.assertEqual(path, "/graphql")
            self.assertEqual(payload["variables"], {"login": "YACINBK"})
            return calendar([
                {"date": "2026-10-15", "contributionCount": 2},
                {"date": "2026-10-16", "contributionCount": 3},
            ])

        self.assertEqual(collect_activity("YACINBK", fetch), ([5], "2026-10-15", "2026-10-16"))

    def test_api_and_calendar_errors_preserve_previous_graph(self):
        invalid = [
            {"errors": [{"message": "Resource unavailable"}]},
            calendar([]),
            calendar([{"date": "2026-10-16", "contributionCount": -1}]),
            calendar([
                {"date": "2026-10-14", "contributionCount": 0},
                {"date": "2026-10-16", "contributionCount": 0},
            ]),
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "activity.svg"
            for response in invalid:
                with self.subTest(response=response):
                    output.write_text("previous graph")
                    with self.assertRaises(ValueError):
                        generate_activity("YACINBK", output, lambda path, payload: response)
                    self.assertEqual(output.read_text(), "previous graph")

    def test_zero_activity_renders_valid_graph_in_original_palette(self):
        svg = render_activity("YACINBK", ([0, 0], "2026-10-05", "2026-10-16"),
                              datetime(2026, 10, 16, 12, tzinfo=timezone.utc))
        root = ElementTree.fromstring(svg)
        self.assertIn("0 contributions", svg)
        self.assertIn("#8FFF52", svg)
        self.assertIn("#050705", svg)
        line = root.find(".//{http://www.w3.org/2000/svg}polyline")
        coordinates = [tuple(map(float, point.split(","))) for point in line.attrib["points"].split()]
        self.assertEqual(coordinates[0][1], coordinates[1][1])
        self.assertGreater(coordinates[1][0], coordinates[0][0])
        self.assertTrue(all(0 <= x <= 860 and 0 <= y <= 320 for x, y in coordinates))


if __name__ == "__main__":
    unittest.main()
