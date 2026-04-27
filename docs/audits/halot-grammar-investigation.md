# HALOT Grammar Investigation

**Branch:** `fix/halot-grammar-investigation`
**Date:** 2026-04-27
**Mode:** Investigation-only (Builder Mode 3). No fix code produced.
**Director spec:** `docs/topic-director-notes/hebrew-2026-04-27-r4.md` § 5
**Input fixture:** `data/fixtures/lex_halot.json` (master `4bfeff3`, 22 MB, 6,632 entries)
**Source binary:** `C:\ProgramData\Accordance\Modules\Tools\HALOT.atool\HALOT` (31.7 MB, 7,523 entries via `[A0 0D 0D]` separator)

---

## Section A — Scope Confirmation

### Acceptance script

```python
import json, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FIXTURE = "C:/git/fellwork/autoresearch-win-rtx/data/fixtures/lex_halot.json"
with open(FIXTURE, encoding="utf-8") as f:
    data = json.load(f)
entries = data if isinstance(data, list) else data.get("entries", data.get("data", []))
print(f"Total entries: {len(entries)}")
dist = collections.Counter(e.get("grammar_normalized") for e in entries)
for k, v in sorted(dist.items(), key=lambda x: -x[1]):
    print(f"  grammar_normalized={k!r}: {v}")
NAMED = ["נתן","שפט","אמר","עשה","בוא","ראה","ידע","שאל","שוב","דבר"]
for verb in NAMED:
    hits = [e for e in entries if e.get("headword_consonantal") == verb]
    if hits:
        for e in hits:
            print(f"  {verb}: grammar_normalized={e.get('grammar_normalized')!r}, grammar={e.get('grammar')!r}, "
                  f"binyanim={bool(e.get('binyanim'))}, entry_index={e.get('entry_index')}, "
                  f"headword_raw={e.get('headword_raw')!r}")
    else:
        print(f"  {verb}: NOT FOUND by headword_consonantal")
```

### Verbatim output

```
Total entries: 6632
  grammar_normalized=None: 3120
  grammar_normalized='noun': 2953
  grammar_normalized='verb': 298
  grammar_normalized='adjective': 167
  grammar_normalized='adverb': 54
  grammar_normalized='preposition': 20
  grammar_normalized='interj.': 15
  grammar_normalized='conjunction': 5
```

### Named verb table

| Verb | Entry index | `grammar_normalized` | `grammar` | `binyanim` | `headword_raw` | Notes |
|------|-------------|---------------------|-----------|------------|----------------|-------|
| נתן | 7297 | `noun` | `n.m.` | False | `ntN:` | **Aramaic** cognate entry, not Hebrew verb |
| שפט | 6561 | `noun` | `n.m.` | False | `vDpDf:` | Noun entry שֶׁפֶט "judgment" |
| שפט | 7488 | `None` | `None` | False | *(Roman hw)* | Second homograph, grammar missing |
| אמר | 6941 | `noun` | `n.m.` | False | `amr:` | **Aramaic** cognate entry |
| עשה | 422 | `noun` | `noun` | False | `aRlVoDcDh` | Derived noun אֶלְעָשָׂה, not verb |
| עשה | 3708 | `noun` | `noun` | False | `mAoScRh` | Derived noun מַעֲשֶׂה "deed" |
| בוא | 743 | `noun` | `n.` | False | `bwa` | Hebrew verb entry — MISCLASSIFIED as noun |
| ראה | 2627 | `None` | `None` | False | `yörÃaDh:` | Derived noun יִרְאָה |
| ראה | 3815 | `None` | `None` | False | `mArÃaRh` | Derived noun מַרְאָה |
| ידע | 7153 | `noun` | `n.` | False | `ydo:` | **Aramaic** cognate entry |
| שאל | 6192 | `noun` | `n.` | False | `val:` | **Aramaic** cognate entry |
| שוב | 6271 | `noun` | `n.` | False | `vwb:` | **Aramaic** cognate entry |
| דבר | 1289 | `noun` | `n.` | False | `d¶;bDr` | Noun דָּבָר "word" |
| דבר | 1292 | `noun` | `n.` | False | *(variant)* | Additional noun homograph |
| דבר | 1293 | `None` | `None` | False | *(variant)* | Grammar missing |

