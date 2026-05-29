#!/usr/bin/env python3
"""
Corroborate the registry of hard OSINT facts against current open sources via Tavily.

Writes data/fact_checks.json with, per fact: the value we use, fresh corroborating source
URLs, the date checked, and -- only when a clearly different number is parsed from the news --
a POSSIBLE-discrepancy flag with the parsed value. It never overwrites a value automatically;
a human reviews flagged facts. Graceful no-op (exit 0) when TAVILY_API_KEY is absent.

Usage:  TAVILY_API_KEY=... python scripts/verify_facts.py
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

from osint_cad.doctrine.hard_facts import list_facts

TAVILY_URL = "https://api.tavily.com/search"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fact_checks.json")

_NUM_RE = re.compile(r"\$?\s*(\d+(?:\.\d+)?)\s*(billion|bn|million|m|km|mach|ghz|tonnes|tons)?",
                     re.IGNORECASE)


def _tavily(query: str, api_key: str, max_results: int = 5) -> dict:
    payload = json.dumps({"api_key": api_key, "query": query, "search_depth": "basic",
                          "max_results": max_results, "topic": "news"}).encode()
    req = urllib.request.Request(TAVILY_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _to_unit(value: float, token: str, unit: str) -> float:
    """Normalize a parsed (value, token) into the fact's unit where possible."""
    token = (token or "").lower()
    if unit == "USD_million":
        if token in ("billion", "bn"):
            return value * 1000.0
        if token in ("million", "m"):
            return value
    if unit == "km" and token == "km":
        return value
    if unit == "mach" and token == "mach":
        return value
    if unit == "GHz" and token == "ghz":
        return value
    if unit == "tonnes" and token in ("tonnes", "tons"):
        return value
    return float("nan")


def main() -> int:
    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        print("TAVILY_API_KEY not set -- skipping fact verification (no-op).")
        return 0

    now = datetime.now(timezone.utc).date().isoformat()
    checks = []
    for f in list_facts():
        rec = {"key": f.key, "claim": f.claim, "value_used": f.value, "unit": f.unit,
               "checked": now, "sources": list(f.sources), "status": "unverified"}
        try:
            res = _tavily(f.query, api_key)
            results = res.get("results", [])
            urls = [r.get("url", "") for r in results if r.get("url")]
            if urls:
                rec["sources"] = urls[:4]
            blob = " ".join((r.get("content") or "") for r in results)
            parsed = None
            for m in _NUM_RE.finditer(blob):
                v = _to_unit(float(m.group(1)), m.group(2), f.unit)
                if v == v:  # not NaN
                    parsed = v
                    break
            # Only treat a parsed number as comparable if it is within an order of magnitude
            # of the value we use; otherwise it is almost certainly a different figure in the
            # text (program total, unrelated stat) and we just refresh the sources.
            comparable = parsed is not None and 0.1 <= (parsed / f.value if f.value else 0) <= 10
            if not comparable:
                rec["status"] = "sources_refreshed"  # sources updated; no comparable figure parsed
            else:
                rec["parsed_value"] = round(parsed, 4)
                rel = abs(parsed - f.value) / max(abs(f.value), 1e-9)
                rec["status"] = "possible_discrepancy" if rel > 0.25 else "corroborated"
                rec["relative_delta"] = round(rel, 3)
            print(f"  {f.key}: {rec['status']}" +
                  (f" (news ~{rec.get('parsed_value')})" if 'parsed_value' in rec else ""))
        except (urllib.error.URLError, ValueError, KeyError) as exc:
            rec["status"] = "lookup_failed"
            print(f"  {f.key}: lookup failed ({exc})")
        checks.append(rec)

    os.makedirs(os.path.dirname(os.path.normpath(OUT_PATH)), exist_ok=True)
    with open(os.path.normpath(OUT_PATH), "w") as fh:
        json.dump({"generated": now, "facts": checks}, fh, indent=2)
    print(f"Wrote {os.path.normpath(OUT_PATH)} ({len(checks)} facts).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
