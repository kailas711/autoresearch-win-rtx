# BDB Binyan Investigation — Root Cause Analysis

**Date:** 2026-04-27  
**Branch:** `fix/bdb-binyan-residuals`  
**Input:** `data/fixtures/lex_bdb.json`, `BDB Complete.atool`, `lex_bdb-binyan-audit.md` (Verifier-1), Director r2 brief  
**Status:** Investigation complete — all three sub-defects traced to Tier 1 mechanical extractor bugs

---

## Pre-investigation fixture measurements

Before any fix code:

| Metric | Value |
|---|---|
| Total entries | 8,846 |
| Verb entries (`grammar_normalized='verb'`) | 1,641 |
| Verbs with `binyanim` populated | 1,414 |
| Verbs with `binyanim=None` | **227** |
| Non-verbs with `binyanim` | **0** (clean) |
| `קרא` verb entries with `binyanim` | 0 |
| `הלך` entries | 2 (both noun) |
| `עשה` entries | 0 |

---

## Sub-defect 1: 227 verbs with `binyanim=None`

### Control group (5 verbs with binyanim populated)

| headword_consonantal | headword_raw | grammar | parse_method | binyanim stems |
|---|---|---|---|---|
| אבד | `aDbAd` | `vb.` | `binyan` | qal, piel, hiphil |
| אבך | `aDbAKJ]` | `vb.` | `binyan` | hithpael |
| אבס | `aDbAs]` | `vb.` | `binyan` | qal |
| אבל | `I.` | `vb.` | `binyan` | qal, hiphil |
| None | `I.` | `vb.` | `binyan` | qal |

All working entries have `parse_method='binyan'`.

### Failing group (5 verbs with `binyanim=None`, including קרא)

| headword_consonantal | headword_raw | grammar | parse_method | sense body snippet |
|---|---|---|---|---|
| קרא | `qVr¶a]` | `vb.` | `single` | `vb. call, read out, aloud (v. BH I. qra);ÑPe. Impf. 3 ms.` |
| אחד | `aDjAd]` | `vb.` | `single` | `vb. v. yjd or jdd (Co Ez 21:21). [Addendum]` |
| אמל | `aDmAl]` | `vb.` | `single` | `vb. be weak...Qal. Pt. pass. f.` |
| ביי | `b;Dy\x81y` | `vb.` | `single` | `vb. entreat...` |
| ברד | `b;Dr\x8cd` | `vb.` | `single` | `vb. denom. hail...` |

All failing entries have `parse_method='single'` (226 of 227) or `'numbered'` (1 of 227).

### Root cause identification

The BDB extractor in `crates/fw-binaries/src/decoder/bdb_hooks.rs::extract_binyanim` searches for the label list `BDB_BINYANIM`:

```rust
const BDB_BINYANIM: &[(&str, &str)] = &[
    ("Qal ", "qal"),
    ("Niph. ", "niphal"),
    ("Pi. ", "piel"),
    ("Pu. ", "pual"),
    ("Hithp. ", "hithpael"),
    ("Hiph. ", "hiphil"),
    ("Hoph. ", "hophal"),
    ("Pilp. ", "pilpel"),
    ("Polal ", "polal"),
    ("Polel ", "polel"),
    ("Hithpo. ", "hithpolel"),
    ("Nithp. ", "nithpael"),
];
```

**Critical finding:** BDB's Aramaic section uses *different stem labels* not present in this list. BDB contains a substantial Aramaic vocabulary section (marked `vb.` not `vb. (Aram.)`) with Peal/Pael/Haphel stems instead of Qal/Piel/Hiphil.

Token frequency scan across all 227 failing verb sense bodies:

| Stem token | Count | Normalized name |
|---|---|---|
| `Pe. ` | 98 | peal |
| `Pa. ` | 22 | pael |
| `Haph. ` | 17 | haphel |
| `Po. ` | 3 | polel (alternate abbreviation) |
| `Ithpa. ` | 2 | ithpaal |
| `Shaph. ` | 2 | shaphel |
| `Aph. ` | 1 | aphel |
| `Ithpe. ` | 1 | ithpeel |
| **total with Aramaic stem** | **141** | — |

