# Domain Knowledge Cache

**Purpose:** capture domain-specific knowledge supplied by the user (or discovered through investigation) so future agent dispatches reference it directly instead of relying on the Team Lead to remember and re-relay each time. Update this file whenever a new domain hint surfaces.

Referenced by `docs/autoresearch-team-orchestration.md` — agent briefs should include a "consult `docs/domain-knowledge-cache.md` for any domain detail you're uncertain about" line, replacing prior ad-hoc relay.

---

## Accordance binary formats

### Beta Code character mappings

The canonical Greek + Hebrew "beta code" mappings live inside Accordance's installed OpenType fonts at:

- `C:\Program Files (x86)\OakTree\Accordance\Resources\Fonts\Helena.otf` — Greek beta-code → Greek Unicode (CMAP table)
- `C:\Program Files (x86)\OakTree\Accordance\Resources\Fonts\Lakhish.otf` — Hebrew beta-code → Hebrew Unicode (CMAP table)
- `Accordance.ttf`, italic/bold variants — additional glyph tables for reference

Hand-rolled Beta Code tables in code (e.g., legacy `halot_sense_extractor::betacode_consonant`) are **reinventions** of these official mappings and diverge in rare-character cases. Build-time CMAP extraction via `ttf-parser` is the canonical approach.

### .atool format (lexicons)

Module structure: `<NAME>.atool/` directory containing:
- Main binary data file (no extension; e.g., `BDAG`, `HALOT`)
- `Biblio Info` — bibliographic metadata (small text)
- `Info.plist` — Apple-style property list with `com.oaktree.module.moduletype` (3 = pre-v4, 4 = v4 newer format), `language`, `humanreadablename`, `tagsarray`
- `Resources/` — typically just cover.png/cover@2x.png

