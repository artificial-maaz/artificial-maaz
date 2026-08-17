#!/usr/bin/env python3
"""
Generate self-owned stat SVGs (contributions + languages) from the GitHub
GraphQL API, styled to match the rooftop hero (indigo / mono). No third-party
image services, so nothing can rate-limit or go dark.

Env:
  GH_TOKEN  GitHub token (Actions GITHUB_TOKEN, or a PAT for private stats)
  GH_USER   GitHub login (default: artificial-maaz)

Writes: assets/stats-contrib.svg, assets/stats-langs.svg
"""
import os
import json
import math
import html
import urllib.request

TOKEN = os.environ["GH_TOKEN"]
USER = os.environ.get("GH_USER", "artificial-maaz")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

QUERY = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ contributionCount date } }
      }
    }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{ languages(first:10, orderBy:{field:SIZE, direction:DESC}){
        edges{ size node{ name color } } } }
    }
  }
}
"""


def gql():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": "bearer " + TOKEN,
            "Content-Type": "application/json",
            "User-Agent": USER,
        },
    )
    with urllib.request.urlopen(req) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    return payload["data"]["user"]


def compute(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    total = cal["totalContributions"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]

    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            current += 1
        else:
            break

    agg, colors = {}, {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            agg[n] = agg.get(n, 0) + e["size"]
            colors[n] = e["node"]["color"] or "#8a8f9e"
    total_bytes = sum(agg.values()) or 1
    langs = sorted(agg.items(), key=lambda kv: -kv[1])[:6]
    langs = [(n, s, 100.0 * s / total_bytes, colors[n]) for n, s in langs]

    return {
        "total": total,
        "current": current,
        "longest": longest,
        "repos": user["repositories"]["totalCount"],
        "langs": langs,
    }


FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SURFACE = "#0e1430"


def card_open(w, h):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">'
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" '
        f'fill="{SURFACE}" stroke="#26305a"/>'
    )


def stats_contrib(s):
    w, h = 300, 150
    svg = [card_open(w, h)]
    svg.append(f'<text x="20" y="52" font-size="42" font-weight="700" fill="#e6ebff">{s["total"]}</text>')
    svg.append('<text x="22" y="70" font-size="11" fill="#8b9ad6">contributions in the last year</text>')
    rows = [("current streak", f'{s["current"]}d'),
            ("longest streak", f'{s["longest"]}d'),
            ("public repos", str(s["repos"]))]
    y = 96
    for label, val in rows:
        svg.append(f'<text x="20" y="{y}" font-size="12" fill="#adbad6">{label}</text>')
        svg.append(f'<text x="280" y="{y}" font-size="12" font-weight="700" fill="#e6ebff" text-anchor="end">{val}</text>')
        y += 18
    svg.append("</svg>")
    return "".join(svg)


def _pt(cx, cy, r, a):
    return f"{cx + r*math.cos(a):.2f} {cy + r*math.sin(a):.2f}"

def _wedge(cx, cy, ro, ri, a0, a1):
    large = 1 if (a1 - a0) > math.pi else 0
    return (f'M{_pt(cx,cy,ro,a0)} A{ro} {ro} 0 {large} 1 {_pt(cx,cy,ro,a1)} '
            f'L{_pt(cx,cy,ri,a1)} A{ri} {ri} 0 {large} 0 {_pt(cx,cy,ri,a0)} Z')

def stats_langs(s):
    w, h = 300, 150
    svg = [card_open(w, h)]
    svg.append('<text x="20" y="26" font-size="12" fill="#8b9ad6">most used languages</text>')

    langs = s["langs"]
    cx, cy, ro, ri = 64, 88, 40, 25
    total = sum(p for _n, _sz, p, _c in langs) or 100.0

    a = -math.pi / 2                       # start at 12 o'clock
    for name, _sz, pct, color in langs:
        sweep = 2 * math.pi * (pct / total)
        if sweep <= 0:
            continue
        if sweep >= 2 * math.pi - 1e-6:    # single language -> full ring
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{(ro+ri)/2}" fill="none" '
                       f'stroke="{color}" stroke-width="{ro-ri}"/>')
            break
        svg.append(f'<path d="{_wedge(cx,cy,ro,ri,a,a+sweep)}" fill="{color}" '
                   f'stroke="{SURFACE}" stroke-width="2" stroke-linejoin="round"/>')
        a += sweep

    # hero: the leading language sits in the hole
    if langs:
        top, _sz, tpct, _c = langs[0]
        svg.append(f'<text x="{cx}" y="{cy-1}" font-size="14" font-weight="700" fill="#e6ebff" '
                   f'text-anchor="middle">{tpct:.0f}%</text>')
        svg.append(f'<text x="{cx}" y="{cy+12}" font-size="8" fill="#8b9ad6" '
                   f'text-anchor="middle">{html.escape(top.lower())}</text>')

    # legend — identity is never colour alone
    y = 46
    for name, _sz, pct, color in langs:
        svg.append(f'<rect x="124" y="{y-7}" width="8" height="8" rx="2" fill="{color}"/>')
        svg.append(f'<text x="139" y="{y}" font-size="10" fill="#adbad6">{html.escape(name.lower())}</text>')
        svg.append(f'<text x="282" y="{y}" font-size="10" font-weight="700" fill="#e6ebff" '
                   f'text-anchor="end">{pct:.0f}%</text>')
        y += 17

    svg.append("</svg>")
    return "".join(svg)


def main():
    s = compute(gql())
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "stats-contrib.svg"), "w") as f:
        f.write(stats_contrib(s))
    with open(os.path.join(OUT, "stats-langs.svg"), "w") as f:
        f.write(stats_langs(s))
    print("wrote stats:", s["total"], "contributions,", len(s["langs"]), "languages")


if __name__ == "__main__":
    main()