Example from קרא (entry_index scanned in binary):
```
vb. call, read out, aloud (v. BH I. qra);
Pe. Impf. 3 ms. yöqVrëh...
```

The `Pe. ` label is NOT in `BDB_BINYANIM`, so `extract_binyanim` returns `None` and the entry falls through to single-sense fallback.

**Remaining ~86 entries** (after adding Aramaic stems) break into:
- **~69 zero-label entries**: legitimate Hebrew verbs with very sparse bodies (hapax legomena, denom. verbs, etc.) that have no explicit stem section. BDB editorial practice: sparse pure-Qal verbs do not always include a `Qal ` section header. These need an *implicit Qal fallback*.
- **~17 entries** that are addendum/cross-ref stubs or have non-zero but still-unmatched labels (3× `Qal.` with period, 1× `Ni. ` without trailing `ph.`, etc.). These are legitimate source-sparsity cases.

Expected post-fix count: **~22** (141 Aramaic fixed + 64 implicit Qal + remaining stubs ≈ 22 remaining ≤ 30 target).

**BDB binary confirmation:** The binary at `C:\ProgramData\Accordance\Modules\Tools\BDB Complete.atool\BDB Complete` (30.33 MB) confirms that קרא's body text contains `Pe. Impf.` in the Aramaic section immediately after the entry header. This is NOT a HALOT `\n\t\t{stem}:` pattern — BDB uses spaced capital form `Pe. ` with period and space.

`root_cause: BDB_BINYANIM list missing Aramaic stem labels (Pe., Pa., Haph., Ithpa., Shaph., Aph., Ithpe., Po.) and no implicit Qal fallback for pure-Qal verbs`  
`fix_approach: Add 8 Aramaic stem labels to BDB_BINYANIM in bdb_hooks.rs; add implicit Qal fallback when no stem labels found in Verbal entry body`  
`tier: 1 mechanical`

---

## Sub-defect 2: `הלך` misclassified as noun

### Fixture entries for `headword_consonantal=הלך`

| entry_index | headword_raw | grammar | grammar_normalized | sense definition |
|---|---|---|---|---|
| 1982 | `hQElRKJ` | `n. m.` | `noun` | `n. m. traveller (properly a going, journey...)` |
| 1983 | `hSlDKJ` | `n.` | `noun` | `n. [m.] toll; Ezr 4:13...` |

**These two noun entries are source-truth.** BDB genuinely files `הֵלֶךְ` (n.m. traveller) and `הֲלָךְ` (n. toll) as distinct nominal derivatives of the root הלך. The `grammar_normalized='noun'` is correct.

### The missing entry: verbal `הָלַךְ`

The **verbal** form of הלך IS present in the source binary. Binary inspection at offset `0x9d5ec0`:

```
1980, 3212\thDlAKJ 1545 vb. go, come, walk (MI waDhlK, lK; SI wylkw;...)
```

The entry uses a **compound Strong's key** `1980, 3212` separated by comma+space. The `strongs_tab` entry parser (`entry_parser.rs::find_strongs_tab_entries`) uses the pattern `\r\r{digits}\t` — it parses leading digits and stops when it encounters a non-digit. For `1980, 3212\t`, the parser parses `1980`, then encounters `,` (not TAB), and the pattern does NOT match. This entry is therefore never extracted as its own `RawEntry`.

**Downstream consequence:** The compound-strongs entry body is absorbed into the previous strongs_tab entry (3872, headword `hljwt`). As evidence: fixture entry_index=3872 has an anomalous 15 binyanim (the entire הָלַךְ verb body plus its own).

The acceptance script checks `grammar_normalized='verb'` for `headword_consonantal='הלך'`. The two existing noun entries are correct source-truth. No verb entry exists in the fixture because the verbal root was never extracted.

**Binary hex evidence (offset 0x9d5ec0):**
```
\r\r1980, 3212\thDlAKJ 1545 vb. go, come, walk ...
```
Bytes (first 30): `0d 0d 31 39 38 30 2c 20 33 32 31 32 09 68 44 6c 41 4b 4a 20 31 35 34 35 20 76 62 2e 20 67`

The comma at byte offset +4 (`0x2c`) prevents strongs_tab from matching.

