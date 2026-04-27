"""
Fetch and parse public-domain Hebrew/Greek lexicons, writing per-lemma JSON fixtures.

Lexicons produced:
  data/fixtures/lex_bdb.json    — BDB (Brown-Driver-Briggs), keyed by H-Strong number
  data/fixtures/lex_thayer.json — Thayer's (via STEPBible TBESG / Abbott-Smith), keyed by G-Strong
  data/fixtures/lex_lsj.json   — LSJ (Liddell-Scott-Jones via STEPBible TFLSJ), keyed by G-Strong

All fixtures share the shape:
  { "<strong_or_lemma_key>": { "lemma": "...", "gloss": "...", "definition": "..." }, ... }

Commercial lexicons (HALOT, Koehler-Muraoka, BDAG) are intentionally omitted.
# TODO commercial: add HALOT / KM / BDAG ingestion once licensing path is established.

Sources (all public-domain / CC-BY):
  BDB XML:      https://github.com/openscriptures/HebrewLexicon (MIT/CC-BY)
  Lexical idx:  same repo, LexicalIndex.xml
  TBESG (Thayer/Abbott-Smith):
                https://github.com/STEPBible/STEPBible-Data (CC-BY)
  TFLSJ (LSJ):  same repo

Usage:
    uv run python scripts/fetch_lexicons.py
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

OUT_DIR = Path("data/fixtures")

BDB_XML_URL = (
    "https://raw.githubusercontent.com/openscriptures/HebrewLexicon/master/"
    "BrownDriverBriggs.xml"
)
LEX_INDEX_URL = (
    "https://raw.githubusercontent.com/openscriptures/HebrewLexicon/master/"
    "LexicalIndex.xml"
)
TBESG_URL = (
    "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Lexicons/"
    "TBESG%20-%20Translators%20Brief%20lexicon%20of%20Extended%20Strongs%20for%20"
    "Greek%20-%20STEPBible.org%20CC%20BY.txt"
)
TFLSJ_URL = (
    "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/Lexicons/"
    "TFLSJ%20%200-5624%20-%20Translators%20Formatted%20full%20LSJ%20Bible%20"
    "lexicon%20-%20STEPBible.org%20CC%20BY.txt"
)

# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "autoresearch-lexicon-ingest/1.0"


def fetch_text(url: str, retries: int = 3, timeout: int = 60) -> str:
    """Download *url* and return the text body, retrying on transient errors."""
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except requests.RequestException as exc:
            print(f"  [warn] attempt {attempt + 1} failed: {exc}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


def fetch_bytes(url: str, retries: int = 3, timeout: int = 120) -> bytes:
    """Download *url* and return raw bytes (for large files)."""
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=timeout, stream=True)
            r.raise_for_status()
            chunks: list[bytes] = []
            for chunk in r.iter_content(chunk_size=1 << 16):
                chunks.append(chunk)
            return b"".join(chunks)
        except requests.RequestException as exc:
            print(f"  [warn] attempt {attempt + 1} failed: {exc}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts")


# ---------------------------------------------------------------------------
# BDB (Brown-Driver-Briggs) — Hebrew
# ---------------------------------------------------------------------------


# OpenScriptures XML namespace
_MORPHHB_NS = "http://openscriptures.github.com/morphhb/namespace"
_NS = f"{{{_MORPHHB_NS}}}"


def _strip_ns_xml(xml_text: str) -> str:
    """Strip BOM, DOCTYPE, and inline namespace declarations so ElementTree parses cleanly."""
    xml_text = xml_text.lstrip("﻿")
    xml_text = re.sub(r"<!DOCTYPE[^>]*>", "", xml_text, count=1)
    return xml_text


def _ns(tag: str) -> str:
    return f"{_NS}{tag}"


def _collect_bdb_defs(entry: ET.Element) -> list[str]:
    """Return all <def> text values from an entry and its immediate <sense> children."""
    defs: list[str] = []
    for d in entry.findall(_ns("def")):
        t = (d.text or "").strip()
        if t:
            defs.append(t)
    for sense in entry.findall(_ns("sense")):
        for d in sense.findall(_ns("def")):
            t = (d.text or "").strip()
            if t:
                defs.append(t)
    return defs


def parse_bdb_xml(xml_text: str) -> dict[str, dict]:
    """
    Parse BrownDriverBriggs.xml (namespace-aware).

    Returns dict keyed by BDB entry id (e.g. "a.ac.aa") with:
      { "lemma": str, "pos": str, "defs": [str], "raw_strongs": int|None }
    """
    xml_text = _strip_ns_xml(xml_text)
    root = ET.fromstring(xml_text)

    entries: dict[str, dict] = {}
    for entry in root.iter(_ns("entry")):
        eid = entry.get("id", "")
        if not eid:
            continue

        w_el = entry.find(_ns("w"))
        lemma = (w_el.text or "").strip() if w_el is not None else ""

        pos_el = entry.find(_ns("pos"))
        pos = (pos_el.text or "").strip() if pos_el is not None else ""

        # Raw Strong's number: appears as text node between </w> and <pos>
        raw_strongs: int | None = None
        if w_el is not None and w_el.tail:
            m = re.search(r"\b(\d{1,5})\b", w_el.tail)
            if m:
                raw_strongs = int(m.group(1))

        defs = _collect_bdb_defs(entry)
        entries[eid] = {
            "lemma": lemma,
            "pos": pos,
            "defs": defs,
            "raw_strongs": raw_strongs,
        }
    return entries


def parse_lex_index(xml_text: str) -> dict[str, dict]:
    """
    Parse LexicalIndex.xml (namespace-aware).

    Returns dict: H<strong> -> { "bdb_id": str, "lemma": str, "gloss": str }
    The LexicalIndex is the authoritative Strong's→BDB bridge and also carries
    its own lemma and def fields, which we use as the primary gloss source.
    """
    xml_text = _strip_ns_xml(xml_text)
    root = ET.fromstring(xml_text)

    result: dict[str, dict] = {}
    for entry in root.iter(_ns("entry")):
        xref = entry.find(_ns("xref"))
        if xref is None:
            continue
        bdb_id = xref.get("bdb", "")
        strong_raw = xref.get("strong", "")
        if not strong_raw:
            continue
        try:
            strong_key = f"H{int(strong_raw)}"
        except ValueError:
            continue

        w_el = entry.find(_ns("w"))
        lemma = (w_el.text or "").strip() if w_el is not None else ""
        def_el = entry.find(_ns("def"))
        gloss = (def_el.text or "").strip() if def_el is not None else ""

        if strong_key not in result:
            result[strong_key] = {"bdb_id": bdb_id, "lemma": lemma, "gloss": gloss}
        else:
            # Accumulate alternate glosses
            existing = result[strong_key]
            if gloss and gloss not in existing["gloss"]:
                existing["gloss"] = (
                    existing["gloss"] + "; " + gloss if existing["gloss"] else gloss
                )
            if not existing["lemma"] and lemma:
                existing["lemma"] = lemma

    return result


def build_bdb_fixture(
    bdb_entries: dict[str, dict], lex_index: dict[str, dict]
) -> dict[str, dict]:
    """
    Merge LexicalIndex Strong's→BDB mapping with detailed BDB XML definitions.

    Priority:
    1. Key and primary gloss come from LexicalIndex (has Strong's, lemma, def).
    2. Richer multi-sense definitions come from BDB XML via bdb_id lookup.
    """
    # Build reverse: bdb_id -> strong key (take the first mapping for duplicates)
    bdb_id_to_key: dict[str, str] = {}
    for strong_key, info in lex_index.items():
        bid = info["bdb_id"]
        if bid and bid not in bdb_id_to_key:
            bdb_id_to_key[bid] = strong_key

    fixture: dict[str, dict] = {}

    # Start from LexicalIndex (has all Strong's numbers)
    for strong_key, info in lex_index.items():
        lemma = info["lemma"]
        gloss = info["gloss"]
        bdb_id = info["bdb_id"]

        # Enrich from BDB XML
        bdb_entry = bdb_entries.get(bdb_id, {})
        bdb_defs = bdb_entry.get("defs", [])
        pos = bdb_entry.get("pos", "")

        # Use BDB lemma if LexIndex has none
        if not lemma:
            lemma = bdb_entry.get("lemma", "")

        # Build definition from BDB defs; fall back to gloss
        if bdb_defs:
            definition = "; ".join(bdb_defs)
        else:
            definition = gloss

        if pos:
            definition = f"[{pos}] {definition}" if definition else f"[{pos}]"

        # Use BDB first def as gloss if LexIndex gloss is missing
        if not gloss and bdb_defs:
            gloss = bdb_defs[0]

        if not lemma and not gloss:
            continue

        if strong_key not in fixture:
            fixture[strong_key] = {
                "lemma": lemma,
                "gloss": gloss,
                "definition": definition,
            }
        else:
            existing = fixture[strong_key]
            if gloss and gloss not in existing["gloss"]:
                existing["gloss"] += "; " + gloss

    # Add any BDB entries that have a raw strongs# but weren't in LexIndex
    for bdb_id, entry in bdb_entries.items():
        rs = entry.get("raw_strongs")
        if not rs:
            continue
        strong_key = f"H{rs}"
        if strong_key in fixture:
            continue
        defs = entry["defs"]
        if not defs and not entry["lemma"]:
            continue
        gloss = defs[0] if defs else ""
        definition = "; ".join(defs) if defs else gloss
        pos = entry["pos"]
        if pos:
            definition = f"[{pos}] {definition}" if definition else f"[{pos}]"
        fixture[strong_key] = {
            "lemma": entry["lemma"],
            "gloss": gloss,
            "definition": definition,
        }

    return fixture


def fetch_bdb() -> dict[str, dict]:
    """Download and parse BDB, return fixture dict."""
    print("Fetching BrownDriverBriggs.xml …")
    xml_text = fetch_text(BDB_XML_URL, timeout=90)
    print(f"  Downloaded {len(xml_text):,} bytes")

    print("Fetching LexicalIndex.xml …")
    idx_text = fetch_text(LEX_INDEX_URL, timeout=60)
    print(f"  Downloaded {len(idx_text):,} bytes")

    print("Parsing BDB XML …")
    bdb_entries = parse_bdb_xml(xml_text)
    print(f"  Parsed {len(bdb_entries):,} raw BDB entries")

    print("Parsing LexicalIndex …")
    lex_index = parse_lex_index(idx_text)
    print(f"  Indexed {len(lex_index):,} Strong's numbers from LexicalIndex")

    fixture = build_bdb_fixture(bdb_entries, lex_index)
    print(f"  Built {len(fixture):,} BDB fixture entries")
    return fixture


# ---------------------------------------------------------------------------
# STEPBible TSV helpers (shared by Thayer/TBESG and LSJ/TFLSJ)
# ---------------------------------------------------------------------------

# Column indices for the STEPBible TBESG / TBESH / TFLSJ tab-separated files:
# eStrong#  dStrong  uStrong  Lemma  Translit  Morph  Gloss  Meaning
_COL_ESTRONG = 0
_COL_LEMMA   = 3
_COL_MORPH   = 5
_COL_GLOSS   = 6
_COL_MEANING = 7


def _is_header_or_comment(line: str) -> bool:
    return (
        not line
        or line.startswith("#")
        or line.startswith("=")
        or line.startswith("TBESH")
        or line.startswith("TBESG")
        or line.startswith("TFLSJ")
        or line.startswith("See also")
        or line.startswith("Extended")
        or line.startswith("Lexicons")
        or line.startswith("The Brief")
        or line.startswith("The Full")
        or line.startswith("FIELD")
        or line.startswith("eStrong")
        or line.startswith("===")
    )


_STRONG_RE = re.compile(r"^([GH]\d+[A-Z]?)")


def parse_stepbible_tsv(
    text: str,
    prefix: str,
    *,
    max_entries: int | None = None,
) -> dict[str, dict]:
    """
    Generic STEPBible tab-separated lexicon parser.

    *prefix* is "G" for Greek files or "H" for Hebrew files.
    Returns fixture dict keyed by Strong's number.
    """
    fixture: dict[str, dict] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if _is_header_or_comment(line):
            continue
        cols = line.split("\t")
        if len(cols) < 7:
            continue

        estrong = cols[_COL_ESTRONG].strip()
        m = _STRONG_RE.match(estrong)
        if not m:
            continue
        key = m.group(1)
        if not key.startswith(prefix):
            continue

        lemma   = cols[_COL_LEMMA].strip()   if len(cols) > _COL_LEMMA   else ""
        morph   = cols[_COL_MORPH].strip()   if len(cols) > _COL_MORPH   else ""
        gloss   = cols[_COL_GLOSS].strip()   if len(cols) > _COL_GLOSS   else ""
        meaning = cols[_COL_MEANING].strip() if len(cols) > _COL_MEANING else ""

        if not lemma and not gloss:
            continue

        definition = meaning if meaning else gloss
        if morph:
            definition = f"[{morph}] {definition}" if definition else f"[{morph}]"

        if key not in fixture:
            fixture[key] = {
                "lemma": lemma,
                "gloss": gloss,
                "definition": definition,
            }
        else:
            # Accumulate alternate glosses for the same strongs number
            existing = fixture[key]
            if gloss and gloss not in existing["gloss"]:
                existing["gloss"] = existing["gloss"] + "; " + gloss if existing["gloss"] else gloss

        if max_entries and len(fixture) >= max_entries:
            break

    return fixture


# ---------------------------------------------------------------------------
# Thayer's Greek Lexicon (via STEPBible TBESG / Abbott-Smith)
# ---------------------------------------------------------------------------

def fetch_thayer() -> dict[str, dict]:
    """
    Download STEPBible TBESG (Translators Brief Extended Strongs Greek).

    The TBESG is based on Abbott-Smith's Manual Greek Lexicon of the NT
    (itself the standard Thayer successor / update), edited by Tyndale scholars.
    It is CC-BY licensed.
    """
    print("Fetching TBESG (Thayer/Abbott-Smith) …")
    text = fetch_text(TBESG_URL, timeout=90)
    print(f"  Downloaded {len(text):,} bytes")
    fixture = parse_stepbible_tsv(text, prefix="G")
    print(f"  Built {len(fixture):,} Thayer fixture entries")
    return fixture


# ---------------------------------------------------------------------------
# LSJ (Liddell-Scott-Jones via STEPBible TFLSJ)
# ---------------------------------------------------------------------------

def fetch_lsj() -> dict[str, dict]:
    """
    Download STEPBible TFLSJ (Translators Formatted full LSJ, entries 0-5624).

    The underlying LSJ (9th edition + supplement) is public domain.
    STEPBible's formatting/expansion layer is CC-BY.
    """
    print("Fetching TFLSJ (LSJ) …")
    raw = fetch_bytes(TFLSJ_URL, timeout=180)
    text = raw.decode("utf-8", errors="replace")
    print(f"  Downloaded {len(raw):,} bytes")

    fixture = parse_stepbible_tsv(text, prefix="G")
    print(f"  Built {len(fixture):,} LSJ fixture entries")
    return fixture


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def write_fixture(path: Path, data: dict[str, dict]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    size_kb = path.stat().st_size // 1024
    print(f"  Wrote {path}  ({len(data):,} entries, {size_kb:,} KB)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- BDB (Hebrew) ----
    print("\n=== BDB (Brown-Driver-Briggs) ===")
    bdb = fetch_bdb()
    write_fixture(OUT_DIR / "lex_bdb.json", bdb)

    # ---- Thayer (Greek) ----
    print("\n=== Thayer / Abbott-Smith (TBESG) ===")
    thayer = fetch_thayer()
    write_fixture(OUT_DIR / "lex_thayer.json", thayer)

    # ---- LSJ (Greek) ----
    print("\n=== LSJ (TFLSJ) ===")
    lsj = fetch_lsj()
    write_fixture(OUT_DIR / "lex_lsj.json", lsj)

    print("\nDone.")

    # TODO commercial: HALOT (Hebrew/Aramaic Lexicon of the OT) — needs license
    # TODO commercial: KM (Koehler-Muraoka Aramaic) — needs license
    # TODO commercial: BDAG (Bauer-Danker-Arndt-Gingrich) — needs license


if __name__ == "__main__":
    main()