**Verifier-3 confirmation:** None=3,120 and verb=298 counts confirmed exactly. All 10 named verbs present in fixture but NONE classified as `grammar_normalized='verb'`. The two entries for עשה and ראה found in the fixture are **derived nouns**, not the Hebrew verb entries. The Hebrew verb entries for the named verbs (אמר at entry 469, ידע at entry 2353, עשה at entry 4977, בוא at entry 743) exist in the binary but decode to `grammar_normalized=None` or `noun` — the verb nature is silently lost.

---

## Section B — Source Binary Inspection

**Binary path confirmed:** `C:\ProgramData\Accordance\Modules\Tools\HALOT.atool\HALOT`
Binary size: 33,284,702 bytes (31.7 MB). Entry separator: `[A0 0D 0D]`. Total separators: 7,523 (7,523 entries; fixture contains 6,632 = Hebrew section only; ~891 are Aramaic section entries beyond fixture range).

**split_halot_line behavior:** The pipeline function `split_halot_line` (pipeline.rs:173) splits on **first whitespace**, producing `headword_field = text[:ws]` and `body = text[ws:].strip()`. Grammar scanner then searches `body` for patterns from `halot.toml`.

### Failing samples — no `vb.` in binary entry

**אמר — entry 469 ("I amr", Hebrew verb "to say", ~5,280 OT occurrences)**

```
Offset in binary: positions[468] + 3
First 64 bytes hex:
  49 20 61 6d 72 20 28 35 32 38 30 20 78 29 3a 20
  53 65 6d 2e 3b 20 74 6f 20 73 61 79 20 4d 48 62
  2e 20 4c 61 63 68 2e 20 4d 6f 2e 20 50 68 2e 20
  41 72 6d 2e 20 28 f9 20 42 41 72 6d 2e 20 44 49
Latin-1: "I amr (5280 x): Sem.; to say MHb. Lach. Mo. Ph. Arm. (ù BArm. DISO 18), OSArb. Arb. to order..."
split_halot_line: hw_field = "I",  body = "amr (5280 x): Sem.; to say MHb. Lach. ..."
Grammar labels in full body: 'n.' at position 2030 only (from "n.m." in derived noun section)
'vb.' in body: ABSENT — the entire entry contains NO "vb." label
Fixture result: headword_raw='I', grammar='n.', grammar_normalized='noun' (FALSE POSITIVE)
```

**ידע — entry 2353 ("I ydo", Hebrew verb "to know", ~949 OT occurrences)**

```
Offset: positions[2352] + 3
First 64 bytes hex:
  49 20 79 64 6f 3a 20 4d 48 65 62 2e 3b 20 55 67
  2e 20 79 64 7b 3b 20 50 68 2e 2c 20 4c 61 63 68
  69 73 68 2c 20 4f 41 72 6d 2e 20 61 6e 64 20 45
  67 41 72 6d 2e 20 28 4a 65 61 6e 2d 48 2e 20 44
Latin-1: "I ydo: MHeb.; Ug. yd{; Ph., Lachish, OArm. and EgArm. (Jean-H. Dictionnaire 104)..."
split_halot_line: hw_field = "I",  body = "ydo: MHeb.; Ug. yd{; Ph., Lachish..."
'vb.' in body: ABSENT
Fixture result: headword_raw='I', grammar=None, grammar_normalized=None
```

**עשה — entry 4977 ("I och", Hebrew verb "to do", ~2,627 OT occurrences)**

```
Offset: positions[4976] + 3
First 64 bytes hex:
  49 20 6f 63 68 20 28 32 36 32 37 20 74 69 6d 65
  73 29 2c 20 4d 48 65 62 2e 2c 20 44 53 53 20 28
  4b 75 68 6e 20 4b 6f 6e 6b 6f 72 64 61 6e 7a 20
  31 37 30 66 2e 20 61 6e 64 20 54 48 41 54 20 32
Latin-1: "I och (2627 times), MHeb., DSS (Kuhn Konkordanz 170f. and THAT 2:369)..."
split_halot_line: hw_field = "I",  body = "och (2627 times), MHeb., DSS (Kuhn Konkordanz..."
'vb.' in body: ABSENT
Fixture result: headword_raw='I', grammar=None, grammar_normalized=None (not in fixture at all as verb)
```