Module type=3: parseable by existing OakTree reader (HALOT, BDAG, BDB Complete).
Module type=4: KM Hebrew Dictionary; required custom parser (committed in PR #6 to fellwork-api). Content starts at ~3.2 MB offset (not standard 2 MB cap); detect via `gk H{n} | s ` fingerprint, walk back to triple-CR boundary.

### .atext format (tagged Bibles)

`HMT-DEMO`, `MT-ETCBC-A`, `GNT28-T`, etc. at `C:\ProgramData\Accordance\Modules\Texts\<NAME>.atext\`.

Per `docs/atext-exploration-report.md` (2026-04-27): all `.atext` files have `moduletype=1`, `hasgrammaticaltags=1`, `usestrongsnumber=0`. **"Tagged" means morphology-tagged, NOT Strong's-tagged.** Strong's identifiers must be sourced from lexicons (HALOT/BDB/BDAG) or STEPBible TSV, not from the tagged Bibles.

OakTree-reader compatibility per file:
- HMT-DEMO + MT-LXX Interlinear: parse cleanly (header compatible)
- GNT28-T: partial (corrupted title_len)
- MT-ETCBC-A + MT-E words: fail sentinel detection; need new parser code
- All require new extractor logic; existing reader does not produce correct entries from any

### .ainter format (interlinear)

`MT-LXX Interlinear.ainter` is a tar archive containing "Revised CATSS Hebrew/Greek Parallel Text". Per-record format inside: `{HEB}\t{GRK}\r` per word-pair with `\r\rGen. 1:1\r` verse headers; 44 LXX books; identity char table works (no Beta Code decoding needed for the alignment column).

Verse-ref table at offset 0x5A400C.

### .agloss format (gloss table)

`MT-E words.agloss` is a 432 KB structured binary:
- Offset table: 9,248 entries at 0x140
- Hebrew lemmas (Westminster Beta Code) at 0x10000
- Bilingual English/German glosses at 0x21760
- No standard sentinel; offsets-driven parser

---

## HALOT-specific patterns

### Binyan markers (Hebrew verb stem labels)

HALOT uses the pattern `\n\t\t<lowercase-stem>:` — note: lowercase, with two tabs and trailing colon. NOT `Qal ` (capitalized + space).

For high-frequency verbs, the marker often expands: `\n\t\tqal (ca. 750 times):` — accept variants with parenthesized occurrence counts.

Stem names (lowercase): `qal`, `niphal`, `piel`, `pual`, `hiphil`, `hophal`, `hithpael`, plus rare/Aramaic stems (`pa`, `pe`, `haphel`, `pilpel`, `hithpolel`).

Implicit-Qal fallback: verbal entries that lack explicit section headers are pure-Qal verbs. The extractor should not require an explicit `qal:` marker for entries that only have one stem.

### Cross-references vs binyan markers

`classify_entry_type()` must check binyan markers BEFORE `→` cross-reference markers. Common verbs (e.g., hayah `→ II hwh; Sil.,...`) have etymology cross-refs that would mis-classify them as CrossRef otherwise. Tighten cross-ref detection to require body < 60 chars AND no newlines.

### Entries that "look missing" but exist

If a verb appears absent from the multi-stem extraction (e.g., natan, shaphat reportedly missing): check if it's classified into a different category (CrossRef, single-stem) rather than truly absent. Source binary almost certainly has these as discrete entries.

### HALOT verb entry format — two classes (discovered 2026-04-27, see docs/audits/halot-grammar-investigation.md)

**Class 1 — Explicit-vb. entries (~298 in current fixture):**
Format: `headword: [DSS|denom.|Ña.] vb. ...`
`vb.` appears within first ~50 chars of body after `split_halot_line`. Grammar extraction succeeds.

**Class 2 — Implicit-verb entries (high-frequency roots, ~1,200+ estimated):**
Format A (homograph): `I headword (N x): etymology; qal:...`
Format B (non-homograph): `headword (N x): etymology; qal:...`
NO `vb.` label anywhere in entry. Verb identity signaled ONLY by stem section headers (`qal:`, `nif.:`, etc.). This is deliberate HALOT editorial practice for roots whose verbal nature is universally known (e.g., אמר entry 469, ידע entry 2353, עשה entry 4977, בוא entry 743). Grammar extraction currently fails for all Class 2 entries.

### Roman numeral prefix format

HALOT uses `"I headword"` (space, NO dot) for homograph disambiguation. Distinct from BDB's `"I. headword"` (dot + space). The `is_roman_numeral_stub` fallback in pipeline.rs only handles BDB style (`"I."` with dot). HALOT's `"I "` format does NOT trigger the fallback → headword_field='I' → decoded as Hebrew hirek mark `ִ` → headword_consonantal=None for 1,294 entries.

### Hebrew verb נתן (to give, ~2,014 OT occurrences)

Has NO standalone Hebrew verb root entry in the HALOT binary. Exists only via derived nouns (entries 4349, 4352-4355) and Aramaic cognate (entry 7297). HALOT editorial omission, not a parsing defect. Validation sample lists for any fix must note this: נתן cannot be validated as a Hebrew verb entry via HALOT.

### Hebrew verb ראה (to see, ~1,311 OT occurrences)

No extractable Hebrew root entry found in binary section. Derived nouns יִרְאָה (entry 2627) and מַרְאָה (entry 3815) are present. Root may exist under unexpected beta-code encoding — requires targeted binary search. Not confirmed as editorial omission.

---

## BDAG-specific patterns

### Headword encoding

BDAG headwords are stored as **Helena.otf font-encoded Latin bytes**, NOT Unicode polytonic Greek. Decoding requires the unified Beta Code table from font CMAP. Example: bytes `[0xC6, 0x41, 0x72, 0x77, 0xC0]` → `Ἀαρών`.

### Sense markers

Primary senses use **circled digits** (① ② ③ ... ⑳) — these are font-encoded too; need decoding via Beta Code table to fire as sense markers.

Sub-senses use lowercase Roman/Latin (`a.`, `b.`, `c.`) and Greek letter sequences (`Ι.`, `ΙΙ.`, `ΙΙΙ.` — the `Ι` here is Greek Iota U+0399, not Latin I).

### Numbered-dot sense detection trap

`split_on_numbered_dot` must require **tab prefix** before the numeral. Otherwise citation references like "Pollux 6, 9." match before real sense numbers `\t1.`, and sequential validation rejects the entire detection.

### Body field split

BDAG uses `bdag_line` strategy (split on first whitespace), NOT `halot_line` (split on first colon). BDAG bodies legitimately contain colons (Bible references like `Mt 5:3`); colon-split corrupts 411+ entries.

### Out-of-scope content

Skip when extracting (no ML signal toward English fluency):
- Classical Greek / Patristic / Septuagint quotations inside BDAG entry bodies
- Bibliography references
- Form-variation tables

---

## KM-specific patterns

### Cross-references and structure

KM uses `gk H{n} | s ` fingerprint pattern as content-start signal. Triple-CR (`\r\r\r`) boundaries between entries.

### KM number ↔ Strong's

Per-entry GK number (`gk_H#####`) is the primary identifier. Strong's Hebrew also present (98.5% coverage). Cross-reference between the two via the lexicon's own table.

### Mounce attribution

Anchor string `"Portions also derived from Mounce's Complete Expository"` appears in KM metadata. Useful as a known landmark for binary-format inspection.

### Bible translations field

This edition's `±` lines contain only column-header abbreviations (`niv | esv | ...`), not per-entry renderings. All 10,173 entries have `bible_translations: null` by design — confirmed via hex inspection. Not a defect.

---

## BDB-specific patterns

### Schema compliance (post-iter-5)

BDB fixtures should match Architect Section D shape:
- `primary_key` (consonantal Hebrew form)
- `senses[]` (recursive nested structure)
- `binyanim[]` (per-stem subtree for verbs)
- All annotated fields have `_source: "mechanical" | "curated"` keys

The early flat-6-fields shape (lemma, gloss, definition, headword_raw, sense_count, grammar) is non-compliant.

### Homograph collapsing

BDB Complete has multiple consonantally-identical entries that should be collapsed under one headword with `homograph_index = 0..N`. ~3,030 entries have `homograph_index` assigned in current state.

### Binyan extraction

Currently 93/8848 entries have binyanim populated — likely incomplete extraction. Filed as Plan #7b for follow-up investigation.

---

## OSHB / public sources

### Hebrew text

Sefaria API at `https://www.sefaria.org/api/texts/Genesis.{chapter}?context=0` returns `he` field with vocalized Hebrew per verse. Cleanup needed:
- HTML tags (`<...>`)
- HTML entities (`&nbsp;` etc. — must use `html.unescape`)
- Sefaria editorial annotations: `{...}`, `[...]`, `(...)`, `*`
- Stray combining grapheme joiners (U+034F)

Reference cleanup function: `scripts/fetch_genesis_full.py::strip_hebrew_html`.

### Hebrew use of maqaf

ASCII hyphen `-` (U+002D) is NOT correct for Hebrew word-joining. Use Hebrew maqaf `־` (U+05BE). Validate Hebrew strings contain only `U+0590-05FF | U+05BE | U+0020`.

### English Bible — Berean Standard Bible (BSB)

Public-domain, downloadable as plain TSV from `https://bereanbible.com/bsb.txt`. Format: `Genesis 1:1\tIn the beginning God created...`.

### Public-domain lexicons

Sources confirmed working:
- BDB: OpenScriptures `BrownDriverBriggs.xml` + `LexicalIndex.xml` from `github.com/openscriptures/HebrewLexicon`
- Thayer (Abbott-Smith): STEPBible TBESG tab-separated file
- LSJ: STEPBible TFLSJ (23 MB; already Greek Unicode, no beta code decoding needed)

### STEPBible Strong's↔GK mapping

Authoritative TSV at `github.com/STEPBible/STEPBible-Data` for Strong's↔GK Hebrew + Strong's↔GK Greek conversions. Vendor as data file, NOT code-generate as a hardcoded `match` table (caused a 600s wrong-direction stall in iter 5b).

---

## Project-specific terminology

| Term | Meaning |
|---|---|
| Binyan | Hebrew verb stem (Qal, Niphal, Piel, Pual, Hiphil, Hophal, Hithpael, plus rare/Aramaic) |
| Wayyiqtol | Hebrew narrative consecutive imperfect (`waw` + verb); preserved as "And ..." in gold rendering |
| Maqaf | Hebrew word-joiner U+05BE (NOT ASCII hyphen) |
| Construct chain | Hebrew genitive construction; rendered as "X of Y" in gold |
| GK number | Goodrick-Kohlenberger numbering (used in NIV apparatus) |
| Mounce numbering | William Mounce's Greek numbering, linked from KM |
| ETCBC | Eep Talstra Centre for Bible and Computer; Hebrew morphology system |
| OSHB | Open Scriptures Hebrew Bible |
| Beta Code | ASCII transliteration for Greek/Hebrew, used in Accordance fonts and some scholarly sources |
| OakTree | Accordance's internal binary format for module data files |

---

## Update protocol

When a new domain hint surfaces (user-supplied or investigation-discovered):
1. Add to the appropriate section above
2. Reference it from the relevant orchestration template if substantive
3. Future briefs say "consult `docs/domain-knowledge-cache.md` for domain detail" instead of inline relay
