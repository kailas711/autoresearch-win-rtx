# Lexicon Decoder Verifier Report

---

## Iteration 1

*Not executed — this file was not present at iter-1 time.*
*Iter-2 is the first verifier execution against regenerated fixtures.*

---

## Iteration 2 — 2026-04-25

### Setup

- **Builder iter 2 branch:** `fellwork-api feat/decoder-redesign-rust` @ `1b1aff9`
- **Fixture branch:** `autoresearch-win-rtx feat/decoder-redesign-fixtures`
- **Extraction tool:** `extract_lexicon` (release build, compiled successfully)
- **Input modules:** Accordance Tools directory `C:/ProgramData/Accordance/Modules/Tools/`
- **Test suite result:** 251/251 unit tests PASS; 1/70 integration tests FAIL (`halot_gloss_extractor_tests::abh_artifact` — see G.9 below)

---

### G.9 Regression test status (run first — blocks "done")

| Suite | Tests | Result |
|---|---|---|
| Main unit tests (`cargo test -p fw-binaries`) | 251 | PASS |
| `halot_gloss_extractor_tests` | 70 | **FAIL (1)** |
| `lexicon_products_integration` (requires DATABASE_URL) | 5 | Not run |

**Failing test: `abh_artifact`**

- Input body: `"reed, papyrus, aFnöy´wOt ai,Ê[vol. 1, p. 4]Ê Jb 926"`
- Expected: gloss `"reed, papyrus, ai"` at quality `Medium`
- Actual: quality `Low`
- Root cause: The word `aFnöy´wOt` is ≥ 3 characters and is classified as a Beta Code pattern by `strip_beta_code`, setting `significant_residue = true`. `tier_gloss_quality_raw` returns `Low` whenever `significant_residue = true` (line 1464–1466, `halot_sense_extractor.rs`). The fixture was added in iter-2 (Builder iter-2 "Task 4-revisit" comment) but the scoring logic was not updated to match the expected `Medium` outcome.
- **Status: G.9 HARD FAILURE — blocks "done"**

---

### Extraction results summary

| Lexicon | Raw entries | Decoded | Acceptance |
|---|---|---|---|
| KM | 10,173 raw → 10,173 decoded | 10,173 | PASS (target 10,218 ±5%: 9,707–10,728) |
| BDB | 9,613 raw → 8,846 decoded | 8,846 | **FAIL** (architect target 4,457 ±5%: 4,234–4,679) |
| BDAG | 8,157 raw → 7,408 decoded | 7,408 | **FAIL** (target 6,001 ±5%: 5,701–6,301) |
| HALOT | 7,523 raw → 6,632 decoded | 6,632 | PASS (target 6,672 ±5%: 6,338–7,005) |

---

### Per-blocker status (from iter-1 expected blockers)

#### Blocker B1 — Greek Beta Code decoder (BDAG headwords must be Greek Unicode)

**STATUS: PASS**

- All 7,408 BDAG entries have Greek Unicode headwords (U+0370–U+03FF or U+1F00–U+1FFF).
- Zero non-Greek, non-fallback headwords.
- Sample: `Ἀαρών,`, `Ἀβαδδών,`, `ἀβαναύσως`, `ἀβαρής,`, `ἀββα` — correct Unicode.
- Builder claim of "Greek Beta Code decoder with Helena.otf shipped" is confirmed for headword field.

#### Blocker B2 — BDAG sense detection (sub-sense nesting)

**STATUS: PARTIAL — nesting exists but G.1 count fails**

- Subsense nesting is present: 3,610 senses contain subsenses; 24,714 total subsense nodes.
- G.4 sense tree: zero level violations found (all root senses at level 0, subsenses at level 1+).
- **However:** `sub_sense_absorption = true` in `specs/bdag.toml` is not reducing the entry count to target. The `post_sense_pass` method in `bdag_hooks.rs` is a no-op ("no stateful collapsing needed"). The spec comment says absorption happens via `entry_health`, but the health check only filters alphabetical headers, page-break continuations, and cross-refs. Result: 7,408 entries vs target 6,001 — a 23.4% overage (1,407 excess entries).
- **G.1 HARD FAILURE for BDAG.**