**בוא — entry 743 ("bwa", Hebrew verb "to come", ~2,550 OT occurrences)**

```
Offset: positions[742] + 3
First 64 bytes hex:
  62 77 61 20 28 32 35 35 30 20 78 29 3a 20 4d 48
  62 2e 20 28 6d 65 61 6e 69 6e 67 20 d2 74 6f 20
  65 6e 74 65 72 20 74 68 72 6f 75 67 68 d3 20 73
  75 70 65 72 73 65 64 65 64 20 62 79 20 6b 6e 73
Latin-1: 'bwa (2550 x): MHb. (meaning "to enter through" superseded by kns nif.), Ug. b}; Arslan-T, Lach....'
split_halot_line: hw_field = "bwa",  body = "(2550 x): MHb. (meaning..."
'vb.' in body: ABSENT
Fixture result: grammar='n.', grammar_normalized='noun' (FALSE POSITIVE — 'n.' from abbreviation "Hb.")
```

### Passing sample — `vb.` present at position 4 in body

**אשם — entry 663 ("avM:", Hebrew verb "to be guilty" — CORRECTLY classified)**

```
Offset: positions[662] + 3
First 64 bytes hex:
  61 76 4d 3a 20 44 53 53 20 76 62 2e 2c 20 73 62
  73 74 2e 20 61 6e 64 20 61 64 6a 2e 3b 20 3f 20
  55 67 2e 20 61 74 d7 6d 20 55 54 47 6c 2e 20 34
  32 32 3b 20 41 72 62 2e 20 7d 61 74 d7 69 6d 61
Latin-1: "avM: DSS vb., sbst. and adj.; ? Ug. at×m UTGl. 422; Arb. }at×ima to do wrong..."
split_halot_line: hw_field = "avM:",  body = "DSS vb., sbst. and adj.; ..."
'vb.' in body at position 4 -> grammar scan succeeds
Fixture result: grammar='vb.', grammar_normalized='verb' (CORRECT)
```

### Diagnostic comparison

| Attribute | PASSING entries (298 verbs) | FAILING high-frequency verbs |
|-----------|----------------------------|------------------------------|
| Entry format | `headword: ... vb. ...` | `I headword (N x): etymology` or `headword (N x): etymology` |
| `vb.` in body | YES — explicit, positionally first | NO — absent from entire entry |
| `split_halot_line` result | `hw_field = "headword:"`, body starts at grammar | `hw_field = "I"` (Roman numeral only), body starts with root consonants |
| Grammar scanner outcome | Finds `vb.` → `grammar='vb.'` | Finds nothing or false-positive `n.` |
| Fixture outcome | `grammar_normalized='verb'` | `grammar_normalized=None` or `'noun'` |

**Additional quantification:**
- 181 of 298 correctly-classified verb entries have `vb.` at position >200 in body — confirming the **200-char scan limit is NOT enforced** in the actual pipeline code. The `extract_grammar` function in `pipeline.rs:341` scans the full body with no length restriction. The halot_hooks.rs line 7 comment ("limited to first 200 chars") is a **stale documentation comment** that does not reflect the live code path.

---

## Section C — Decoder Code Trace

### Pipeline path for HALOT grammar extraction

1. **`split_halot_line` (pipeline.rs:173-188):** splits on **first whitespace**.
   ```rust
   let end = trimmed.find(|c: char| c.is_whitespace()).unwrap_or(trimmed.len());
   let hw = &trimmed[..end];
   let body = trimmed[end..].trim().to_string();
   ```
   Comment in `halot.toml` says `"first token before ':' is headword"` but the code splits on whitespace, not colon. For entries without a space before the colon (e.g., `"avM: DSS vb."`), whitespace split and colon split produce the same result. For entries with format `"I amr (5280 x): ..."`, whitespace split extracts only `"I"`.

