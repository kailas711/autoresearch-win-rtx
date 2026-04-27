"""
Fetch full Genesis (50 chapters) in Hebrew (OSHB via Sefaria API) and English
(Berean Standard Bible via bereanbible.com plain-text download).

Writes:
  data/fixtures/genesis_full_hebrew.json
  data/fixtures/genesis_full_berean.json

Both files are dicts keyed by canonical Gen.<chapter>.<verse> refs.

Usage:
    uv run python scripts/fetch_genesis_full.py
"""

import html
import json
import re
import sys
import time
from pathlib import Path

import requests

OUT_DIR = Path("data/fixtures")
SEFARIA_URL = "https://www.sefaria.org/api/texts/Genesis.{chapter}?context=0"
BSB_URL = "https://bereanbible.com/bsb.txt"


def fetch_hebrew_chapter(chapter: int, retries: int = 3) -> list[str]:
    """Return list of Hebrew verses for the given Genesis chapter."""
    url = SEFARIA_URL.format(chapter=chapter)
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            verses = data.get("he", [])
            return [v if isinstance(v, str) else "" for v in verses]
        except Exception as exc:
            print(f"  retry {attempt + 1}: {exc}", file=sys.stderr)
            time.sleep(1 + attempt)
    raise RuntimeError(f"failed to fetch Genesis {chapter} from Sefaria")


def strip_hebrew_html(text: str) -> str:
    """Clean Sefaria Hebrew verses to bare consonantal/vocalized text.

    Sefaria delivers Hebrew with HTML tags, HTML entities (&nbsp;), bracketed
    editorial annotations ({...}, [...], (...)), variant-reading asterisks,
    and stray combining grapheme joiners (U+034F). Strip all of them so the
    BPE tokenizer sees only Hebrew + standard space.
    """
    # 1. Strip HTML tags: <sup>1</sup>, <i>...</i>, etc.
    text = re.sub(r"<[^>]+>", "", text)
    # 2. Decode HTML entities: &nbsp; -> NBSP (then collapsed below), &amp; -> &
    text = html.unescape(text)
    # 3. Strip Sefaria's bracketed editorial annotations
    text = re.sub(r"\{[^}]*\}", "", text)  # {qere/ketiv}
    text = re.sub(r"\[[^\]]*\]", "", text)  # [variant]
    text = re.sub(r"\([^)]*\)", "", text)  # (note)
    # 4. Strip variant-reading asterisks
    text = text.replace("*", "")
    # 5. Strip combining grapheme joiner (U+034F) — Sefaria sometimes inserts these
    text = text.replace("͏", "")
    # 6. Normalize all whitespace (incl. NBSP from step 2) to single ASCII space, trim
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_hebrew_genesis() -> dict[str, str]:
    out: dict[str, str] = {}
    for chapter in range(1, 51):
        print(f"Hebrew Genesis {chapter}...")
        verses = fetch_hebrew_chapter(chapter)
        for v_idx, verse_text in enumerate(verses, start=1):
            ref = f"Gen.{chapter}.{v_idx}"
            out[ref] = strip_hebrew_html(verse_text)
        time.sleep(0.3)
    return out


def fetch_berean_genesis() -> dict[str, str]:
    print("Fetching full BSB plain-text...")
    r = requests.get(BSB_URL, timeout=30)
    r.raise_for_status()
    out: dict[str, str] = {}
    for line in r.text.splitlines():
        line = line.strip()
        if not line or line.startswith("Verse") or line.startswith("The Holy"):
            continue
        if "\t" not in line:
            continue
        ref_str, text = line.split("\t", 1)
        m = re.match(r"^Genesis\s+(\d+):(\d+)\s*$", ref_str.strip())
        if not m:
            continue
        chapter = int(m.group(1))
        verse = int(m.group(2))
        if chapter > 50:
            continue
        out[f"Gen.{chapter}.{verse}"] = text.strip()
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    hebrew = fetch_hebrew_genesis()
    print(f"Hebrew verses: {len(hebrew)}")

    berean = fetch_berean_genesis()
    print(f"Berean verses: {len(berean)}")

    common = sorted(set(hebrew.keys()) & set(berean.keys()))
    print(f"Common verses (both sides have text): {len(common)}")

    if not common:
        raise RuntimeError("No overlap between Hebrew and Berean — alignment failed")

    hebrew_aligned = {ref: hebrew[ref] for ref in common}
    berean_aligned = {ref: berean[ref] for ref in common}

    he_path = OUT_DIR / "genesis_full_hebrew.json"
    en_path = OUT_DIR / "genesis_full_berean.json"
    he_path.write_text(json.dumps(hebrew_aligned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    en_path.write_text(json.dumps(berean_aligned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {he_path}")
    print(f"Wrote {en_path}")


if __name__ == "__main__":
    main()
