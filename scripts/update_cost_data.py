#!/usr/bin/env python3
"""
Refresh proposed-system cost estimates from open news via the Tavily API.

Writes data/proposed_systems.json, whose entries OVERRIDE the seed figures in
osint_cad.doctrine.cost_benefit. Designed for CI (see .github/workflows/update-cost-data.yml):

  - Reads the API key from the TAVILY_API_KEY environment variable (a GitHub Actions secret).
  - If the key is absent (e.g. local run with no key), it is a graceful NO-OP and exits 0,
    so CI never fails just because the secret isn't configured.
  - Updates `sources` and `last_updated` for every system; updates `unit_cost_musd` ONLY when
    a cost figure can be confidently parsed from the news text (otherwise the seed value
    stands). It does not fabricate numbers.

Usage:  TAVILY_API_KEY=... python scripts/update_cost_data.py
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

from osint_cad.doctrine.cost_benefit import seed_systems

TAVILY_URL = "https://api.tavily.com/search"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "proposed_systems.json")

# "$3.3 billion", "$30 million", "1.2bn", etc. near a cost-ish word.
_COST_RE = re.compile(
    r"(?:cost|price|unit|procure\w*|each|per)[^.$]{0,60}?\$?\s*"
    r"(\d+(?:\.\d+)?)\s*(billion|bn|million|m)\b",
    re.IGNORECASE,
)


def _tavily_search(query: str, api_key: str, max_results: int = 5) -> dict:
    payload = json.dumps({
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "topic": "news",
    }).encode()
    req = urllib.request.Request(TAVILY_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _parse_cost_musd(text: str):
    """Best-effort: return a cost in USD millions if confidently parsed, else None."""
    m = _COST_RE.search(text or "")
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2).lower()
    return value * 1000.0 if unit in ("billion", "bn") else value


def main() -> int:
    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        print("TAVILY_API_KEY not set -- skipping news refresh (no-op).")
        return 0

    now = datetime.now(timezone.utc).date().isoformat()
    out_systems = []
    for sys_ in seed_systems():  # raw curated seed -> never re-propagate prior news URLs
        if not sys_.news_query:
            continue
        # Keep the curated seed sources by default. Only replace `sources` with news URLs
        # when those URLs actually yielded a usable cost figure -- otherwise the URLs are
        # merely "related news" and must NOT masquerade as citations for the figure. We
        # always expose what we found under `related_news` for transparency.
        entry = {"key": sys_.key, "last_updated": now, "sources": list(sys_.sources)}
        try:
            res = _tavily_search(sys_.news_query, api_key)
            results = res.get("results", [])
            urls = [r.get("url", "") for r in results if r.get("url")][:4]
            if urls:
                entry["related_news"] = urls
            blob = " ".join((r.get("content") or "") for r in results)
            cost = _parse_cost_musd(blob)
            if cost and 0.5 <= cost <= 100_000:  # sanity bound (0.5M .. 100B)
                entry["unit_cost_musd"] = round(cost, 1)
                if urls:
                    entry["sources"] = urls  # these URLs substantiate the parsed figure
                print(f"  {sys_.key}: parsed unit cost ~${cost/1000:.2f}B from news")
            else:
                print(f"  {sys_.key}: no confident cost parsed (kept curated sources)")
        except (urllib.error.URLError, ValueError, KeyError) as exc:
            print(f"  {sys_.key}: news lookup failed ({exc}); kept curated sources")
        out_systems.append(entry)

    os.makedirs(os.path.dirname(os.path.normpath(OUT_PATH)), exist_ok=True)
    with open(os.path.normpath(OUT_PATH), "w") as fh:
        json.dump({"generated": now, "systems": out_systems}, fh, indent=2)
    print(f"Wrote {os.path.normpath(OUT_PATH)} ({len(out_systems)} systems).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