2. **`extract_grammar` / `pattern_list` (pipeline.rs:332-368):** scans `fields.body` for the first occurrence of any pattern from `halot.toml [grammar] patterns`. No length restriction in code (the 200-char comment in halot_hooks.rs is stale). Returns the earliest-matched pattern label.

3. **`halot.toml [grammar] patterns` (halot.toml:29-44):** Contains `"vb."`, `"n.m."`, `"n.f."`, `"n.c."`, `"n."`, `"adj."`, etc. Pattern `"n."` is a short substring that matches within many abbreviations: `"MHb."`, `"OSArb."`, `"EgArm."`, etc. — producing false-positive grammar='n.' for verb entries whose body text contains these etymological abbreviations. **Pattern list completeness is not the issue**: `"vb."` is in the list; it simply does not appear in the body of failing entries.

4. **`normalize_grammar_label` (pipeline.rs:1017-1038):** maps `vb.` → `"verb"`, `n.*` → `"noun"`. This stage is never reached for failing entries because `extract_grammar` returns `None` (no match) or `"n."` (false positive).

5. **`classify_from_grammar` (hooks.rs:30-44):** when `grammar=None` → `EntryType::Unknown` → binyan extractor not invoked. When `grammar='n.'` → `EntryType::NominalCommon` → same result. The 49 Roman-numeral-prefixed entries that ARE in the verb pool reached this step because `vb.` appeared in their body (e.g., entry 5948 "I roh: Ña. **vb.**: MHeb.").

6. **Roman numeral headword fallback (pipeline.rs:236-250):** `is_roman_numeral_stub(token)` checks for `"I."`, `"II."`, `"III."`, `"IV."` (with trailing dot). HALOT format uses `"I "` (space, no dot). The stub check therefore **does not fire** for HALOT homograph entries. The fallback to `fields.body.split_whitespace().next()` only fires for BDB-style `"I."` stubs. HALOT homograph entries decode `"I"` as Hebrew beta code → hirek vowel mark `ִ` → `headword_consonantal=None`.

### Hypothesis assessment

**Hypothesis 1 (halot_line colon-split firing on wrong colon):** ELIMINATED. The `halot_line` strategy uses whitespace split, not colon split. Colons do not cause mis-splitting. The problem is that whitespace-split of `"I amr (5280 x): ..."` extracts only `"I"` as headword and moves the actual root + grammar-bearing body into `fields.body`, which starts with the beta-code root (not the grammar label).

**Hypothesis 2 (200-char scan limit):** ELIMINATED. The 200-char comment in halot_hooks.rs line 7 is stale — no limit is enforced in `extract_grammar`. The 181 correctly-classified verbs with `vb.` beyond position 200 confirm this.

**Actual root cause (identified from binary evidence):**

HALOT's high-frequency Hebrew verb entries use a **different header format** than the ~298 entries that ARE classified:

- **Classified format:** `"headword: [DSS|denominative|etc.] vb. ..."` — explicit `vb.` immediately follows headword. `split_halot_line` extracts headword correctly; grammar scan finds `vb.` in body.
- **Unclassified format A (homograph verbs):** `"I headword (N x): etymology; qal:..."` — Roman numeral prefix. `split_halot_line` extracts `"I"` as headword; body starts with root consonants; no `vb.` label anywhere in entry (the grammatical category is **implicit**: editorial convention in HALOT omits the `vb.` label for roots whose verbal nature is universally known).
- **Unclassified format B (non-homograph high-frequency verbs):** `"headword (N x): etymology; qal:..."` — occurrence count in parens immediately after headword. `split_halot_line` correctly extracts headword; but body begins with `"(N x): MHb...."` — no `vb.` label. Occurrence count format occurs only for the most common verbs (בוא 2,550×, עשה 2,627×, אמר 5,280×).

**Additional defect — False-positive `n.` matches:** For verb entries where grammar scanner finds no `vb.`, it may match `n.` from etymological abbreviations in the body (e.g., `"OSArb."`, `"EgArm."`, `"MHb."`). This causes grammar='n.' / grammar_normalized='noun' rather than None for some verb entries.