Additionally: there are **810 compound-strongs entries** in BDB with `N, M\t` format (discovered by regex scan). These are all dropped by the current parser.

`root_cause: entry_parser.rs strongs_tab strategy only handles single-integer Strong's; BDB compound strongs "N, M\t" entries are silently dropped and their bodies absorbed into adjacent entries`  
`fix_approach: Extend strongs_tab in entry_parser.rs to handle "N, M\t" pattern; use primary strongs (N) as entry ID; re-run extraction`  
`tier: 1 mechanical`

---

## Sub-defect 3: `עשה` absent from fixture

### Search results

`headword_consonantal='עשה'` yields **0 entries** in the fixture (confirmed: ayin U+05E2 + shin U+05E9 + heh U+05D4).

### Binary inspection

The source binary at offset `0xc8f719`:
```
6213\tI. oDcDh 2622 vb. do, make (NH = BH; MI:23, :26 oCty...
```

**עשה IS present in the source binary** with Strong's 6213. The entry uses the pattern `I. oDcDh` — `I.` is a Roman numeral homograph prefix (BDB editorial practice: multiple homographs of the same root are labelled `I.`, `II.`, etc.).

### Extraction failure trace

The `strongs_tab` strategy correctly matches `6213\t` (single integer → TAB). The `decoded_text` for this entry is `I. oDcDh 2622 vb. do, make...`.

The BDB spec uses `halot_line` field split strategy: first whitespace-separated token = `headword_field`, remainder = body. For `I. oDcDh 2622 vb...`:
- First whitespace at index 2 (after `I.`)
- `headword_field = "I."`
- `body = "oDcDh 2622 vb. do, make..."`

In `extract_headword` with `beta_code_token` extraction and `strip_roman_numerals = true`:
- `raw_field = "I."`
- `strip_roman_numeral_prefix("I.") → ""` (strips the `I ` prefix... but `"I."` without a space after the period doesn't match the pattern `"I "`)

Wait — checking the code: `strip_roman_numeral_prefix` strips `"I "` (with space), but `headword_field = "I."` (period, no space). The beta_code_token path calls `strip_roman_numeral_prefix(s, &mut None)` on `"I."`:
- Pattern `"I "` is not a prefix of `"I."` → not stripped
- Result: `"I."` → split on whitespace/comma → first token `"I."`
- `BetaCodeTable::decode_hebrew("I.")` → consonantal skeleton is empty (no Hebrew beta-code consonants)
- `headword_consonantal = ""` → filtered to `None`

The `assemble_entry` function does NOT skip entries with empty headword_consonantal — it uses `headword` (vocalized form) for the empty check. The vocalized decode of `"I."` returns a dotted-I character, so the entry is NOT dropped. Instead it appears in the fixture as entry_index=6213 with `hw_raw='I.'` and `headword_consonantal=None`.

**Confirmed:** `עשה` exists in the fixture at entry_index=6213 with `grammar_normalized='verb'` and `headword_consonantal=None` — invisible to the acceptance script which queries by `headword_consonantal`.

**Binary hex evidence for עשה in source (offset 0xc8f719, first 30 bytes):**
```
36 32 31 33 09 49 2e 20 6f 44 63 44 68 20 32 36 32 32 20 76 62 2e 20 64 6f 2c 20 6d 61 6b
= "6213\tI. oDcDh 2622 vb. do, mak"
```

`root_cause: halot_line field split extracts only "I." as headword_field; beta_code_token extraction decodes to empty consonantal; entry appears in fixture with hw_cons=None`  
`fix_approach: In bdb_hooks.rs, override headword extraction to detect "I./II./III./IV. {headword}" pattern and extract the SECOND token when first token is a Roman numeral stub; OR modify halot_line split to handle Roman numeral prefix in the headword field`  
`tier: 1 mechanical`

---

## Secondary finding: 810 compound-strongs entries silently dropped

The BDB binary contains **810 entries** with compound Strong's format `N, M\t` (e.g. `1980, 3212\t` for הָלַךְ). All 810 are silently consumed by adjacent entries due to `strongs_tab` parser limitation. This affects both the verb count (sub-defect 1) and named verbs (sub-defect 2). The correct fix is in `entry_parser.rs::find_strongs_tab_entries`.

---

## Relationship between sub-defects

| Sub-defect | Code location | Fix type |
|---|---|---|
| 1 (227 verbs, Aramaic) | `bdb_hooks.rs::BDB_BINYANIM` | Add 8 Aramaic stems |
| 1 (227 verbs, Qal fallback) | `bdb_hooks.rs::extract_binyanim` | Add implicit Qal for no-label verbs |
| 2 (הלך verb missing) | `entry_parser.rs::find_strongs_tab_entries` | Handle `N, M\t` compound strongs |
| 3 (עשה hw_cons=None) | `pipeline.rs::extract_headword` or `bdb_hooks.rs` | Extract second token when first is Roman numeral |

Sub-defects 2 and 3 share a theme (Roman numeral headword issue) but have different root causes. Sub-defect 2 is in the entry parser; sub-defect 3 is in headword extraction.

---

## Domain-knowledge-cache additions

New BDB encoding patterns discovered (to be appended to `docs/domain-knowledge-cache.md`):

1. **Aramaic stem labels:** BDB uses `Pe. `, `Pa. `, `Haph. `, `Ithpa. `, `Shaph. `, `Aph. `, `Ithpe. `, `Po. ` for its Aramaic vocabulary section (entries filed as `vb.` not `vb. (Aram.)`). These are NOT the same as HALOT's lowercase `\n\t\t{stem}:` pattern.

2. **Compound Strong's entries:** 810 BDB entries use `N, M\t` format (primary + secondary Strong's). The entry parser's `strongs_tab` strategy requires plain `N\t` and silently drops these. Primary Strong's (N) should be used as the entry ID.

