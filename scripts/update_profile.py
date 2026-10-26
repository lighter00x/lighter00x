"""Build the project dashboard from public GitHub metadata."""

from collections import Counter
from html import escape
from pathlib import Path
import json
import os
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
USER = "lighter00x"
COLORS = {"Python": "#3979f6", "HTML": "#f28b53", "JavaScript": "#e4bd3e", "TypeScript": "#36a4e5", "Jupyter Notebook": "#9c6deb"}


def request(url):
    headers = {"User-Agent": "lighter00x-profile", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
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
    return json.loads(request("https://api.github.com" + path))


def public_repositories():
    repositories = []
    page = 1
    while True:
        batch = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        repositories.extend(repo for repo in batch if not repo.get("private", False))
        if len(batch) < 100:
            return repositories
        page += 1


def svg_text(x, y, text, size=12, color="#6b7b96", **attrs):
    extra = " ".join(f'{name.replace("_", "-")}="{escape(str(value), quote=True)}"' for name, value in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(text))}</text>'


def dashboard(repositories):
    nonfork = [repo for repo in repositories if not repo.get("fork")]
    languages = Counter(repo["language"] for repo in nonfork if repo.get("language"))
    groups = languages.most_common(3)
    other = sum(languages.values()) - sum(count for _, count in groups)
    if other:
        groups.append(("Other", other))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="108" viewBox="0 0 960 108" role="img" aria-labelledby="title desc">',
        '<title id="title">Repository overview for lighter00x</title>',
        '<desc id="desc">Public repository count and primary languages by non-fork repository. No activity or commit ranking.</desc>',
        '<rect x=".5" y=".5" width="959" height="107" rx="10" fill="#ffffff" stroke="#e7edf6"/>',
        '<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">',
        svg_text(24, 27, "REPOSITORY OVERVIEW", 9, "#7a8aa3", letter_spacing=1.2),
        svg_text(24, 55, f"{len(repositories)} public repositories", 17, "#30476b", font_weight=500),
        svg_text(24, 81, "A small snapshot of what I build.", 10, "#8491a6"),
        '<path d="M333 25V83" stroke="#e7edf6"/>',
    ]
    total = max(sum(languages.values()), 1)
    position = 360
    parts.append('<rect x="360" y="32" width="570" height="5" rx="2.5" fill="#edf2fa"/>')
    for index, (name, count) in enumerate(groups):
        width = 570 * count / total
        color = COLORS.get(name, "#9aacc5")
        parts.append(f'<rect x="{position:.2f}" y="32" width="{width:.2f}" height="5" fill="{color}"/>')
        x = 360 + index * 145
        label = name if len(name) <= 15 else name[:14] + "…"
        parts += [f'<circle cx="{x+3}" cy="66" r="3" fill="{color}"/>', svg_text(x+14, 70, f"{label} · {count}", 10, "#6b7b96")]
        position += width
    if not groups:
        parts.append(svg_text(360, 70, "Primary languages will appear as projects grow.", 11))
    parts += [svg_text(360, 91, "By primary language per non-fork public repository", 8, "#94a0b2"), '</g></svg>']
    result = "\n".join(parts) + "\n"
    ET.fromstring(result)
    return result


def main():
    repositories = public_repositories()
    svg = dashboard(repositories)
    (ROOT / "assets" / "projects.svg").write_text(svg, encoding="utf-8")
    print(f"Updated compact overview: {len(repositories)} public repositories.")


if __name__ == "__main__":
    main()