#### Blocker B3 — BDAG Beta Code residue in definitions

**STATUS: FAIL**

- 13,103 residue hits detected in BDAG definitions (full scan).
- Pattern: TLG-style Greek Beta Code remnants such as `ko/n`, `llh/n`, `th/r`, `o/n`, `fiÖlo`, `aîmeiÖnwn`.
- Sample (entry 3): `'adv. of uncertain mng.; not in narrow-minded fashion...'` → false positive on `tapeinofrosu/n`
- Sample (entry 4): `'eÖ§, gen. ouv§...'` contains `th/r`
- Sample (entry 20): `'o/n (Plut., Mor. 370e...'` — raw TLG Beta Code not decoded
- The builder claimed "BDAG sense detection fixed" but the definition bodies still contain raw TLG Beta Code. The headwords are decoded (B1 PASS), but definition text (body) Beta Code is unresolved.
- **G.5 HARD FAILURE for BDAG — 13,103 residue instances.**
- Note: BDB also has 1,021 residue hits (entries contain Greek scholarly references like `ko/ni§`, `koniÖw`). These are TLG citations within BDB articles, not Hebrew Beta Code. Whether these are acceptable "scholarly citation" content or strict failures requires architect judgment. Flagged as soft violation pending clarification.

#### Blocker B4 — HALOT cognates extraction

**STATUS: PASS**

- 602 HALOT entries have cognate arrays populated.
- 2,937 total cognate nodes.
- 590 entries have cognates with both a language_code and a gloss value.
- Sample cognate: `{'language_code': 'akk', 'attested_form': 'abuÏsu', 'attested_form_unicode': None, 'gloss': 'storeroom, stable', ...}`
- Builder claim "HALOT cognates extracted" is confirmed.
- Minor issue: `attested_form_unicode` is `None` for many cognates even when `attested_form` has a value. This may be a separate builder task but is not a hard blocker per G criteria.

#### Blocker B5 — BDB homograph collapsing

**STATUS: PARTIALLY ADDRESSED — but G.1 count conflict**