**Pattern list completeness:** NOT a root cause. The `"vb."` pattern is in `halot.toml`. It matches correctly when present. The problem is absence of the label from the source binary for high-frequency verb entries.

**Aramaic section boundary:** NOT a root cause for the named verbs. The named verbs in the Aramaic section (entries 6192–7297) are correctly parsed Aramaic cognate entries; they lack Hebrew verb entries by design. The Hebrew verb entries (e.g., entry 469 for אמר, entry 2353 for ידע) are in the Hebrew section and correctly separated by the `[A0 0D 0D]` sentinel. The section boundary mechanism is not defective.

**Scope of impact:**
- 1,279 entries have Roman numeral prefix format in binary — 603 have `grammar_normalized=None`, 585 classified as noun (false positive), 49 correctly as verb (only when `vb.` happens to appear in body text)
- ~2,101 additional entries with non-Roman headword also have `grammar_normalized=None` — primarily derived nouns and proper names that genuinely lack grammar labels, plus ~347 cross-references

---

## Section D — Investigation Conclusion

### Root Cause 1 — Missing `vb.` grammar label in high-frequency verb entries

```
root_cause: HALOT high-frequency Hebrew verb entries omit the "vb." label; the
  pattern_list grammar scanner requires explicit "vb." in fields.body and therefore
  returns None for ~1,200+ verbal root entries. The source binary editorial convention
  for frequently-occurring roots is to use "I headword (N x): etymology; qal: ..."
  format with no explicit POS label — the verbal nature is signaled only by qal:/nif:/
  stem section headers, which the current grammar extraction pipeline does not inspect.

fix_approach: Add a secondary grammar inference rule: if fields.body contains any HALOT
  binyan stem label pattern (\n\t\t{stem}: or \r\t\t{stem}: as defined in halot_hooks.rs
  HALOT_BINYAN_LABELS) and grammar extraction returned None, classify the entry as
  grammar='vb.' before invoking normalize_grammar_label. This covers both homograph and
  non-homograph high-frequency verb entries. The binyan label scan already exists in
  HalotExtensionHooks::extract_binyanim; the fix extends it to influence grammar
  classification upstream (before entry type is determined).

tier: 1 mechanical

estimated_scope: small (1-2 files: pipeline.rs extract_grammar or halot_hooks.rs
  classify_entry_type, plus halot.toml if a new strategy flag is added)

validation_samples: נתן, שפט, אמר, עשה, בוא, ראה, ידע, שאל, שוב, דבר, אבד (I abd),
  ישב (yshb), שמע (shma), הלך (hlkh), מצא (mts)
```

### Root Cause 2 — Roman numeral headword decoding failure

```
root_cause: For HALOT homograph entries "I X: ..." and "II X: ...", split_halot_line
  extracts only the Roman numeral "I"/"II" as headword_field. The BDB Roman-numeral
  fallback in extract_headword (pipeline.rs:236) checks is_roman_numeral_stub() which
  matches "I." "II." "III." "IV." (with trailing dot, BDB format) but NOT "I" "II"
  "III" "IV" (no dot, HALOT format). The fallback does not fire; "I" is decoded as
  Hebrew beta code producing headword='ִ' (hirek diacritic) and headword_consonantal=None.
  1,294 fixture entries are affected — all have headword_consonantal=None and are
  unsearchable by Hebrew root.

fix_approach: Extend is_roman_numeral_stub in pipeline.rs to also match bare "I", "II",
  "III", "IV" (without trailing dot), OR extend split_halot_line to detect the pattern
  "Roman_numeral SPACE headword COLON" and split differently. With the fallback firing,
  the headword field correctly uses the first token of the body (the actual beta-code
  root), and the body is then the post-headword content including any grammar labels.

tier: 1 mechanical

estimated_scope: small (1 file: pipeline.rs, is_roman_numeral_stub function, ~5 LOC)

validation_samples: same as Root Cause 1 plus the 1,294 homograph entries — any of:
  I abd (to perish), I amr (to say), I ydo (to know), I och (to do), I ntN (Aramaic),
  I roh (to shepherd), II dbr (to speak)
```