3. **Implicit Qal verbs:** BDB editorial practice allows verb entries with no explicit stem section header — the entry body gives only forms and definitions without a `Qal ` label. These are pure-Qal verbs. Approximately 64 such entries exist in the corpus.

4. **Roman numeral headword prefix:** BDB files homographs as `I. {headword}`, `II. {headword}` in the entry body. When `halot_line` field split extracts only `I.` as the headword token, headword_consonantal decodes to empty. The actual headword is the SECOND whitespace-delimited token.

---

## Investigation conclusions

```
Sub-defect 1:
  root_cause: BDB_BINYANIM missing Aramaic stems (Pe., Pa., Haph., +5 more); 
              no implicit Qal fallback for sparse pure-Qal verbs
  fix_approach: Add 8 Aramaic stem labels to BDB_BINYANIM in bdb_hooks.rs;
                add Qal fallback returning Some([qal section]) when no stems found in verbal body
  tier: 1 mechanical

Sub-defect 2:
  root_cause: entry_parser strongs_tab skips "N, M\t" compound-strongs entries;
              הלך verb body absorbed into entry 3872 (hljwt)
  fix_approach: Extend strongs_tab in entry_parser.rs to match "N, M\t" pattern;
                use primary (N) as entry ID
  tier: 1 mechanical

Sub-defect 3:
  root_cause: halot_line split extracts only "I." as headword when BDB uses "I. {hw}" format;
              beta_code_token decodes to empty consonantal; entry present but headword_consonantal=None
  fix_approach: Override bdb_hooks headword extraction to use second token when first is Roman numeral;
                OR modify split to include remainder
  tier: 1 mechanical
```

All three sub-defects are Tier 1 mechanical. Surface trigger: NOT required. Proceed to Phase 2.

---

## Evidence artifacts

- Binary offset for קרא body with `Pe.`: raw inspection confirmed in session
- Binary offset 0x9d5ec0: `1980, 3212\thDlAKJ` (compound strongs for הָלַךְ)
- Binary offset 0xc8f719: `6213\tI. oDcDh` (עשה with Roman numeral prefix)
- 810 compound-strongs entries confirmed via regex scan of binary
- Fixture entry_index=6213: `hw_raw='I.'`, `hw_cons=None`, `grammar_normalized='verb'` (עשה IS in fixture, just invisible)
- Fixture entry_index=3872 (`hljwt`): anomalous 15 binyanim from absorbed הָלַךְ body
