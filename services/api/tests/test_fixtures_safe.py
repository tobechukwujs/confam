"""Links must never be invented. Fixtures use only reserved domains (*.example), and no
fictional government address (.gov.ng or .gov) appears anywhere in the repo (rules 9 and 10)."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
SKIP_DIRS = {"node_modules", ".venv", ".next", ".git", "test-results", "playwright-report", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".json", ".md", ".py", ".ts", ".tsx", ".css", ".mjs", ".toml", ".yaml", ".yml", ".txt", ".example"}
SKIP_FILES = {"pnpm-lock.yaml", "uv.lock", "test_fixtures_safe.py"}  # this file names the patterns

GOV = re.compile(r"\.gov(\.ng)?\b", re.IGNORECASE)
URL = re.compile(r"https?://[^\s\"'<>)\]]+")


def repo_text_files():
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = Path(folder) / name
            if name in SKIP_FILES or (path.suffix not in TEXT_SUFFIXES and name != ".env.example"):
                continue
            yield path


def test_no_gov_address_anywhere_in_the_repo():
    offenders = []
    for path in repo_text_files():
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if GOV.search(line):
                offenders.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()[:100]}")
    assert offenders == [], "fictional .gov / .gov.ng addresses found:\n" + "\n".join(offenders)


def test_every_url_in_fixtures_is_on_a_reserved_example_domain():
    offenders = []
    for path in (ROOT / "fixtures").rglob("*.json"):
        for url in URL.findall(path.read_text(encoding="utf-8")):
            url = url.rstrip(".,;:")  # a full stop after a link is sentence punctuation
            host = urlparse(url).hostname or ""
            if not (host == "example" or host.endswith(".example")):
                offenders.append(f"{path.relative_to(ROOT)}: {url}")
    assert offenders == [], "fixture URLs must end in .example:\n" + "\n".join(offenders)


def test_the_scan_actually_sees_fixture_urls():
    found = [u for p in (ROOT / "fixtures").rglob("*.json") for u in URL.findall(p.read_text(encoding="utf-8"))]
    assert any("sec.example" in u for u in found)


def test_the_gov_pattern_catches_what_it_should():
    assert GOV.search("https://elections.gov.ng/notice")
    assert GOV.search("https://portal.gov/x")
    assert not GOV.search("https://sec.example/notice")
    assert not GOV.search("the government announced")
