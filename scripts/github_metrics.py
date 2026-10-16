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
    icons = (
        '<rect x="3" y="2" width="17" height="21" rx="3"/><path d="M3 18h17M8 6v7m4-7h4"/>',
        '<path d="M12 2l3.1 6.3 7 .9-5.1 5 1.2 7-6.2-3.3-6.2 3.3 1.2-7-5.1-5 7-.9z"/>',
        '<circle cx="9" cy="7" r="4"/><path d="M2 22v-3a7 7 0 0 1 14 0v3M17 3a4 4 0 0 1 0 8m3 11v-3a7 7 0 0 0-3-5"/>',
    )
    for x, value, label, note, color, icon in zip(
        (28, 305, 582), (repositories, stars, followers),
        ("Repositories", "Stars", "Followers"),
        ("Original public repositories", "Across original public repositories", "Following my work on GitHub"),
        ("#8FFF52", "#C5FF00", "#00D8FF"), icons,
    ):
        cells.append(f'''<g>
      <rect x="{x}" y="48" width="250" height="112" rx="10" fill="#0a120c" stroke="#1f2b22"/>
      <path d="M{x + 16} 48h42" stroke="{color}" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
      <text x="{x + 16}" y="74" fill="#E5F5E5" font-size="12" font-weight="600">{label}</text>
      <g transform="translate({x + 210} 64)" fill="none" stroke="{color}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.7">{icon}</g>
      <text x="{x + 16}" y="117" fill="{color}" font-size="36" font-weight="700">{value:,}</text>
      <text x="{x + 16}" y="142" fill="#8CA08A" font-size="11">{note}</text>
    </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="206" viewBox="0 0 860 206" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Public GitHub API snapshot. Forks excluded. Last successful refresh: {stamp}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#0b0f0c"/><stop offset="50%" stop-color="#111a12"/><stop offset="100%" stop-color="#0b0f0c"/>
    </linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8FFF52" stop-opacity="0"/><stop offset="50%" stop-color="#8FFF52" stop-opacity="0.35"/><stop offset="100%" stop-color="#00D8FF" stop-opacity="0"/>
    </linearGradient>
    <style>@media (prefers-reduced-motion: reduce) {{ .ambient {{ display: none; }} }}</style>
  </defs>
  <rect width="860" height="206" rx="16" fill="#050705"/>
  <rect width="860" height="206" rx="16" fill="url(#bg)" opacity="0.55"/>
  <rect class="ambient" width="860" height="206" rx="16" fill="url(#glow)" opacity="0.12">
    <animate attributeName="opacity" values="0.08;0.22;0.08" dur="6s" repeatCount="indefinite"/>
  </rect>
  <rect x="12" y="12" width="836" height="182" rx="12" fill="none" stroke="#1f2b22"/>
  <g font-family="Segoe UI, Inter, Arial, sans-serif" fill="#8CA08A">
    <text x="28" y="32" fill="#8FFF52" font-size="10" letter-spacing="2">// PUBLIC SNAPSHOT</text>
    <text x="832" y="32" font-size="10" text-anchor="end" letter-spacing="1">6H REFRESH CYCLE</text>
    {''.join(cells)}
    <text x="28" y="183" font-size="10">Last successful refresh: {stamp}</text>
    <text x="832" y="183" font-size="10" text-anchor="end">PUBLIC DATA · FORKS EXCLUDED</text>
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
    points = [(64 + i * 738 / max(len(totals) - 1, 1), 238 - total / maximum * 126)
              for i, total in enumerate(totals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{points[0][0]:.1f},238 {line} {points[-1][0]:.1f},238"
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#C5FF00"/>' for x, y in points)
    last_x, last_y = points[-1]
    stamp = updated.astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    title = escape(f"{username}: weekly GitHub contributions, {start} to {end}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="320" viewBox="0 0 860 320" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{sum(totals):,} contributions in the returned calendar. Weekly totals; first and last weeks may be partial. Last successful refresh: {stamp}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#0b0f0c"/><stop offset="50%" stop-color="#111a12"/><stop offset="100%" stop-color="#0b0f0c"/>
    </linearGradient>
    <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8FFF52" stop-opacity="0.25"/><stop offset="100%" stop-color="#8FFF52" stop-opacity="0.015"/>
    </linearGradient>
    <style>@media (prefers-reduced-motion: reduce) {{ .ambient {{ display: none; }} }}</style>
  </defs>
  <rect width="860" height="320" rx="16" fill="#050705"/>
  <rect width="860" height="320" rx="16" fill="url(#bg)" opacity="0.55"/>
  <rect x="12" y="12" width="836" height="296" rx="12" fill="none" stroke="#1f2b22"/>
  <g font-family="Segoe UI, Inter, Arial, sans-serif">
    <text x="28" y="32" fill="#8FFF52" font-size="10" letter-spacing="2">// CONTRIBUTION RHYTHM</text>
    <text x="28" y="65" fill="#E5F5E5" font-size="22" font-weight="700">{sum(totals):,} contributions over the past year</text>
    <rect x="710" y="44" width="122" height="26" rx="6" fill="#0e160f" stroke="#1f2b22"/>
    <circle cx="724" cy="57" r="3" fill="#C5FF00"/>
    <text x="736" y="61" fill="#8CA08A" font-size="10">WEEKLY TOTALS</text>
    <rect x="28" y="88" width="804" height="172" rx="10" fill="#0a120c" stroke="#1f2b22"/>
    <path d="M64 112h738M64 175h738M64 238h738" stroke="#1f2b22" stroke-dasharray="3 5" fill="none"/>
    <text x="54" y="116" fill="#8CA08A" font-size="10" text-anchor="end">{maximum}</text>
    <text x="54" y="242" fill="#8CA08A" font-size="10" text-anchor="end">0</text>
    <polygon points="{area}" fill="url(#area)"/>
    <polyline points="{line}" fill="none" stroke="#8FFF52" stroke-width="7" opacity="0.08" stroke-linejoin="round"/>
    <polyline points="{line}" fill="none" stroke="#8FFF52" stroke-width="2" stroke-linejoin="round"/>
    {dots}
    <circle class="ambient" cx="{last_x:.1f}" cy="{last_y:.1f}" r="7" fill="none" stroke="#00D8FF" opacity="0.3">
      <animate attributeName="r" values="4;9;4" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;0.1;0.5" dur="4s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="3" fill="#00D8FF"/>
    <text x="64" y="277" fill="#8CA08A" font-size="11">{escape(start)}</text>
    <text x="802" y="277" fill="#8CA08A" font-size="11" text-anchor="end">{escape(end)}</text>
    <text x="28" y="298" fill="#8CA08A" font-size="10">Last successful refresh: {stamp}</text>
    <text x="832" y="298" fill="#8CA08A" font-size="10" text-anchor="end">EDGE WEEKS MAY BE PARTIAL</text>
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
