"""Build the profile from public GitHub metadata and the owner's Atom feed."""

from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import os
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
USER = "lighter00x"
BLOG = "https://lighter00x.github.io/feed.xml"
COLORS = {"Python": "#82ac8b", "HTML": "#d9b67c", "JavaScript": "#b6bd72", "TypeScript": "#7ca7b3", "Jupyter Notebook": "#bd9bc0"}


def request(url, github=False):
    headers = {"User-Agent": "lighter00x-profile", "Accept": "application/vnd.github+json" if github else "application/atom+xml"}
    token = os.environ.get("GITHUB_TOKEN")
    if github and token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def api(path):
    return json.loads(request("https://api.github.com" + path, github=True))


def public_repositories():
    repositories = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        repositories.extend(repo for repo in batch if not repo.get("private", False))
        if len(batch) < 100:
            return repositories
        page += 1


def public_events():
    events = []
    for page in range(1, 4):
        batch = api(f"/users/{USER}/events/public?per_page=100&page={page}")
        events.extend(batch)
        if len(batch) < 100:
            break
    return events


def svg_text(x, y, text, size=12, color="#707d73", **attrs):
    extra = " ".join(f'{name.replace("_", "-")}="{escape(str(value), quote=True)}"' for name, value in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(text))}</text>'


def dashboard(repositories, events, now):
    nonfork = [repo for repo in repositories if not repo.get("fork")]
    languages = Counter(repo["language"] for repo in nonfork if repo.get("language"))
    today = now.date()
    first_week = today - timedelta(days=today.weekday(), weeks=11)
    buckets = [0] * 12
    for event in events:
        date = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).date()
        week = (date - first_week).days // 7
        if 0 <= week < len(buckets):
            buckets[week] += 1
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-labelledby="title desc">',
        '<title id="title">Public project signals for lighter00x</title>',
        '<desc id="desc">Public repository counts, primary languages by repository, and a sample of recent public events. Not a full contribution calendar.</desc>',
        '<rect x=".5" y=".5" width="959" height="359" rx="14" fill="#f6f5ef" stroke="#dedfd5"/>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">',
        svg_text(30, 31, "PROJECT SIGNALS", 10, "#52745c", letter_spacing=2),
        svg_text(730, 31, f"UPDATED {now:%Y.%m.%d} UTC", 9, letter_spacing=1),
    ]
    for index, (label, value) in enumerate((("PUBLIC REPOSITORIES", len(repositories)), ("NON-FORK REPOSITORIES", len(nonfork)), ("PRIMARY LANGUAGES", len(languages)))):
        x = 30 + index * 310
        parts += [svg_text(x, 83, value, 34, "#244737", font_weight=600), svg_text(x, 106, label, 9, letter_spacing=1.1)]
    parts += ['<path d="M30 129H930M476 152V305" stroke="#dedfd5"/>', svg_text(30, 161, "WHAT THE PROJECTS ARE WRITTEN IN", 9, "#52745c", letter_spacing=1), svg_text(505, 161, "RECENT PUBLIC ACTIVITY", 9, "#52745c", letter_spacing=1)]
    top_languages = languages.most_common(4)
    if not top_languages:
        parts.append(svg_text(30, 211, "No primary language reported yet."))
    for index, (name, count) in enumerate(top_languages):
        y = 195 + index * 28
        width = 205 * count / max(languages.values())
        parts += [svg_text(30, y, name, 11, "#364e3e"), f'<rect x="180" y="{y-8}" width="205" height="6" rx="3" fill="#e6e9df"/>', f'<rect x="180" y="{y-8}" width="{width:.1f}" height="6" rx="3" fill="{COLORS.get(name, "#91a79a")}"/>', svg_text(404, y, f"{count} repos", 10)]
    maximum = max(max(buckets), 1)
    for index, count in enumerate(buckets):
        x = 510 + index * 34
        height = max(4, 97 * count / maximum)
        parts += [f'<rect x="{x}" y="{282-height:.1f}" width="22" height="{height:.1f}" rx="3" fill="{"#477b59" if count else "#e3e8db"}"><title>{first_week + timedelta(weeks=index)}: {count} public events</title></rect>']
    parts += [svg_text(510, 301, f"{first_week:%m.%d}" , 9), svg_text(845, 301, "THIS WEEK", 9), '<path d="M30 320H930" stroke="#dedfd5"/>', svg_text(30, 343, "Languages = primary language per non-fork public repository.", 9), svg_text(505, 343, f"12 weeks / sample of {len(events)} latest public events / not commits", 9), '</g></svg>']
    result = "\n".join(parts) + "\n"
    ET.fromstring(result)
    return result


def blog_links():
    root = ET.fromstring(request(BLOG))
    namespace = {"a": "http://www.w3.org/2005/Atom"}
    links = []
    for entry in root.findall("a:entry", namespace)[:3]:
        title = " ".join((entry.findtext("a:title", default="", namespaces=namespace)).split())
        title = re.sub(r"([\\\[\]])", r"\\\1", title)
        link = next((node.attrib.get("href", "") for node in entry.findall("a:link", namespace) if node.attrib.get("rel", "alternate") == "alternate"), "")
        if not link.startswith("https://lighter00x.github.io/"):
            raise ValueError("Unexpected blog link origin")
        link = "https://lighter00x.github.io/" + link.removeprefix("https://lighter00x.github.io/").lstrip("/")
        links.append(f"- [{title}]({link})")
    if not links:
        raise ValueError("Blog feed contains no entries")
    return "\n".join(links)


def main():
    repositories = public_repositories()
    events = public_events()
    svg = dashboard(repositories, events, datetime.now(timezone.utc))
    links = blog_links()
    path = ROOT / "README.md"
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(r"<!-- BLOG:START -->[\s\S]*?<!-- BLOG:END -->", "<!-- BLOG:START -->\n" + links + "\n<!-- BLOG:END -->", content)
    if count != 1:
        raise ValueError("Expected one blog section")
    (ROOT / "assets" / "projects.svg").write_text(svg, encoding="utf-8")
    path.write_text(updated, encoding="utf-8")
    print(f"Updated profile: {len(repositories)} public repositories; {len(events)} sampled public events; 3 blog links.")


if __name__ == "__main__":
    main()