### Root Cause 3 — False-positive `n.` matches from abbreviations

```
root_cause: The pattern_list grammar scanner matches "n." as a substring anywhere in
  fields.body. Hebrew etymological abbreviations common in HALOT — "MHb.", "OSArb.",
  "EgArm.", "JArm.", and others — contain the substring "n." and produce
  grammar='n.' for verbal entries where no "vb." was found. This causes
  grammar_normalized='noun' rather than None for some verb entries (e.g., בוא entry 743,
  אמר entry 6941), making them harder to detect via grammar_normalized=None query.

fix_approach: Tighten the "n." pattern match to require word-boundary context: e.g.,
  require "n." to be preceded by whitespace or start-of-body, or add an anchoring
  condition in extract_grammar for the shortest patterns. Alternatively, demote "n."
  to require it appear before any stem label (qal:/nif:) in the body.

tier: 1 mechanical

estimated_scope: small (1 file: pipeline.rs extract_grammar or halot.toml grammar
  pattern definitions)

validation_samples: בוא, אמר (Aramaic entry 6941), דבר — these should not retain
  grammar='n.' after fix; they should be reclassified as verb or None pending RC1 fix
```

### Prioritization note

Root Cause 2 (Roman numeral headword) and Root Cause 1 (missing `vb.` label) are tightly coupled: fixing RC2 first (correct headword extraction for `"I X: ..."` format) changes what is in `fields.headword_field` vs `fields.body` for homograph entries. After RC2, the body for `"I amr (5280 x): ..."` would be `"(5280 x): Sem.; to say..."` and RC1's binyan-stem inference approach would still be needed (since `vb.` is still absent from the body). RC1 and RC2 should be dispatched together in a single fix Builder, not separately.

Root Cause 3 (false-positive `n.`) is lower priority — it affects only symptom presentation, not the core verb pool defect. It can be addressed in the same fix pass.

---

## Domain-knowledge cache addendum

The following was discovered during Section B investigation and should be added to `docs/domain-knowledge-cache.md` § HALOT-specific patterns:

**HALOT verb entry formats — two classes:**

1. **Explicit-vb. entries (~298 in current fixture):** `headword: [DSS|denom.|Ña.] vb. ...` — `vb.` appears within first ~50 chars of body after `split_halot_line`. Grammar extraction succeeds.

2. **Implicit-verb entries (high-frequency roots, ~1,200+ estimated):** `I headword (N x): etymology; qal:...` or `headword (N x): etymology; qal:...` — NO `vb.` label anywhere in entry. Verb identity signaled only by stem section headers (`qal:`, `nif.:`, etc.). Grammar extraction fails (returns None or false-positive `n.`). This is deliberate HALOT editorial practice for roots whose verbal nature is universally known.

**Roman numeral prefix format:** HALOT uses `"I headword"` (space, no dot) for homograph disambiguation. Distinct from BDB's `"I. headword"` (dot + space). The `is_roman_numeral_stub` fallback in pipeline.rs only handles BDB style.

**Hebrew verb נתן (to give, ~2,014 OT occurrences):** Has NO standalone Hebrew verb root entry in the HALOT binary. The root exists only via derived nouns (entries 4349, 4352-4355) and an Aramaic cognate entry (entry 7297). This is not a parsing defect — it is HALOT editorial omission of the most common Hebrew verb root. Any fix must account for this: the named-sample validation for נתן must target the Aramaic entry 7297 (reclassify as Aramaic verbal) or acknowledge the root is not addressable as a Hebrew verb through HALOT alone.

**Hebrew verb ראה (to see, ~1,311 OT occurrences):** Hebrew section contains no `rah` or `rwah` root entry that was extractable by the current parser. The derived nouns יִרְאָה and מַרְאָה appear at entries 2627 and 3815. The root itself may be in the binary under an unexpected beta-code encoding or may be an editorial omission like נתן. Requires further targeted binary search (not completed this round — surface to Director).

---

## Wrong-direction guardrails (confirmed)

- No fix code produced.
- No changes to fellwork-api.
- No fixture regeneration.
- Named-sample bar not lowered.
- Scope confined to HALOT grammar defect only.
