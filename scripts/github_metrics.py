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


def request_json(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-profile-metrics",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
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
        cells.append(f'<text x="{x}" y="53" font-size="32" font-weight="700">{value:,}</text>')
        cells.append(f'<text x="{x}" y="81" font-size="16">{label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="130" viewBox="0 0 860 130" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">Public GitHub API snapshot. Forks excluded. Last successful refresh: {stamp}.</desc>
  <rect x="1" y="1" width="858" height="128" rx="12" fill="#F4F7FF" stroke="#CAD6FF"/>
  <g font-family="Verdana, Geneva, sans-serif" fill="#16275C">
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


if __name__ == "__main__":
    try:
        generate(os.environ.get("PROFILE_USERNAME", "YACINBK"))
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError, OSError) as error:
        print(f"Metrics refresh failed; previous SVG preserved: {error}", file=sys.stderr)
        sys.exit(1)
