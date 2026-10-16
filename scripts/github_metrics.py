"""Generate public GitHub counts; preserve the last good SVG on API failure."""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OUTPUT = Path(__file__).resolve().parents[1] / "assets/generated/github-metrics.svg"
ACTIVITY_OUTPUT = OUTPUT.with_name("activity-graph.svg")


def request_json(path, payload=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-profile-metrics",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(f"https://api.github.com{path}", headers=headers, data=data)
    for attempt in range(3):
        try:
            with urlopen(request, timeout=20) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError("GitHub returned an invalid count")
    return value


def collect(username, fetch=request_json):
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", username):
        raise ValueError("Invalid GitHub username")
    user = fetch(f"/users/{username}")
    followers = count(user["followers"])
    repositories = {}
    page = 1
    while True:
        batch = fetch(f"/users/{username}/repos?type=owner&sort=full_name&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("GitHub returned an invalid repository list")
        for repo in batch:
            if type(repo["fork"]) is not bool or type(repo["private"]) is not bool:
                raise ValueError("GitHub returned invalid repository visibility")
            if not repo["fork"] and not repo["private"]:
                repositories[count(repo["id"])] = count(repo["stargazers_count"])
        if len(batch) < 100:
            break
        page += 1
    return len(repositories), sum(repositories.values()), followers


def render(username, metrics, updated):
    repositories, stars, followers = (count(value) for value in metrics)
    title = escape(f"{username}: {repositories} original public repositories, {stars} stars, {followers} followers")
    stamp = escape(updated.astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC"))
    cells = []
    for x, value, label in zip((28, 314, 600), (repositories, stars, followers),
                               ("Original public repos", "Stars on those repos", "Followers")):
        cells.append(f'<text x="{x}" y="53" fill="#8FFF52" font-size="32" font-weight="700">{value:,}</text>')
        cells.append(f'<text x="{x}" y="81" fill="#E5F5E5" font-size="16">{label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="130" viewBox="0 0 860 130" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Public GitHub API snapshot. Forks excluded. Last successful refresh: {stamp}.</desc>
  <rect width="860" height="130" rx="16" fill="#050705"/>
  <rect x="12" y="12" width="836" height="106" rx="12" fill="none" stroke="#1f2b22"/>
  <g font-family="Segoe UI, Inter, Arial, sans-serif" fill="#8CA08A">
    {''.join(cells)}
    <text x="28" y="111" font-size="12">Last successful refresh: {stamp} · Forks excluded</text>
  </g>
</svg>
'''


def generate(username, output=OUTPUT, fetch=request_json):
    metrics = collect(username, fetch)
    svg = render(username, metrics, datetime.now(timezone.utc))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".svg.tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(output)


def collect_activity(username, fetch=request_json):
    payload = {
        "query": """query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                weeks { contributionDays { date contributionCount } }
              }
            }
          }
        }""",
        "variables": {"login": username},
    }
    result = fetch("/graphql", payload)
    if result.get("errors"):
        raise ValueError("GitHub contribution query failed")
    weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    if not isinstance(weeks, list) or not 1 <= len(weeks) <= 54:
        raise ValueError("Invalid contribution calendar")
    totals = []
    all_dates = []
    for week in weeks:
        days = week["contributionDays"]
        if not isinstance(days, list) or not 1 <= len(days) <= 7:
            raise ValueError("Invalid contribution week")
        dates = [datetime.strptime(day["date"], "%Y-%m-%d").date() for day in days]
        all_dates.extend(dates)
        totals.append(sum(count(day["contributionCount"]) for day in days))
    if any((right - left).days != 1 for left, right in zip(all_dates, all_dates[1:])):
        raise ValueError("Contribution calendar must contain consecutive days")
    return totals, all_dates[0].isoformat(), all_dates[-1].isoformat()


def render_activity(username, activity, updated):
    totals, start, end = activity
    maximum = max(max(totals), 1)
    points = [(52 + i * 754 / max(len(totals) - 1, 1), 220 - total / maximum * 136)
              for i, total in enumerate(totals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{points[0][0]:.1f},220 {line} {points[-1][0]:.1f},220"
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#C5FF00"/>' for x, y in points)
    stamp = updated.astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    title = escape(f"{username}: weekly GitHub contributions, {start} to {end}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="284" viewBox="0 0 860 284" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{sum(totals):,} contributions in the returned calendar. Weekly totals; first and last weeks may be partial. Last successful refresh: {stamp}.</desc>
  <rect width="860" height="284" rx="16" fill="#050705"/>
  <rect x="12" y="12" width="836" height="260" rx="12" fill="none" stroke="#1f2b22"/>
  <g font-family="Segoe UI, Inter, Arial, sans-serif">
    <text x="28" y="38" fill="#8FFF52" font-size="10" letter-spacing="2">// CONTRIBUTION RHYTHM</text>
    <text x="28" y="63" fill="#E5F5E5" font-size="18" font-weight="700">{sum(totals):,} contributions over the past year</text>
    <path d="M52 84h754M52 152h754M52 220h754" stroke="#1f2b22" fill="none"/>
    <text x="28" y="88" fill="#8CA08A" font-size="10">{maximum}</text>
    <text x="28" y="224" fill="#8CA08A" font-size="10">0</text>
    <polygon points="{area}" fill="#132015"/>
    <polyline points="{line}" fill="none" stroke="#8FFF52" stroke-width="2" stroke-linejoin="round"/>
    {dots}
    <text x="52" y="240" fill="#8CA08A" font-size="11">{escape(start)}</text>
    <text x="806" y="240" fill="#8CA08A" font-size="11" text-anchor="end">{escape(end)}</text>
    <text x="28" y="262" fill="#8CA08A" font-size="10">Weekly totals · Edge weeks may be partial · Last successful refresh: {stamp}</text>
  </g>
</svg>
'''


def generate_activity(username, output=ACTIVITY_OUTPUT, fetch=request_json):
    activity = collect_activity(username, fetch)
    svg = render_activity(username, activity, datetime.now(timezone.utc))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".svg.tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(output)


if __name__ == "__main__":
    try:
        generator = generate_activity if "--activity" in sys.argv else generate
        generator(os.environ.get("PROFILE_USERNAME", "YACINBK"))
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError, OSError) as error:
        print(f"Metrics refresh failed; previous SVG preserved: {error}", file=sys.stderr)
        sys.exit(1)
