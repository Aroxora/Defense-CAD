#!/usr/bin/env python3
"""Tests for the hard-facts registry and the (offline) fact verifier."""

import os
import runpy

from osint_cad.doctrine import hard_facts as hf


def test_hard_facts_registry_well_formed():
    facts = hf.list_facts()
    assert len(facts) >= 6
    for f in facts:
        assert f.claim and f.unit and f.query
        assert f.sources
        assert 0.0 < f.confidence <= 1.0
        assert isinstance(f.value, (int, float)) and f.value > 0
    assert hf.get_fact("madl_band_ghz").unit == "GHz"


def test_verifier_is_graceful_noop_without_key(monkeypatch, capsys):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    # run the script's main() via runpy without a key -> must not raise, must print no-op
    mod = __import__("importlib").import_module("importlib.util")
    spec = mod.spec_from_file_location(
        "verify_facts",
        os.path.join(os.path.dirname(__file__), "..", "scripts", "verify_facts.py"),
    )
    m = mod.module_from_spec(spec)
    spec.loader.exec_module(m)
    rc = m.main()
    assert rc == 0
    assert "no-op" in capsys.readouterr().out.lower()