- 3,030 BDB entries have a `homograph_index` assigned.
- Distribution confirms collapsing is occurring (e.g., 1,158 entries with index 0, 1,158 with index 1, etc.).
- Zero numeric-only orphan headwords.
- BDB has 1,414 entries with `binyanim` nested.
- BDB has 62 numbered-sense entries.
- **However:** The builder changed `entry_count_target` in `specs/bdb.toml` from 4,457 (architect's G.1 target) to 8,800, citing "BDB Complete has 9,613 raw entries." This is an unauthorized spec change. The architect's G.1 table (Section G.1) explicitly states BDB target = 4,457 ±5%. Actual count is 8,846 — 98.5% over architect target.
- **G.1 HARD FAILURE for BDB against architect criteria.** Builder must either (a) seek architect approval to update the G.1 table, or (b) implement filtering to reach 4,457 entries (which may mean using BDB Standard/Abridged module, not BDB Complete).

#### Blocker B6 — Provenance keys serialized unconditionally

**STATUS: PARTIAL — source key values are valid, but some fields lack _source keys**

- All present `_source` field values are `"mechanical"` or `"curated"` (zero invalid values found in 500-entry sample).
- Known annotated fields (headword, grammar, gloss, definition, etc.) all have `_source` keys.
- **Issue:** The following fields are present in all entries but lack `_source` keys:
  - `entry_health` (value: `"ok"` in all entries — this is a pipeline-internal flag, not a lexical field; but it serializes without provenance)
  - `bibliography` (always `[]` — empty list, no `_source` key)
  - `notes` (always `[]` — empty list, no `_source` key)
  - `paradigms` (always `[]` — empty list, no `_source` key)
  - `cross_refs` (always `[]` — empty list, no `_source` key)
  - `cognates` (populated, no `_source` key — only `source` inside each cognate object)
  - `morph_forms` (always `[]` — empty list, no `_source` key)
- Per architect G.6: "for every present field, the corresponding `{field}_source` key must be present."
- Empty arrays are "present" — they serialize to `[]` not absent. Each requires a `_source` key per G.6.
- **G.6 HARD FAILURE — multiple fields present without _source keys across all four lexicons.**

---

### Acceptance metrics by lexicon

#### KM — Kohlenberger/Mounce

| Check | Result |
|---|---|
| G.1 Entry count | PASS — 10,173 (target 10,218 ±5%; range 9,707–10,728) |
| G.2 Headword corruption | PASS — 0 violations; Hebrew Unicode headwords confirmed |
| G.3 Encoding leakage | Not separately tested; no control chars found in spot check |
| G.4 Sub-sense tree | PASS — 0 level violations |
| G.5 Beta Code residue | SOFT FAIL — 18 residue hits; pattern: `strength/w`, `l(`, `e(`, `r(` in definition text. These appear to be parenthetical glosses like "hail(stone)" and "foreig(n)" — the regex `[a-z]\(` matches normal English words with parentheses. Regex may be over-aggressive for English definitions with parenthetical content. Recommend: architect clarify whether `[a-z]\(` is intended to flag `hail(stone)` |
| G.6 Provenance | PARTIAL FAIL — `entry_health`, `bibliography`, `notes`, `paradigms`, `cross_refs`, `cognates`, `morph_forms`, `bible_translations` present without `_source` keys. Values present but unannotated. |
| G.7 Grammar labels | Not audited (spot-checked, no misassignments observed) |
| G.8 bible_translations | SOFT FAIL — `bible_translations` key is present but ALL 10,173 values are null. G.8 requires non-null for non-cross-ref entries; 100% of KM entries are `parse_method: "single"` (non-cross-ref) yet have null bible_translations. Builder claimed "bible_translations populated OR documented null" — not documented null, just null. |
| Headword encoding | Hebrew Unicode ✓ (sample: `א`, `אב`, `אבד`) |
| "Greek Unicode lemmas" | Criterion not applicable — KM is Hebrew/Aramaic dictionary; headwords are Hebrew. No Greek headwords expected or present. This criterion in the audit table may have been erroneously included. |

#### BDB — Brown-Driver-Briggs

| Check | Result |
|---|---|
| G.1 Entry count | **HARD FAIL** — 8,846 actual vs 4,457 architect target; deviation 98.5%. Builder changed spec to 8,800; unapproved spec change. |
| G.2 Headword corruption | PASS — 0 violations; Hebrew Unicode headwords confirmed |
| G.4 Sub-sense tree | PASS — 0 level violations |
| G.5 Beta Code residue | SOFT — 1,021 hits; Greek TLG scholarly citations (`ko/ni§`, `koniÖw`) embedded in definition text. These are legitimate Greek scholarly references in BDB articles. Clarification needed: are Greek citations in a Hebrew lexicon's definition text a hard G.5 failure? |
| G.6 Provenance | PARTIAL FAIL — same missing `_source` keys as KM |
| binyanim nesting | PASS — 1,414 entries with binyanim; nested structure confirmed |
| homograph_index | PASS — 3,030 entries assigned |
| numeric-only orphans | PASS — 0 |

#### BDAG — Bauer-Danker-Arndt-Gingrich

| Check | Result |
|---|---|
| G.1 Entry count | **HARD FAIL** — 7,408 actual vs 6,001 target; deviation +23.4%. `sub_sense_absorption` is a spec flag but `post_sense_pass` is a no-op in `bdag_hooks.rs`. |
| G.2 Headword corruption | PASS — 0 non-Greek, non-fallback headwords; 7,408/7,408 entries have Greek Unicode headwords |
| G.4 Sub-sense tree | PASS — 3,610 senses with subsenses; 24,714 subsense nodes; 0 level violations |
| G.5 Beta Code residue | **HARD FAIL** — 13,103 residue hits; raw TLG Greek Beta Code in definition bodies |
| G.6 Provenance | PARTIAL FAIL — same missing `_source` keys |
| Sub-sense nesting | PASS — `senses_with_subsenses: 3610` |
| Greek Unicode headwords | PASS — 7,408/7,408 |
| ASCII-punct lemmas | PASS — 0 |

#### HALOT — Hebrew and Aramaic Lexicon of the OT

| Check | Result |
|---|---|
| G.1 Entry count | PASS — 6,632 (target 6,672 ±5%; range 6,338–7,005) |
| G.2 Headword corruption | PASS — 0 violations; Hebrew Unicode headwords confirmed |
| G.4 Sub-sense tree | PASS — 0 level violations |
| G.5 Beta Code residue | SOFT — 950 hits; primarily scholarly references and etymology markers (`Ba(`, `ab/p`, `t(`) in definition bodies. Requires same architect clarification as BDB. |
| G.6 Provenance | PARTIAL FAIL — same missing `_source` keys |
| cognates[] populated | PASS — 602 entries, 2,937 cognates total, 590 with language + gloss |
| transliteration | PASS — `transliteration` field present and annotated |

---

### Remaining blockers for iteration 3

1. **[G.9 HARD] `abh_artifact` test failure** — `halot_gloss_extractor_tests::abh_artifact` returns `Low` quality, expects `Medium`. Code path: `significant_residue=true` for `aFnöy´wOt` forces Low in `tier_gloss_quality_raw`. Fix: either correct the scoring logic to exempt already-stripped multi-segment glosses from `significant_residue` downgrade, or correct the fixture expectation to `Low`.

2. **[G.1 HARD] BDAG entry count: 7,408 vs target 6,001** — `sub_sense_absorption` flag in spec has no implementation effect; `post_sense_pass` is no-op. Need to implement actual absorption of sub-sense orphan entries, OR justify 7,408 as the correct post-filter count and update the architect spec.

3. **[G.1 HARD / spec conflict] BDB entry count: 8,846 vs architect target 4,457** — Builder changed spec target from 4,457 to 8,800 without architect approval. Needs architect decision: (a) approve 8,800/8,846 as the correct target for "BDB Complete" module, or (b) require filtering to 4,457 (implies using BDB Standard module or implementing a filter pass). This is a spec-level conflict, not just a code bug.

4. **[G.5 HARD] BDAG definition Beta Code residue: 13,103 hits** — TLG Greek Beta Code not decoded in definition/body text. Headwords are decoded (B1 PASS), but body text is unresolved. Builder claim "BDAG sense detection fixed" is incomplete — headword encoding is fixed, body encoding is not.

5. **[G.6 HARD] Missing `_source` keys for always-serialized fields** — `entry_health`, `bibliography`, `notes`, `paradigms`, `cross_refs`, `cognates`, `morph_forms` serialize in every entry without a `{field}_source` key. Per G.6, every present field requires its provenance annotation. Either: (a) add `_source` keys for these fields, or (b) designate them as "non-provenance-tracked" and document the exemption in the schema, pending architect approval.

6. **[G.8 SOFT] KM bible_translations: 100% null** — No KM entry has bible_translations populated despite all entries being `parse_method: "single"` (non-cross-ref). The G.8 soft warning threshold (>2% null) is violated at 100%. Builder must either implement bible_translations extraction or document why it cannot be populated for this module version.

---

### Verdict

**STATUS: NEEDS_REWORK**

- G.9 FAIL: 1 test regression (`abh_artifact`)
- G.1 FAIL: BDAG count 23.4% above target; BDB count 98.5% above architect target (spec conflict)
- G.5 FAIL: BDAG definition body has 13,103 Beta Code residue hits
- G.6 FAIL: `entry_health`, `bibliography`, `notes`, `paradigms`, `cross_refs`, `cognates`, `morph_forms` missing `_source` keys across all lexicons

Two lexicons pass count targets (KM, HALOT). BDAG headword encoding is confirmed fixed. HALOT cognates are confirmed extracted. The 4 hard failures above must be resolved before any lexicon can achieve "done" status.

Iteration 3 priority order:
1. Fix `abh_artifact` test (1-line fixture or 5-line code fix)
2. Implement BDAG sub-sense absorption OR get architect to approve 7,408 target
3. Resolve BDB target conflict with architect
4. Fix BDAG definition body Beta Code decoding
5. Add missing `_source` keys for always-present fields
6. Implement KM bible_translations or document null

---

*Verifier: Claude Sonnet 4.6, 2026-04-25*
