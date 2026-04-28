# Plan #6 — Corpus Assembly Architecture Spec

**Date:** 2026-04-28 (v3 — applies Q3=C clarifications on top of v2's three corrections)
**Author:** Architect (Mode 2, r7 dispatch)
**Branch:** `feat/plan-6-corpus-architecture`
**Builder target:** r8 implementation dispatch
**Status at writing:** all sections complete; revised twice post-user-review

---

## Design corrections (post-r7 user review)

The user reviewed v1 on 2026-04-28 (three corrections applied in v2) and answered six approval questions on the same day; Q3 returned answer **C — both interpretations apply**, prompting two further refinements applied in v3. This section records all corrections in chronological order so future readers see the full rationale without digging through commit history.

### Correction 1 — Drop source-derived IDs from token identity; joins are linguistic

**User's verbatim guidance (v2 round):** "The link should be based on the linguistic identifiers not just a derived index number from a source. Strong's is only for KJV interlinear and does not help here. We are working on individual token instances, were as the Strong's concordance just does a blanket meaning for the word no matter the context incorrectly."

**Impact:**
- `bdb_key`, `halot_key`, `km_number`, `bdag_key`, `thayer_key`, `lsj_key` are NOT identity fields. They are removed from § A as required token-identity fields and never participate in joins.
- Token identity is purely linguistic: `token_id`, `surface`, `lemma`, `lemma_vocalized`, `morphology_code`, `binyan`, optionally `root`. Fingerprint (§ D) is over these.
- Lexicon joins are computed at corpus-build time via linguistic match (lemma + morphology + binyan compatibility) and stored in a denormalized convenience field `lexicon_links`. Source-ID-based joins are explicitly rejected as a category mistake — Strong's is a concordance index, not a linguistic identifier.

**v3 refinement (Q3=C, Effect 1):** Strong's and GK numbers are PRESERVED in the per-token record as `cross_walk_references` (a non-identity reference field group). They are kept for interop with concordance-keyed external resources — other people's notes, older commentaries, study Bibles keyed by Strong's. They are NOT in the fingerprint, NOT identity, NOT used for join logic. They are descriptive cross-walk metadata only. The user's clarification: full removal was too aggressive; the rejection is of Strong's/GK as identity and as join key, not as preserved cross-reference data. See § A `cross_walk_references` field group; § D fingerprint exclusion note; § H.5 updated rejection scope.

### Correction 2 — Per-passage translations belong in their own table

**User's verbatim guidance:** "How will that work when we translate and the words or phrasing are moved around from english or language X translation?"

**Impact:**
- Translations are NOT a per-token attribute. They are passage-grain prose with their own structural reordering.
- New section § B' introduces `data/corpus/hebrew/translations.jsonl` — one row per `(passage_id, target_language, source_attribution)` triple.
- Token-to-prose alignment is deferred to v2 (§ J); v1 stores translations as plain text per passage. The decoder will learn token-to-prose correspondence through attention; explicit gold-alignment artifacts are a separate later round.

### Correction 3 — Interlinear glosses ARE per-token (and per-token-aligned by source)

**User's verbatim guidance:** "Will it still be able to map the interlinear links to the tokens/lemma"

**Impact:**
- Interlinear glosses are per-token by source construction — `.ainter`, `.agloss`, STEPBible interlinear all attach gloss strings to individual Hebrew tokens. No alignment computation required; the alignment IS the source data.
- New per-token field `interlinear_glosses: list[{gloss, source, language}]` replaces the v1 `gloss_en` and `catss_alignment` fields, which were single-source single-language flatteners.
- Distinct from per-passage translations (§ B') which require alignment work that we defer.

### Correction 4 (v3, Q3=C, Effect 2) — STEPBible TSV restored as primary linguistic data source

**Context:** Q3 of the spec-v2 approval round asked whether the demotion of STEPBible TSV to "paragraph-marker + interlinear-gloss source only" was acceptable. The user answered **C — both interpretations apply**, signalling that the v2 demotion was too aggressive and lost STEPBible's actual contribution.

**Impact:**
- STEPBible TSV is restored as a **primary linguistic data source**, sitting alongside OSHB/ETCBC. Its purpose-built tables carry rich linguistic data (vocalized lemmas, morphology codes, Strong's↔GK cross-walks, paragraph markers, per-token interlinear glosses) that the corpus uses across multiple fields.
- STEPBible is **NOT** a join key (Correction 1 still stands — joins are linguistic, not source-ID-based). STEPBible is a normalized linguistic data source, distinct from being an indexing scheme.
- Specific field-by-field STEPBible role:
  - `lemma` (consonantal) — primary OSHB/ETCBC; STEPBible cross-checks; conflict resolution: prefer OSHB/ETCBC, flag divergence.
  - `lemma_vocalized` — **primary STEPBible TSV** (its vocalized lemma column is high-quality); cross-check OSHB; conflict resolution: prefer STEPBible TSV.
  - `morphology_code` — primary OSHB/ETCBC; STEPBible cross-checks; conflict resolution: prefer OSHB/ETCBC, flag divergence.
  - `cross_walk_references.strong_number` and `cross_walk_references.gk_number` — **primary STEPBible TSV** (its Strong's↔GK Hebrew table is the authoritative source).
  - `paragraph_marker_post` — primary STEPBible.
  - `interlinear_glosses` — STEPBible interlinear is one of the multiple gloss sources (alongside `.ainter`, `.agloss`).
- See § F sourcing pipeline for the full revised conflict-resolution table.

---

## Pre-design: Landscape audit

### Fixture inventory (measured; do not assume)

| Fixture | Type | Measured count | Key fields confirmed |
|---|---|---|---|
| `data/fixtures/lex_bdb.json` | list[dict] | **9,433** | `primary_key`, `headword_consonantal` (9,409/9,433), `headword_vocalized`, `grammar_normalized`, `binyanim`, `strongs` (0/9,433 — **null for all entries**), `gk_number` (0/9,433 — **null**), `senses`, `entry_health`, `_source` provenance keys on every annotated field |
| `data/fixtures/lex_halot.json` | list[dict] | **6,631** | Same schema as BDB; `primary_key` = `headword_consonantal`; `strongs` (0/6,631 — **null for all**), `gk_number` (0/6,631 — **null**); `headword_consonantal` present 6,619/6,631 |
| `data/fixtures/lex_km.json` | list[dict] | **10,173** | `primary_key` = `gk_H00001`-format; `gk_number` (int, 10,173/10,173 — **100% coverage**), `strongs` (10,019/10,173 — 98.5%); same schema as BDB/HALOT |
| `data/fixtures/genesis_full_hebrew.json` | dict[str, str] | **1,532** | Key format `Gen.1.1`; value = vocalized flat Hebrew string; no per-token decomposition |
| `data/fixtures/genesis_full_berean.json` | dict[str, str] | **1,532** | Same key format; value = English string |
| `data/fixtures/lex_thayer.json` | dict | **10,847** | Minimal schema: `lemma`, `gloss`, `definition` only (no `_source` provenance) |
| `data/fixtures/lex_lsj.json` | dict | **5,523** | Same minimal schema: `lemma`, `gloss`, `definition` |
| `data/fixtures/lex_bdag.json` | list[dict] | **7,384** | Full schema matching BDB/HALOT/KM with `_source` provenance keys |
| `gold/catalog.json` | dict with `entries[]` | **95 entries** | Fields: `ref_start`, `ref_end`, `translation`, `source_pdf`, `confidence`, `match_notes`, `book_section`, `is_partial`; books: Gen (67), Ps/Psalm, Deut, Isa, Ezek, NT refs |
| `gold/rubric.md` | markdown | **430 lines, 15 patterns (P1–P15)** | All 15 patterns present |

### Critical join field finding (now redirected by Correction 1)

The v1 spec recommended joining to BDB/HALOT via Strong's number; landscape audit found **0/9,433 BDB and 0/6,631 HALOT entries have `strongs` populated**. Per Correction 1, this mechanical limitation is no longer the primary issue — the deeper issue is that Strong's-based join is linguistically wrong regardless of fixture coverage. KM has `gk_number` 100% coverage and could be joined numerically, but Correction 1 directs that joins go through the linguistic path (lemma + morphology + binyan match against `headword_consonantal`) for ALL Hebrew lexicons. KM gets the same lemma-match treatment as BDB and HALOT.

### Gap Plan #6 fills

Every per-token field needed for the corpus is absent from all current fixtures:
- `surface` (per-token) — `genesis_full_hebrew.json` has verse-level flat strings only
- `lemma`, `lemma_vocalized`, `morphology_code`, `binyan`, `root` — no OSHB/ETCBC per-token data ingested yet
- `phrase_role`, `phrase_depth`, `clause_role` — no Macula Hebrew treebank ingested yet
- `interlinear_glosses` — no `.ainter`/`.agloss`/STEPBible per-token glosses ingested yet
- `lexicon_links` — no linguistic-match join executed yet
- `token_id`, `fingerprint`, `passage_id` — not present in any existing artifact
- Per-passage translations — `genesis_full_berean.json` has English by-verse but is not pericope-grained nor multi-language nor multi-attribution

### Do-not-break contracts

- `score_translate.py` reads `gold/catalog.json["entries"]` with `ref_start`/`ref_end` in `Book.chapter.verse` format and reads `data/fixtures/{corpus}_hebrew.json` as `dict[str, str]` keyed `Gen.1.1`. Plan #6 outputs are ADDITIVE — no modifications to these files.
- `prepare_translate.py` reads `data/fixtures/{corpus}_hebrew.json` + `data/fixtures/{corpus}_berean.json` as flat verse dicts. Same: Plan #6 does not touch these.
- Plan #6 corpus goes to `data/corpus/hebrew/` — a new directory that does not conflict with any existing path.
- The `Book.chapter.verse` key namespace is preserved: `token_id = Gen.1.1.0` starts with `Gen.1.1`, which is the existing verse key.

### Source data availability

| Source | Status | Notes |
|---|---|---|
| `lex_bdb.json`, `lex_halot.json`, `lex_km.json` | **Immediately available** | In `data/fixtures/` |
| OSHB (OpenScriptures GitHub) | **Fetch required** | Public; `github.com/openscriptures/morphhb`; OSIS XML |
| STEPBible TSV (paragraph markers + interlinear) | **Fetch required** | Public; `github.com/STEPBible/STEPBible-Data` |
| Macula Hebrew | **Fetch required** | Public; `github.com/Clear-Bible/macula-hebrew`; TSV/JSON treebank |
| Sefaria API | **Available (backup only)** | HTTP; cleanup required per domain-knowledge-cache |
| Accordance `.agloss` (per-token gloss) | **Locally available** | `MT-E words.agloss`; offset-driven parser needed (new code) |
| Accordance `.ainter` (per-token CATSS gloss) | **Locally available** | `MT-LXX Interlinear.ainter`; verse-ref table at 0x5A400C |
| Berean Standard Bible (per-passage translation) | **Available** | `genesis_full_berean.json` already in fixtures; relicense for `translations.jsonl` ingest |
| User gold catalog (per-passage translation) | **Available** | `gold/catalog.json` ingest as `gold_user_owned` license |
| Anchor Bible Dictionary (per-passage metadata) | **Licensing uncertain** | Flag: v1 passage metadata for disputed fields defaults null or mechanical; future pass fills in when access confirmed |

---

## A. Per-token table schema

Output file: `data/corpus/hebrew/v1.jsonl` — one JSON object per line, one line per Hebrew scripture token.

### Identity fields (linguistic only)

These fields define what a token IS. Per Correction 1, source-derived index numbers (Strong's, GK, lexicon keys) are NOT identity.

| field | type | source(s) | required | nullable | fingerprint | derivation/notes |
|---|---|---|---|---|---|---|
| `token_id` | str | derived | yes | no | yes | `<book>.<chapter>.<verse>.<token_index>`; e.g. `Gen.1.1.0`; § C |
| `fingerprint` | str (32 hex chars) | derived | yes | no | n/a (is the hash) | BLAKE2b-128 over the linguistic-identity fields below; § D |
| `passage_id` | str | derived | yes | no | no | FK into `passages.jsonl`; format per § E |
| `surface` | str | OSHB | yes | no | yes | Vocalized Hebrew surface form including cantillation marks |
| `lemma` | str | OSHB/ETCBC | yes | no | yes | Consonantal lemma, no vocalization, no cantillation |
| `lemma_vocalized` | str | OSHB/ETCBC | yes | yes | yes | Vocalized lemma; primary disambiguator for homographs at the linguistic level (replaces Strong's-as-disambiguator); null only when OSHB does not supply |
| `morphology_code` | str | OSHB/ETCBC | yes | yes | yes | ETCBC tag string; e.g. `HVqp3ms` = Hebrew Verb Qal perfect 3ms; null for untokenizable particles |
| `binyan` | str | derived from morphology; lexicon fallback | no | yes | yes | Verb stem enum (Qal, Niphal, Piel, …, Aramaic stems); together with `lemma_vocalized` linguistically disambiguates homographs that Strong's would have flattened |
| `root` | str | OSHB/ETCBC if available | no | yes | no | Triliteral or biliteral root if extractable from OSHB/ETCBC; null otherwise. Distinct from `lemma`: lemma is the lexicalized form, root is the consonantal abstraction. Not in fingerprint because it's derivative |
| `phrase_role` | str | Macula Hebrew | no | yes | no | Phrase-node function (Subject, Object, Modifier, Predicate, VerbPhrase, PrepPhrase, Apposition, NounPhrase); null if Macula coverage absent |
| `phrase_depth` | int | Macula Hebrew | no | yes | no | Nesting depth within Macula clause tree; 0 = clause level; null if Macula absent |
| `clause_role` | str | Macula Hebrew | no | yes | no | Clause function (RelativeClause, TemporalClause, MainClause, etc.); null if Macula absent |

### Per-token annotation fields (non-identity)

These fields describe attributes of a token but do not define identity. They can change without changing the token.

| field | type | source(s) | required | nullable | fingerprint | derivation/notes |
|---|---|---|---|---|---|---|
| `cross_walk_references` | object `{strong_number, gk_number}` | STEPBible TSV (primary); OSHB embedded Strong's (cross-check) | no | yes (any field inside may be null; the object itself may be null only if neither field is populated) | no | **Non-identity reference data.** Concordance numbers preserved on each token for interop with external resources keyed by Strong's / GK (other people's notes, older commentaries, study Bibles). NOT used for fingerprint. NOT used for lexicon join. See structure and rationale below. v3 addition (Q3=C, Effect 1) |
| `interlinear_glosses` | list[{gloss, source, language}] | `.ainter`, `.agloss`, STEPBible interlinear | no | yes (empty list allowed) | no | Per-token glosses from interlinear sources; multilingual; one entry per source. See structure below |
| `lexicon_links` | list[{lexicon, entry_ref, match_evidence}] | derived join (linguistic match) | no | yes (empty list allowed) | no | **Derivative not identity.** Pre-computed lexicon-match results stored as a convenience field. See structure and computation logic in § F |
| `paragraph_marker_post` | bool | STEPBible TSV / OSHB | no | yes | no | True if a paragraph break follows this token in the MT tradition; false otherwise; null if source doesn't specify |
| `qere_surface` | str | OSHB | no | yes | no | The qere (marginal reading) surface form if this token is a ketiv; null otherwise; paired with `annotation_flags: ["ketiv"]` |
| `annotation_flags` | list[str] | curated / derived | no | yes (empty list allowed) | no | Curator or mechanical tags; e.g. `["ketiv"]`, `["proclitic"]`, `["maqaf-compound"]`, `["sefaria-surface-divergence"]`, `["halot-multiple-match"]`; NOT in fingerprint |
| `source_provenance` | str | derived | yes | no | no | Comma-separated source identifiers contributing fields; e.g. `"OSHB,Macula,STEPBible,.ainter"` |

### Substructure: `cross_walk_references` (v3 addition; Q3=C, Effect 1)

The `cross_walk_references` object groups concordance numbers preserved for external interop. It is **non-identity reference data**: not in the fingerprint, not used for joins, not used for any logical operation. Its only purpose is to let downstream consumers of the corpus look up notes, commentaries, or study-Bible entries that are keyed by Strong's or GK.

```
{
  "strong_number": str | null,   // Hebrew Strong's: "H0001"–"H8674" zero-padded; null when source has no entry
  "gk_number":     str | null    // Goodrick-Kohlenberger: "H1"–"H10000" range with H prefix; null when source has no entry
  // future: room for additional cross-walk numbering schemes (Mounce, OSHB-internal, etc.) without schema break
}
```

**Field-by-field:**
- `strong_number` — Hebrew Strong's number; format `H` + zero-padded 4-digit (e.g., `H0001`, `H0430`, `H8674`). Source: STEPBible TSV (primary); OSHB embedded `<w lemma="strong:H####">` (cross-check). Conflict resolution: STEPBible wins; OSHB used as backup.
- `gk_number` — Goodrick-Kohlenberger Hebrew number. Source: STEPBible TSV Strong's↔GK Hebrew table.

**Population rules:**
- The object itself is present on every token. Either nested field may be `null` if that source did not provide a value.
- The object may be entirely null (`"cross_walk_references": null`) only when neither field has data — typically for non-content tokens (paragraph markers, particles with no concordance entry).

**What this is NOT:**
- NOT identity. Two tokens with identical `cross_walk_references` but different lemmas/morphology are NOT the same token.
- NOT a join key. Lexicon `lexicon_links` is computed via linguistic match (§ F); it does not consult `cross_walk_references`.
- NOT in the fingerprint. See § D explicit exclusion note.

**Why preserved:** Per Q3=C clarification, the user wants concordance numbers retained for downstream interop with external resources. Strong's-keyed study Bibles, older commentaries, and third-party notes will look up tokens by Strong's number. Discarding the numbers entirely would break that interop without serving any modeling purpose. The numbers are cheap to store, and their presence makes the corpus useful as a research artifact beyond the immediate ML training pipeline.

### Substructure: `interlinear_glosses` entry

Each list element is an object:

```
{
  "gloss":    str,   // e.g. "say", "create", "in-the-beginning"
  "source":   str,   // e.g. "Accordance .ainter CATSS", "Accordance .agloss", "STEPBible interlinear"
  "language": str    // ISO 639-1 code: "en", "de", "la", "el" (Greek for CATSS-LXX); typically "en"
}
```

Multiple entries permitted; same gloss may appear from different sources for cross-validation. Empty list `[]` (not null) when no interlinear gloss data is available for a token.

### Substructure: `lexicon_links` entry

Each list element is an object:

```
{
  "lexicon":        str,   // "BDB", "HALOT", "KM"
  "entry_ref":      str,   // primary_key of the matched lexicon entry (e.g. "ברא" for BDB/HALOT, "gk_H01254" for KM)
  "match_evidence": str    // human-readable rationale; e.g. "lemma=ברא; morphology=HVqp3ms; binyan=Qal; matched headword_consonantal exact + binyanim has Qal"
}
```

Multiple entries permitted (one per lexicon, plus multiple matches within one lexicon if homograph disambiguation yields more than one candidate). The match logic and homograph rules are specified in § F.

This field is **derivative not identity**: it is a denormalized convenience to avoid re-running the lexicon-match computation at training time. The same `(lemma, lemma_vocalized, morphology_code, binyan)` tuple should always produce the same `lexicon_links` given pinned fixture versions.

### `binyan` enum values

`Qal`, `Niphal`, `Piel`, `Pual`, `Hiphil`, `Hophal`, `Hithpael`, `Polel`, `Hithpolel`, `Pilpel`, `Hithpalpel`, `Peal` (Aramaic), `Pael` (Aramaic), `Haphel` (Aramaic), `Ithpaal` (Aramaic), `Ithpeel` (Aramaic), `Aphel` (Aramaic), `Shaphel` (Aramaic). Null for non-verbs.

### What was removed vs preserved (per Corrections 1 + v3 Q3=C)

**Removed entirely (replaced by `lexicon_links`):**
- `bdb_key`, `halot_key`, `km_number` — source-internal lookup keys; replaced by `lexicon_links` (linguistic-match driven)
- `bdag_key`, `thayer_key`, `lsj_key` — Greek-track source keys; same rationale; will be similarly absent from Greek track schema

**Preserved as non-identity cross-walk reference data (v3 update; Q3=C, Effect 1):**
- `strong_number` — was a top-level identity field in v1 spec; in v3 lives inside `cross_walk_references` as descriptive interop metadata. Not in fingerprint.
- `gk_number` — same: was top-level v1; in v3 lives inside `cross_walk_references`. Not in fingerprint.

**Why the change between v2 and v3:** v2 removed Strong's/GK entirely (per Correction 1, "concordance numbers are not identity"). v3 preserves them as non-identity reference fields (per Q3=C, "preserve for external interop"). Both decisions are consistent: Strong's/GK are NOT identity (v1→v2 fix) AND are not removed entirely (v2→v3 fix). The v3 schema has them stored alongside identity fields for cross-walk only.

Strong's and GK numbers MAY still appear inside `lexicon_links[].match_evidence` strings as descriptive evidence (e.g., "BDB entry for ברא is associated with Strong's H01254 in STEPBible TSV" as part of the human-readable rationale).

The v1 fields `gloss_en` and `catss_alignment` are subsumed by `interlinear_glosses` (Correction 3); each becomes one entry in the list, distinguished by `source`.

---

## B. Per-passage metadata table schema

Output file: `data/corpus/hebrew/passages.jsonl` — one JSON object per line, one line per passage unit (pericope; grain per § E).

| field | type | source(s) | required | nullable | derivation/notes |
|---|---|---|---|---|---|
| `passage_id` | str | derived | yes | no | Primary key; format `Gen.1`; see § E |
| `book` | str | derived | yes | no | Book abbreviation matching token_id prefix |
| `chapter_start` | int | derived | yes | no | First chapter of the pericope (1-indexed) |
| `verse_start` | int | derived | yes | no | First verse of the pericope (1-indexed) |
| `chapter_end` | int | derived | yes | no | Last chapter; equals `chapter_start` for single-chapter pericopes |
| `verse_end` | int | derived | yes | no | Last verse |
| `verse_ref_start` | str | derived | yes | no | Canonical first verse ref: `Book.chapter.verse` |
| `verse_ref_end` | str | derived | yes | no | Canonical last verse ref |
| `canonical_section` | str enum | editorial | yes | no | Torah / Former-Prophets / Latter-Prophets / Writings (Hebrew Bible); Greek track adds Gospels / Pauline / General-Epistles / Apocalyptic |
| `author_tradition` | list[str] | editorial / scholarly | yes | no | Competing authorial attribution positions as list; never empty — mechanical default `["traditional"]` |
| `genre` | str enum | editorial | yes | no | narrative / poetry / legal / apocalyptic / wisdom / epistolary / prophetic |
| `subgenre` | str | editorial | no | yes | genealogy / etiological-narrative / wisdom-poem / lament / hymn / oracle / disputation / parable / creation-account / covenant-narrative |
| `era_estimate` | list[str] | scholarly | no | yes | Composition era range or competing positions |
| `language_register` | str enum | editorial | yes | no | formal / narrative / poetic / legal-formulaic / colloquial / liturgical |
| `audience` | str | editorial | no | yes | covenant-community / gentile-mission / individual-recipient / liturgical-assembly |
| `literary_devices` | list[str] | editorial | no | yes (empty list allowed) | parallelism-synonymous, parallelism-antithetic, parallelism-synthetic, chiasm, inclusio, wordplay, merism, anaphora, hendiadys, lament-structure, beatitude, doxology |
| `manuscript_witnesses` | list[str] | editorial | yes | no | Traditions attesting this passage; minimum `["MT"]` for all Hebrew Bible passages |
| `cross_canon_links` | list[str] | editorial | no | yes | Intertextual references using verse-ref notation; null initially |
| `pericope_source` | str | derived | yes | no | `"macula-discourse"`, `"stepbible-paragraph"`, `"editorial-heading"`, `"fallback-verse"` |
| `token_count` | int | derived | yes | no | Count of tokens with this `passage_id` |
| `source_provenance` | str | derived | yes | no | Comma-separated list of editorial sources |

**List-typed fields rationale:** `author_tradition`, `era_estimate`, `literary_devices`, `cross_canon_links` are list-typed to carry multiple scholarly positions without forcing a single answer. Per `feedback_corpus_dimensions.md`, the corpus encodes scholarly disagreement explicitly rather than picking a side.

---

## B'. Per-passage translations table schema (NEW per Correction 2)

Output file: `data/corpus/hebrew/translations.jsonl` — one JSON object per line, one line per `(passage_id, target_language, source_attribution)` triple.

### Schema

| field | type | source(s) | required | nullable | notes |
|---|---|---|---|---|---|
| `passage_id` | str (FK) | derived from corpus | yes | no | References `passages.jsonl[].passage_id` |
| `target_language` | str | source attribution | yes | no | ISO 639-1 code: `en`, `de`, `la`, `fr`, `es`, etc. |
| `source_attribution` | str | source-side metadata | yes | no | Free-form attribution string: `"Berean Standard Bible 2023"`, `"User gold catalog 2026-04-25"`, `"KJV 1769"`, `"Luther 1545"` |
| `text` | str | the translation source | yes | no | Full prose translation for the passage; preserves the translator's natural-target-language word order |
| `license_status` | str enum | editorial | yes | no | `public_domain`, `cc_by`, `proprietary_with_access`, `gold_user_owned` — gates redistribution downstream |
| `translation_date` | str | source-side metadata | no | yes | ISO 8601 date or year-only (`2023`, `1769`, `1545`); null if unknown |
| `translator_attribution` | str | source-side metadata | no | yes | Translator/committee name when available |
| `notes` | str | editorial | no | yes | Any per-translation notes (e.g., textual-base notes: "based on BHS 1997"; or genre alignment notes) |
| `alignment_artifact_ref` | str | derived (v2+) | no | yes | **Null in v1.** v2 will reference a separate per-token alignment artifact (e.g., `data/corpus/hebrew/alignments/<passage_id>__<source_attribution>.jsonl`); v1 leaves this null |
| `source_provenance` | str | derived | yes | no | Where this row's text was sourced from (e.g., `"data/fixtures/genesis_full_berean.json"`, `"gold/catalog.json"`) |

Multiple translations per passage are permitted by design: one row per `(passage_id, target_language, source_attribution)`. The triple is the natural primary key.

### Spec rationale (verbatim from Correction 2 brief)

Phrase tree is source-side only (encoder features). Translation is target-side prose with its own structure. Token-to-prose alignment is a v2 research artifact, NOT identity. Decoder generates target language in target's natural order; attention bridges reordering.

The Berean Standard Bible's English may render Hebrew SVO clauses as English SVO at a different surface order; Luther's 1545 German may use V2 word order; Latin Vulgate may compress a Hebrew construct chain into a single noun phrase. None of these structural differences disrupt the per-passage table because the table stores prose, not alignment. When the model is trained, it sees one Hebrew passage (multi-token, with full per-token annotations) paired with N candidate translations (each a prose string with its own structure); attention learns the correspondence implicitly.

### v1 ingest sources for `translations.jsonl`

| source | rows it contributes | license_status |
|---|---|---|
| `data/fixtures/genesis_full_berean.json` (1,532 verses) | One row per pericope by joining adjacent verses' English text into the pericope range | `public_domain` |
| `gold/catalog.json` (95 entries; 67 Genesis) | One row per gold entry; `passage_id` resolved by mapping `ref_start`/`ref_end` to the enclosing pericope; if the gold entry spans pericopes, split into one row per pericope | `gold_user_owned` |

Builder must handle the by-verse-to-by-pericope aggregation: for Berean, concatenate adjacent verse strings inside each pericope's verse range, joined with a space, to form the pericope-level prose. For gold catalog entries that don't align to pericope boundaries, the spec accepts that the gold entry may span multiple pericopes — split into one row per pericope, each carrying the same `text` content with `notes: "gold entry spans multiple pericopes; same text on each row"` flag, OR keep the gold entry on the smallest enclosing pericope and flag the verse-range mismatch in `notes`. Builder picks one approach and documents it; either is acceptable for v1.

### v2 path: alignment artifacts

The `alignment_artifact_ref` field is null in v1. In v2, a separate alignment artifact will store per-token correspondences for each `(passage_id, target_language, source_attribution)` triple. The artifact format is open: it could be a JSONL of `{source_token_id, target_word_index, confidence}` triples, or a CTranslate2-style alignment matrix, or a Macula-style cross-translation alignment. The corpus schema reserves the field name now to avoid future renames.

---

## C. Token-id format spec

### Hebrew format

```
<book>.<chapter>.<verse>.<token_index>
```

- `<book>` — canonical book abbreviation (table below), 3–4 chars
- `<chapter>` — 1-indexed integer, no leading zeros
- `<verse>` — 1-indexed integer, no leading zeros
- `<token_index>` — 0-indexed integer within the verse, counting OSHB-tokenized word units

Example: `Gen.1.1.0` = first word of Genesis 1:1 (בְּרֵאשִׁית).

### Hebrew book abbreviations

| Abbreviation | Book | Abbreviation | Book |
|---|---|---|---|
| `Gen` | Genesis | `Ps` | Psalms |
| `Exod` | Exodus | `Prov` | Proverbs |
| `Lev` | Leviticus | `Job` | Job |
| `Num` | Numbers | `Song` | Song of Songs |
| `Deut` | Deuteronomy | `Ruth` | Ruth |
| `Josh` | Joshua | `Lam` | Lamentations |
| `Judg` | Judges | `Eccl` | Ecclesiastes |
| `1Sam` | 1 Samuel | `Esth` | Esther |
| `2Sam` | 2 Samuel | `Dan` | Daniel |
| `1Kgs` | 1 Kings | `Ezra` | Ezra |
| `2Kgs` | 2 Kings | `Neh` | Nehemiah |
| `Isa` | Isaiah | `1Chr` | 1 Chronicles |
| `Jer` | Jeremiah | `2Chr` | 2 Chronicles |
| `Ezek` | Ezekiel | | |
| `Hos` | Hosea | | |
| `Joel` | Joel | | |
| `Amos` | Amos | | |
| `Obad` | Obadiah | | |
| `Jonah` | Jonah | | |
| `Mic` | Micah | | |
| `Nah` | Nahum | | |
| `Hab` | Habakkuk | | |
| `Zeph` | Zephaniah | | |
| `Hag` | Haggai | | |
| `Zech` | Zechariah | | |
| `Mal` | Malachi | | |

Note: `gold/catalog.json` uses both `Ps.` and `Psalm.` — Builder must canonicalize `Psalm.` → `Ps.` when joining gold references to the corpus token_id namespace.

### Greek book abbreviations (parity for future track)

NT: `Matt`, `Mark`, `Luke`, `John`, `Acts`, `Rom`, `1Cor`, `2Cor`, `Gal`, `Eph`, `Phil`, `Col`, `1Thess`, `2Thess`, `1Tim`, `2Tim`, `Titus`, `Phlm`, `Heb`, `Jas`, `1Pet`, `2Pet`, `1John`, `2John`, `3John`, `Jude`, `Rev`. Hebrew and Greek namespaces are orthogonal; no abbreviation collisions.

### Edge case handling rules

**Ketiv / Qere:**
The ketiv (written form) gets the canonical `token_id` and `surface`. The qere is NOT a separate token. Stored as: `surface` = ketiv, `qere_surface` = qere (nullable), `annotation_flags: ["ketiv"]`. Fingerprint is computed over the ketiv (canonical text).

**Proclitic prepositions / conjunctions:**
Follow OSHB tokenization as the canonical split decision. Each OSHB token unit = exactly one `token_id`. Builder must NOT re-tokenize.

**Maqaf-joined compounds:**
Follow OSHB tokenization. If OSHB produces two tokens, each gets sequential `token_index`; if one token containing maqaf, it gets one `token_id`. Tag with `annotation_flags: ["maqaf-compound"]` when the surface contains U+05BE.

**Paragraph markers:**
`paragraph_marker_post = true` on the last token of a verse with following paragraph break. Source: STEPBible TSV or OSHB `<milestone type="paragraph"/>`.

**Elision / DSS variants:**
Out of scope for v1 token_id generation. MT is the canonical text; variant readings are flagged at the passage level via `manuscript_witnesses`.

**Verse-final tokens:**
Token indices reset to 0 at the start of each verse.

### Stability contract

Pinned OSHB commit SHA + pinned ETCBC version + same processing order ⇒ deterministic `token_id` ordering. SHAs recorded in `manifest.json`.

---

## D. Fingerprint algorithm spec (revised per Correction 1; v3 cross-walk note added)

### Algorithm

BLAKE2b with 16-byte digest. Python stdlib: `hashlib.blake2b(payload, digest_size=16)`. Output: lowercase hex string, 32 characters.

### Input construction

```
1. Collect the 6 linguistic-identity fields (sorted by field name, ASCII order)
2. For each field: format as "<field_name>=<value>"
3. Join all formatted pairs with \x00 (null byte)
4. Encode the joined string to UTF-8 bytes
5. Compute hashlib.blake2b(payload, digest_size=16).hexdigest()
```

### Fingerprint-included fields (linguistic identity only)

Sorted ASCII order:

| field | canonical representation | null handling |
|---|---|---|
| `binyan` | verbatim enum value (e.g. `"Qal"`); empty string `""` if null/non-verb | `""` |
| `lemma` | verbatim consonantal Hebrew Unicode string | required; never null |
| `lemma_vocalized` | verbatim vocalized Hebrew string; empty string `""` if null | `""` |
| `morphology_code` | verbatim ETCBC tag string (e.g. `"HVqp3ms"`); empty string if null | `""` |
| `surface` | verbatim Unicode Hebrew surface form including cantillation | required; never null |
| `token_id` | verbatim string | required; never null |

Sorted ASCII: `binyan`, `lemma`, `lemma_vocalized`, `morphology_code`, `surface`, `token_id`.

### Why these fields (per Correction 1)

The user's design intent: same lemma in different positions can carry different curated annotations; concordance numbers (Strong's, GK) "blanket meaning regardless of context" and so they're inappropriate for token-level identity. The fingerprint must capture what the token is at this position, linguistically.

- `token_id` — position
- `surface` — vocalized form at this position (catches ketiv/qere distinction at the surface)
- `lemma` — consonantal lexicalization
- `lemma_vocalized` — vocalized lexicalization (the primary homograph disambiguator at the linguistic level — a job Strong's was crudely proxying)
- `morphology_code` — full ETCBC tag (binyan, person, gender, number, state)
- `binyan` — the verb-stem dimension specifically (extractable from morphology_code but elevated as a top-level field because it is the dominant Hebrew-verb identity dimension; redundancy is acceptable for stability)

`binyan` is included redundantly with `morphology_code` because: (a) `morphology_code` may be null for verbs with editorial gaps; `binyan` may be filled from lexicon fallback; including both ensures fingerprint reflects whichever data is available; (b) for non-verbs, both go to "" and contribute equally.

### Reference implementation (spec; not production code)

```python
import hashlib

FINGERPRINT_FIELDS = sorted([
    "token_id", "surface", "lemma", "lemma_vocalized",
    "morphology_code", "binyan",
])

def compute_fingerprint(token: dict) -> str:
    parts = []
    for field in FINGERPRINT_FIELDS:  # already sorted
        val = token.get(field) or ""
        parts.append(f"{field}={val}")
    payload = "\x00".join(parts).encode("utf-8")
    return hashlib.blake2b(payload, digest_size=16).hexdigest()
```

### Fields excluded from fingerprint

| field | reason |
|---|---|
| `passage_id` | Pericope grain may be revised without token changing |
| `root` | Derivative from lemma; can be recomputed |
| `phrase_role`, `phrase_depth`, `clause_role` | Macula annotations; updatable with Macula re-release |
| `lexicon_links` | **Derivative**; computed from linguistic identity, not part of identity |
| `interlinear_glosses` | Multi-source, multi-language; per-token annotations |
| `paragraph_marker_post`, `qere_surface`, `annotation_flags` | Editorial / curatorial |
| `source_provenance` | Administrative |
| `cross_walk_references` (`strong_number`, `gk_number`) | **Explicitly excluded per Correction 1.** Strong's/GK are concordance-flat indexes that don't reflect token-instance identity (one Strong's number maps to a "blanket meaning regardless of context"). They live alongside identity in the per-token record for cross-walk only. v3 update: preserved as non-identity reference data, not removed entirely (Q3=C, Effect 1) |

**Stability side-benefit:** Because `cross_walk_references` is excluded from fingerprint inputs, STEPBible TSV updates that revise Strong's↔GK mappings DO NOT invalidate token fingerprints. STEPBible can be re-vendored without triggering corpus-wide curation re-review. This is the design payoff for keeping concordance numbers out of identity.

### Stability requirement

Pinned OSHB + ETCBC ⇒ identical fingerprint on every re-run. STEPBible TSV updates DO change `cross_walk_references` values when STEPBible revises Strong's↔GK mappings, but they DO NOT invalidate token fingerprints — `cross_walk_references` is explicitly excluded from fingerprint inputs (§ D table above). This means: re-vendoring STEPBible is a `cross_walk_references` re-population task, not a curation re-review trigger. This is a side benefit of keeping Strong's/GK out of identity.

For fields that ARE in fingerprint inputs and where STEPBible is the primary source — specifically `lemma_vocalized` (per Correction 4 / Q3=C Effect 2) — STEPBible TSV updates that revise `lemma_vocalized` values WILL change fingerprints for affected tokens. Those tokens' curation requires re-review per the diff-driven re-curation protocol (`feedback_token_as_first_class_instance.md`). This is the standard workflow for any source update that touches identity.

### Collision properties

Because `token_id` is in fingerprint inputs and `token_id` values are globally unique, no two tokens can produce the same fingerprint regardless of other field equality. AC-2 (§ G) tests this globally.

---

## E. Passage grain decision

**Decision: per-pericope.**

### Options considered

| option | primary advantage | primary disadvantage |
|---|---|---|
| per-verse | 1:1 with existing key format; no boundary decisions | Too fine for passage metadata; redundant curation across adjacent verses |
| per-pericope | Natural unit for authorial context, literary devices, genre; Macula provides mechanical seeds | Requires pericope boundary source and decisions |
| per-chapter | Lowest boundary-decision burden | Chapters are 13th-century CE divisions; conflate distinct narrative episodes |

### Justification

**Per-verse rejected:** Passage metadata (genre, author_tradition, era_estimate, literary_devices) is identical for blocks of adjacent verses. Annotating 1,532 verses for Genesis when ~200 pericope rows would suffice = 7× curation burden for zero modeling signal. Literary devices (chiasm, inclusio) span multiple verses; assigning per-verse fragments the structure.

**Per-chapter rejected:** Genesis 1 contains both the creation account (1.1–2.3 — typically Priestly source) and the second-account transition (2.4a). One chapter, two distinct authorial units. Per-chapter conflates them.

**Per-pericope chosen because:**
1. Macula Hebrew provides `discourse_unit` annotations from which pericope boundaries are mechanically derivable.
2. All passage-level fields are naturally pericope-scoped.
3. Gold catalog entries (95) implicitly span pericope-level ranges.
4. Rubric patterns P1 (wayyiqtol chains), P3/P4 (parallelism), P7 (chiasm) are pericope-level phenomena.
5. Per-token records carry exact verse address via `token_id`; verse is recoverable, no granularity lost.

### Passage_id format

```
<book>.<pericope_index>
```

`<pericope_index>` = 1-indexed integer within the book. Example: `Gen.1` = first pericope of Genesis.

### Genesis pericope index (proposed; subject to Macula override)

| passage_id | verse_ref_start | verse_ref_end | description |
|---|---|---|---|
| `Gen.1` | `Gen.1.1` | `Gen.2.3` | Creation account |
| `Gen.2` | `Gen.2.4` | `Gen.2.25` | Second creation account / Eden intro |
| `Gen.3` | `Gen.3.1` | `Gen.3.24` | The fall |
| `Gen.4` | `Gen.4.1` | `Gen.4.16` | Cain and Abel |
| `Gen.5` | `Gen.4.17` | `Gen.4.26` | Cain's descendants + Seth's line intro |
| `Gen.6` | `Gen.5.1` | `Gen.5.32` | Genealogy: Adam to Noah |
| `Gen.7` | `Gen.6.1` | `Gen.6.8` | Sons of God / Nephilim |
| `Gen.8` | `Gen.6.9` | `Gen.7.24` | Noah's ark + flood onset |
| `Gen.9` | `Gen.8.1` | `Gen.8.19` | Flood receding |
| `Gen.10` | `Gen.8.20` | `Gen.9.17` | Covenant with Noah |
| `Gen.11` | `Gen.9.18` | `Gen.9.29` | Noah's sons + Noah's death |
| `Gen.12` | `Gen.10.1` | `Gen.10.32` | Table of Nations |
| `Gen.13` | `Gen.11.1` | `Gen.11.9` | Tower of Babel |
| `Gen.14` | `Gen.11.10` | `Gen.11.32` | Shem genealogy + Terah |

Macula discourse boundaries are authoritative; this table is the v1 fallback and validation seed.

### Pericope source hierarchy

1. **Primary:** Macula Hebrew `discourse_unit` annotations
2. **Secondary:** STEPBible paragraph markers
3. **Fallback:** `"editorial-heading"` from canonical commentary divisions
4. **Last resort:** `"fallback-verse"` — each verse becomes own passage; flag for v2 patching

Builder records the actual source in `pericope_source`. Disagreements between Macula and editorial are logged for Verifier review.

### Cross-canon link grain

Cross-canon links use verse-ref notation for the target side (`Book.chapter.verse`); NT pericope grain is deferred to the Greek track round.

---

## F. Sourcing pipeline (revised: linguistic-match joins per Correction 1; per-token interlinear per Correction 3; per-passage translations per Correction 2; STEPBible promoted to primary linguistic source per Correction 4 / Q3=C Effect 2)

### Authoritative source hierarchy

The "Source priority" column shows where each source is primary (P) versus cross-check (X) versus backup (B) for each field. STEPBible is now primary for `lemma_vocalized` and `cross_walk_references`, alongside OSHB which is primary for `surface`, `lemma`, `morphology_code`. v3 update reverses the v2 demotion of STEPBible.

| source | identifier | availability | feeds | source priority for those fields |
|---|---|---|---|---|
| OSHB | `github.com/openscriptures/morphhb` | Fetch required; public MIT | `surface`, `lemma`, `lemma_vocalized`, `morphology_code`, `root`, `cross_walk_references.strong_number` (embedded fallback) | **P** for `surface`, `lemma`, `morphology_code`; **X** for `lemma_vocalized` (cross-checks STEPBible); **X** for `strong_number` (fallback to STEPBible) |
| STEPBible TSV | `github.com/STEPBible/STEPBible-Data` | Fetch required; public CC BY | `lemma_vocalized` (vocalized lemma column); `morphology_code` (cross-check); `cross_walk_references.strong_number` and `.gk_number`; `paragraph_marker_post`; STEPBible interlinear column → `interlinear_glosses` | **P** for `lemma_vocalized`; **X** for `morphology_code`; **P** for `cross_walk_references.strong_number` and `.gk_number`; **P** for `paragraph_marker_post`; **P** for STEPBible-sourced `interlinear_glosses` entries |
| Macula Hebrew | `github.com/Clear-Bible/macula-hebrew` | Fetch required; public CC BY | `phrase_role`, `phrase_depth`, `clause_role`, pericope boundaries | **P** for all Macula fields |
| Sefaria API | `sefaria.org/api` | HTTP backup | `surface` backup | **B** for `surface` only |
| Accordance `.agloss` | `MT-E words.agloss` | Local; offset parser | `interlinear_glosses` entry with `source: "Accordance .agloss"` | **P** for `.agloss`-sourced `interlinear_glosses` entries |
| Accordance `.ainter` | `MT-LXX Interlinear.ainter` | Local; verse-ref table at 0x5A400C | `interlinear_glosses` entry with `source: "Accordance .ainter CATSS"` | **P** for `.ainter`-sourced `interlinear_glosses` entries |
| Lexicon fixtures | `data/fixtures/lex_*.json` | Immediately available | `lexicon_links` (via linguistic match — see below) | **P** for `lexicon_links` (no source-ID join; linguistic match) |
| Berean Standard Bible | `data/fixtures/genesis_full_berean.json` (already in repo) | Immediately available | `translations.jsonl` rows with `source_attribution: "Berean Standard Bible 2023"`, `license_status: "public_domain"` | **P** for Berean rows in `translations.jsonl` |
| User gold catalog | `gold/catalog.json` | Immediately available | `translations.jsonl` rows with `source_attribution: "User gold catalog 2026-04-25"`, `license_status: "gold_user_owned"` | **P** for gold rows in `translations.jsonl` |
| Anchor Bible Dictionary | (licensing pending) | Uncertain | `era_estimate`, `author_tradition` (passage metadata; v1 mechanical defaults) | (deferred — uncertain availability) |

**Note on STEPBible's role (v3):** STEPBible TSV is a **normalized linguistic data source**, not an indexing scheme. It carries vocalized lemmas, morphology codes, Strong's↔GK cross-walks, paragraph markers, and per-token interlinear glosses in purpose-built tables. The v2 spec demoted it to "paragraph-marker + interlinear-gloss only", which lost real content. The v3 restoration aligns STEPBible with OSHB/ETCBC as a primary linguistic source. STEPBible is **NOT** a join key; per Correction 1, lexicon joins remain linguistic-match only. The two ideas — "STEPBible carries linguistic data" and "STEPBible is not a join key" — are independent and both apply in v3.

### Per-token identity field sourcing

**`surface`:** **P** = OSHB OSIS `<w>` content. **B** = Sefaria with `strip_hebrew_html()`. Conflict resolution: OSHB wins; Sefaria divergence logged in `annotation_flags: ["sefaria-surface-divergence"]`.

**`lemma`:** **P** = OSHB OSIS `<w lemma="...">` (consonantal). **X** = STEPBible TSV consonantal lemma column (cross-check). Conflict resolution: prefer OSHB/ETCBC; STEPBible-OSHB divergence logged in `annotation_flags: ["stepbible-lemma-divergence"]` for Verifier review.

**`lemma_vocalized`:** **P** = STEPBible TSV (vocalized lemma column). **X** = OSHB if it supplies vocalized form. Conflict resolution: **prefer STEPBible TSV** (its vocalized lemma column is high-quality and purpose-curated); OSHB used as fallback when STEPBible has no entry. Null only when neither source supplies. v3 promotion: STEPBible is primary here, reversing v2 implicit OSHB-only sourcing.

**`morphology_code`:** **P** = OSHB OSIS `<w morph="...">` (ETCBC tag). **X** = STEPBible TSV morphology column (cross-check). Conflict resolution: prefer OSHB/ETCBC (ETCBC is the canonical morphology system); STEPBible-OSHB divergence logged in `annotation_flags: ["stepbible-morphology-divergence"]` for Verifier review.

**`binyan`:** Derived from `morphology_code` (extract stem letter from ETCBC tag); lexicon fallback via lemma match if `morphology_code` is null but a single-binyan lemma match exists in BDB/HALOT. STEPBible morphology cross-check applies first to `morphology_code`, indirectly to `binyan`.

**`root`:** OSHB/ETCBC root field if available; otherwise null. (STEPBible does not appear to carry a separate root column distinct from lemma; if it does, treat as cross-check.)

**`phrase_role`, `phrase_depth`, `clause_role`:** **P** = Macula Hebrew treebank; null where Macula coverage absent. Single source.

### Per-token cross_walk_references sourcing (v3 addition)

**`cross_walk_references.strong_number`:** **P** = STEPBible TSV (Strong's↔GK Hebrew table; authoritative source). **X** = OSHB embedded `<w lemma="strong:H####">` if present. Conflict resolution: STEPBible wins; OSHB used as backup only if STEPBible has no entry for this token. Format enforcement: always `H` + zero-padded 4-digit (e.g., `H0001`, `H0430`, `H8674`).

**`cross_walk_references.gk_number`:** **P** = STEPBible TSV Strong's↔GK Hebrew table. Format: `H####` (e.g., `H1`, `H430`). Cross-validation: KM `strongs` field (98.5% coverage) can verify the Strong's↔GK mapping; KM disagreements are logged in `annotation_flags: ["stepbible-km-gk-divergence"]` for Verifier review but STEPBible wins.

**Population scope:** `cross_walk_references` is populated on every token where STEPBible has data. Tokens not covered by STEPBible have `cross_walk_references: null` or both nested fields null. Per AC-13 (§ G), v1 target is ≥85% of Hebrew Bible tokens having at least one cross-walk reference populated.

### Per-token interlinear gloss sourcing (Correction 3)

`interlinear_glosses` is populated by joining each interlinear source on the token's verse + token_index:

| source | match key | gloss field | language | source string |
|---|---|---|---|---|
| Accordance `.ainter` | verse-ref + per-token index against the CATSS parallel rows | English column from CATSS | `"en"` (and `"el"` for the LXX side, if Builder also extracts that column) | `"Accordance .ainter CATSS"` |
| Accordance `.agloss` | offset-driven lookup keyed by Hebrew lemma form | English/German gloss | `"en"` (and `"de"` for German) | `"Accordance .agloss"` |
| STEPBible interlinear TSV | verse + token-index | English column | `"en"` | `"STEPBible interlinear"` |

Each source contributes ZERO OR ONE entry per token (one if match found, none if no coverage). The list is the union across sources. No alignment computation: the source data IS aligned per-token by construction.

**v1 best-effort:** If the `.agloss` or `.ainter` offset-driven parsers are not implemented in r8, those sources contribute zero entries; `interlinear_glosses` may have only STEPBible entries. This is a v1 limitation flagged in `manifest.json`. Builder may implement parsers if time permits within the r8 envelope; if not, follow-on parser-implementation rounds backfill.

### Per-token lexicon-link sourcing (Correction 1; linguistic match)

`lexicon_links` is computed at corpus-build time via linguistic-match logic. NO Strong's-based join.

#### Match algorithm (pseudo-SQL; Builder implements)

```
FOR each token t WITH lemma, morphology_code, binyan FROM the corpus:
  FOR each lexicon L IN [BDB, HALOT, KM]:
    candidates = SELECT entries FROM L WHERE headword_consonantal == t.lemma
    
    IF len(candidates) == 0:
      // No lexicon match for this lemma; do nothing
      continue
    
    IF len(candidates) == 1:
      entry = candidates[0]
      // Record without further morphology/binyan filter:
      // single homograph means lexicon does not need disambiguation
      lexicon_links.append({
        lexicon: L.name,
        entry_ref: entry.primary_key,
        match_evidence: f"lemma={t.lemma}; single-homograph match in {L.name}; "
                        f"morphology={t.morphology_code or 'null'}; "
                        f"binyan={t.binyan or 'null'}; "
                        f"entry.grammar_normalized={entry.grammar_normalized}"
      })
      continue
    
    // Multiple candidates (homograph case)
    IF t.binyan AND t is a verb (morphology_code starts with 'HV'):
      // Filter by binyan compatibility
      filtered = [c for c in candidates 
                  if c.grammar_normalized == 'verb' 
                  and t.binyan in (c.binyanim.keys() if c.binyanim else [])]
      IF len(filtered) >= 1:
        FOR each entry IN filtered:
          lexicon_links.append({
            lexicon: L.name,
            entry_ref: entry.primary_key,
            match_evidence: f"lemma={t.lemma}; binyan={t.binyan} matched against entry.binyanim; "
                            f"homograph_index={entry.homograph_index}"
          })
        continue
      // binyan filter found nothing; fall through to fallback
    
    IF t.morphology_code:
      // Filter by POS compatibility (verb / noun / adj / adv / particle)
      pos_inferred = morphology_to_pos(t.morphology_code)  // utility; e.g., 'HV' -> 'verb', 'HN' -> 'noun'
      filtered = [c for c in candidates 
                  if c.grammar_normalized == pos_inferred]
      IF len(filtered) == 1:
        entry = filtered[0]
        lexicon_links.append({
          lexicon: L.name,
          entry_ref: entry.primary_key,
          match_evidence: f"lemma={t.lemma}; POS={pos_inferred} from morphology disambiguated {len(candidates)} homographs; "
                          f"homograph_index={entry.homograph_index}"
        })
        continue
      IF len(filtered) > 1:
        // Genuine ambiguity; record all matches and flag
        FOR each entry IN filtered:
          lexicon_links.append({
            lexicon: L.name,
            entry_ref: entry.primary_key,
            match_evidence: f"lemma={t.lemma}; ambiguous homograph; POS={pos_inferred}; "
                            f"homograph_index={entry.homograph_index}; flagged for v2 sense-disambiguation"
          })
        annotation_flags.append(f"{L.name.lower()}-multiple-match")
        continue
    
    // Final fallback: no morphology, no binyan; record all homograph candidates with explicit ambiguity
    FOR each entry IN candidates:
      lexicon_links.append({
        lexicon: L.name,
        entry_ref: entry.primary_key,
        match_evidence: f"lemma={t.lemma}; ambiguous homograph; no morphology/binyan disambiguation available; "
                        f"homograph_index={entry.homograph_index}; flagged for v2 sense-disambiguation"
      })
    annotation_flags.append(f"{L.name.lower()}-multiple-match")
```

#### Homograph disambiguation rules summary

1. **Single match:** record without filter; the lexicon already disambiguates.
2. **Multiple matches + verb token + binyan known:** filter by `binyan in entry.binyanim.keys()`. Surviving candidates recorded.
3. **Multiple matches + morphology_code known + POS inferable:** filter by `entry.grammar_normalized == pos_inferred`. If exactly one survives, record it; if multiple, record all and flag.
4. **Final fallback (multiple, no disambiguation):** record all candidates and flag `<lexicon>-multiple-match` in `annotation_flags`. v2 sense-disambiguation curation pass picks the right one per context.

#### Why this matches the user's design intent

The user's correction: "We are working on individual token instances, were as the Strong's concordance just does a blanket meaning for the word no matter the context incorrectly."

The match algorithm above respects context: same lemma in two positions with different binyan / different POS produces different `lexicon_links`. The match evidence is human-auditable. The denormalized `lexicon_links` field is a precomputed convenience; the underlying truth is "what lexicon entry/entries the token's linguistic profile matches at this position." Strong's was rejected because it would have collapsed homographs into a single number without context-sensitive disambiguation.

#### Why BDB and HALOT 0/9,433 / 0/6,631 strongs coverage no longer matters

The v1 spec worried that strongs=0 in BDB/HALOT broke the join. Per Correction 1, the join was wrong-headed regardless: lexicon match should always have been linguistic, not via Strong's. The fixtures' `headword_consonantal` (9,409/9,433 BDB, 6,619/6,631 HALOT) is the right join target. KM gets the same treatment; KM `gk_number` is now used only for cross-validation in `match_evidence`, not as a primary join key.

### Per-passage translation sourcing (Correction 2)

**Berean Standard Bible:** Per-pericope rows assembled by:
1. For each pericope in `passages.jsonl`, collect all verse refs in `[verse_ref_start, verse_ref_end]`
2. Look up each verse in `data/fixtures/genesis_full_berean.json`
3. Concatenate verse English strings with a space separator
4. Emit a row: `{passage_id, target_language: "en", source_attribution: "Berean Standard Bible 2023", text: <concatenated>, license_status: "public_domain", source_provenance: "data/fixtures/genesis_full_berean.json"}`

**Gold catalog:** Per-entry rows assembled by:
1. For each entry in `gold/catalog.json["entries"]`, locate the enclosing pericope by mapping `ref_start` to the pericope whose verse range contains it
2. If the entry spans multiple pericopes, Builder picks one of two approaches (documented in commit message): (a) split into one row per pericope with `notes: "gold entry spans multiple pericopes"`, OR (b) place on the smallest enclosing pericope with `notes` flagging the verse-range mismatch
3. Emit row: `{passage_id, target_language: "en", source_attribution: "User gold catalog 2026-04-25", text: <entry.translation>, license_status: "gold_user_owned", translation_date: "2026-04-25", source_provenance: "gold/catalog.json"}`

**Future translations (Luther, KJV, Vulgate, etc.):** Builder need not implement these in r8. Schema accommodates future ingest; v1 ships with Berean + gold only.

### Per-passage metadata sourcing

| field | v1 mechanical default | aspirational source |
|---|---|---|
| `canonical_section` | Derive from book (Gen–Deut = Torah; Josh–2Kgs = Former Prophets; Isa–Mal = Latter Prophets; Ps–Chr = Writings) | Deterministic |
| `author_tradition` | `["traditional"]` for all v1 passages | ABD intros; Driver/Skinner |
| `genre` | Mechanical heuristic (creation-account, genealogy, prose narrative, poetry, legal) | Editorial review |
| `subgenre` | Null in v1 except obvious cases (genealogy, creation-account, lament) | Editorial pass |
| `era_estimate` | Null in v1 | ABD, scholarly tables |
| `language_register` | narrative for prose; poetic for Psalms etc.; legal-formulaic for Lev/Deut code | Editorial |
| `audience` | Null in v1 | Editorial |
| `literary_devices` | Empty list `[]` in v1 | Rubric annotation pass |
| `manuscript_witnesses` | `["MT"]` for all Hebrew Bible passages | Supplement with `["LXX"]` etc. |
| `cross_canon_links` | Null in v1 | Separate annotation pass |

### Manifest file

`data/corpus/hebrew/manifest.json` records pinned source versions:

```json
{
  "generated_at": "<ISO-8601 timestamp>",
  "corpus_version": "1",
  "oshb_commit_sha": "<sha>",
  "macula_release": "<tag>",
  "stepbible_tsv_commit_sha": "<sha>",
  "lex_bdb_fixture_date": "<date>",
  "lex_halot_fixture_date": "<date>",
  "lex_km_fixture_date": "<date>",
  "agloss_parser_status": "<implemented | not-implemented>",
  "ainter_parser_status": "<implemented | not-implemented>",
  "scope": "Genesis",
  "token_count": "<N>",
  "passage_count": "<N>",
  "translation_count": "<N>"
}
```

---

## G. Acceptance criteria (runnable Python)

All scripts read from `data/corpus/hebrew/` and `gold/`. Each script prints `PASS` or `FAIL`. Runs after Builder completes corpus assembly, before PR opens.

### AC-1: Token count plausibility

```python
#!/usr/bin/env python3
import json, sys
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
gen_tokens = [t for t in tokens if t['token_id'].startswith('Gen.')]
print(f"Total tokens: {len(tokens)}")
print(f"Genesis tokens: {len(gen_tokens)}")
low, high = 26_000, 38_000
if low <= len(gen_tokens) <= high:
    print(f"PASS: Genesis token count {len(gen_tokens)} within [{low}, {high}]")
else:
    print(f"FAIL: Genesis token count {len(gen_tokens)} outside [{low}, {high}]")
    sys.exit(1)
```

### AC-2: Fingerprint global uniqueness

```python
#!/usr/bin/env python3
import json, sys
from collections import Counter
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
fps = [t['fingerprint'] for t in tokens]
dup_fps = [fp for fp, cnt in Counter(fps).items() if cnt > 1]
print(f"Total tokens: {len(tokens)}, unique fingerprints: {len(set(fps))}")
if not dup_fps:
    print("PASS: all fingerprints globally unique")
else:
    print(f"FAIL: {len(dup_fps)} duplicate fingerprints")
    for fp in dup_fps[:5]:
        dups = [t['token_id'] for t in tokens if t['fingerprint'] == fp]
        print(f"  fingerprint {fp}: {dups}")
    sys.exit(1)
```

### AC-3: Gold-catalog verse coverage (Genesis)

```python
#!/usr/bin/env python3
import json, sys
tokens_by_verse = set()
for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8'):
    t = json.loads(l)
    parts = t['token_id'].rsplit('.', 1)
    tokens_by_verse.add(parts[0])

catalog = json.load(open('gold/catalog.json', encoding='utf-8'))
missing = []
for entry in catalog['entries']:
    rs = entry.get('ref_start', '')
    if not rs.startswith('Gen.'):
        continue
    if rs not in tokens_by_verse:
        missing.append(rs)

print(f"Gold Genesis entries: {len([e for e in catalog['entries'] if e['ref_start'].startswith('Gen.')])}")
print(f"Missing from corpus: {len(missing)}")
if not missing:
    print("PASS: all gold Genesis verses covered")
else:
    print(f"FAIL: {len(missing)} missing: {missing[:10]}")
    sys.exit(1)
```

### AC-4: Lexicon-link coverage for Hebrew verbs (linguistic match; revised per Correction 1)

```python
#!/usr/bin/env python3
# Verb tokens with at least one lexicon_links entry. Replaces v1 AC-4
# which used Strong's-based halot_key/bdb_key/km_number fields.
import json, sys
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
verbs = [t for t in tokens if (t.get('morphology_code') or '').startswith('HV')]
linked = [t for t in verbs if t.get('lexicon_links')]
pct = 100.0 * len(linked) / max(len(verbs), 1)
print(f"Verb tokens: {len(verbs)}, with >=1 lexicon_link: {len(linked)} ({pct:.1f}%)")
if pct >= 70.0:
    print(f"PASS: verb lexicon-link coverage {pct:.1f}% >= 70%")
else:
    print(f"FAIL: verb lexicon-link coverage {pct:.1f}% < 70%")
    sys.exit(1)
```

### AC-5: Passage FK integrity

```python
#!/usr/bin/env python3
import json, sys
passages = {json.loads(l)['passage_id'] for l in open('data/corpus/hebrew/passages.jsonl', encoding='utf-8')}
broken = []
for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8'):
    t = json.loads(l)
    if t['passage_id'] not in passages:
        broken.append(t['token_id'])

print(f"Passage IDs in passages.jsonl: {len(passages)}")
print(f"Token FK violations: {len(broken)}")
if not broken:
    print("PASS: all passage FKs resolve")
else:
    print(f"FAIL: {len(broken)} unresolvable; first 5: {broken[:5]}")
    sys.exit(1)
```

### AC-6: Named-token structural validation (Gen.1.1.0 = bereshit; revised fingerprint per Correction 1)

```python
#!/usr/bin/env python3
import json, sys, hashlib

def compute_fingerprint(token: dict) -> str:
    FIELDS = sorted(["token_id", "surface", "lemma", "lemma_vocalized",
                     "morphology_code", "binyan"])
    parts = [f"{f}={token.get(f) or ''}" for f in FIELDS]
    payload = "\x00".join(parts).encode("utf-8")
    return hashlib.blake2b(payload, digest_size=16).hexdigest()

tokens = {json.loads(l)['token_id']: json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')}
t = tokens.get('Gen.1.1.0')
if not t:
    print("FAIL: Gen.1.1.0 not found")
    sys.exit(1)

failures = []
if not t.get('lemma'): failures.append("lemma null")
if not t.get('surface'): failures.append("surface null")
if not t.get('passage_id'): failures.append("passage_id null")
if not t.get('fingerprint') or len(t['fingerprint']) != 32:
    failures.append(f"fingerprint malformed: {t.get('fingerprint')!r}")

expected = compute_fingerprint(t)
if t.get('fingerprint') != expected:
    failures.append(f"fingerprint mismatch: stored={t['fingerprint']} computed={expected}")

print(f"Gen.1.1.0: lemma={t.get('lemma')}, lemma_vocalized={t.get('lemma_vocalized')}, "
      f"morph={t.get('morphology_code')}, binyan={t.get('binyan')}, passage_id={t.get('passage_id')}")
print(f"  fingerprint: {t.get('fingerprint')}")
print(f"  lexicon_links count: {len(t.get('lexicon_links') or [])}")
print(f"  interlinear_glosses count: {len(t.get('interlinear_glosses') or [])}")

if not failures:
    print("PASS: Gen.1.1.0 structural quality OK")
else:
    print(f"FAIL: {len(failures)} issues:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
```

### AC-7: Required field completeness

```python
#!/usr/bin/env python3
import json, sys
REQUIRED = ['token_id', 'fingerprint', 'passage_id', 'surface', 'lemma', 'source_provenance']
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
violations = {}
for field in REQUIRED:
    missing = [t['token_id'] for t in tokens if not t.get(field)]
    if missing:
        violations[field] = missing
print(f"Total tokens: {len(tokens)}")
if not violations:
    print("PASS: all required fields present")
else:
    for field, tids in violations.items():
        print(f"FAIL: '{field}' missing on {len(tids)} tokens; first 3: {tids[:3]}")
    sys.exit(1)
```

### AC-8: Fingerprint determinism (revised field set)

```python
#!/usr/bin/env python3
import json, sys, hashlib

def compute_fingerprint(token: dict) -> str:
    FIELDS = sorted(["token_id", "surface", "lemma", "lemma_vocalized",
                     "morphology_code", "binyan"])
    parts = [f"{f}={token.get(f) or ''}" for f in FIELDS]
    payload = "\x00".join(parts).encode("utf-8")
    return hashlib.blake2b(payload, digest_size=16).hexdigest()

tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
mismatches = []
for t in tokens:
    expected = compute_fingerprint(t)
    if t.get('fingerprint') != expected:
        mismatches.append((t['token_id'], t.get('fingerprint'), expected))

print(f"Total tokens: {len(tokens)}")
if not mismatches:
    print("PASS: all fingerprints deterministically recompute")
else:
    print(f"FAIL: {len(mismatches)} mismatches")
    for tid, stored, computed in mismatches[:3]:
        print(f"  {tid}: stored={stored} computed={computed}")
    sys.exit(1)
```

### AC-9: Passage metadata completeness

```python
#!/usr/bin/env python3
import json, sys
passages = [json.loads(l) for l in open('data/corpus/hebrew/passages.jsonl', encoding='utf-8')]
REQUIRED = ['passage_id', 'book', 'chapter_start', 'verse_start',
            'chapter_end', 'verse_end', 'canonical_section',
            'genre', 'language_register', 'manuscript_witnesses',
            'pericope_source', 'source_provenance', 'token_count']
failures = []
for p in passages:
    for field in REQUIRED:
        if p.get(field) is None:
            failures.append(f"passage {p.get('passage_id')} missing {field}")

print(f"Total passages: {len(passages)}")
if not failures:
    print("PASS: all passage required fields present")
else:
    for f in failures[:10]:
        print(f"  FAIL: {f}")
    sys.exit(1)
```

### AC-10: Interlinear gloss coverage (NEW per Correction 3)

```python
#!/usr/bin/env python3
# Tokens with >=1 interlinear gloss from any source.
# Target: >=80% of Genesis tokens given .ainter / .agloss / STEPBible coverage.
# If parsers for .ainter / .agloss are not implemented in r8, this AC may be
# satisfied by STEPBible interlinear alone; manifest.json records parser status.
import json, sys
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
gen_tokens = [t for t in tokens if t['token_id'].startswith('Gen.')]
with_gloss = [t for t in gen_tokens if t.get('interlinear_glosses')]
pct = 100.0 * len(with_gloss) / max(len(gen_tokens), 1)
print(f"Genesis tokens: {len(gen_tokens)}, with >=1 interlinear gloss: {len(with_gloss)} ({pct:.1f}%)")
if pct >= 80.0:
    print(f"PASS: interlinear gloss coverage {pct:.1f}% >= 80%")
else:
    print(f"FAIL: interlinear gloss coverage {pct:.1f}% < 80%")
    print("  Note: if .agloss/.ainter parsers not implemented, AC may use STEPBible-only.")
    print("  Check manifest.json agloss_parser_status / ainter_parser_status.")
    sys.exit(1)
```

### AC-11: Verb binyan-compatible lexicon match (NEW per Correction 1)

```python
#!/usr/bin/env python3
# Verbs whose lexicon_links include at least one entry with binyan-compatible
# match_evidence. Validates the linguistic-match logic in § F is working
# rather than just doing blind lemma joins.
import json, sys
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
verbs = [t for t in tokens if (t.get('morphology_code') or '').startswith('HV') and t.get('binyan')]
binyan_matched = []
for t in verbs:
    links = t.get('lexicon_links') or []
    for link in links:
        if t['binyan'] in (link.get('match_evidence') or ''):
            binyan_matched.append(t['token_id'])
            break
pct = 100.0 * len(binyan_matched) / max(len(verbs), 1)
print(f"Verb tokens with binyan: {len(verbs)}, with binyan-compatible match: {len(binyan_matched)} ({pct:.1f}%)")
if pct >= 85.0:
    print(f"PASS: binyan-compatible match coverage {pct:.1f}% >= 85%")
else:
    print(f"FAIL: binyan-compatible match coverage {pct:.1f}% < 85%")
    sys.exit(1)
```

### AC-12: Translations table integrity (NEW per Correction 2)

```python
#!/usr/bin/env python3
# Every translations.jsonl row's passage_id resolves to passages.jsonl;
# every row has required fields; license_status is in enum.
import json, sys
passages = {json.loads(l)['passage_id'] for l in open('data/corpus/hebrew/passages.jsonl', encoding='utf-8')}
ALLOWED_LICENSES = {'public_domain', 'cc_by', 'proprietary_with_access', 'gold_user_owned'}
REQUIRED = ['passage_id', 'target_language', 'source_attribution', 'text', 'license_status', 'source_provenance']
rows = [json.loads(l) for l in open('data/corpus/hebrew/translations.jsonl', encoding='utf-8')]
broken_fk = []
missing_field = []
bad_license = []
for r in rows:
    if r['passage_id'] not in passages:
        broken_fk.append(r['passage_id'])
    for f in REQUIRED:
        if not r.get(f):
            missing_field.append((r.get('passage_id'), f))
    if r.get('license_status') not in ALLOWED_LICENSES:
        bad_license.append((r.get('passage_id'), r.get('license_status')))

print(f"Translations rows: {len(rows)}")
print(f"  passage_id FK violations: {len(broken_fk)}")
print(f"  missing required fields: {len(missing_field)}")
print(f"  bad license_status: {len(bad_license)}")

# Confirm at least Berean + gold are present for Genesis pericopes covered by gold
berean_rows = [r for r in rows if 'Berean' in (r.get('source_attribution') or '')]
gold_rows = [r for r in rows if 'gold catalog' in (r.get('source_attribution') or '')]
print(f"  Berean rows: {len(berean_rows)}, gold rows: {len(gold_rows)}")

if not broken_fk and not missing_field and not bad_license and len(berean_rows) > 0 and len(gold_rows) > 0:
    print("PASS: translations.jsonl integrity OK")
else:
    sys.exit(1)
```

### AC-13: Cross-walk reference coverage (NEW per v3 Q3=C Effect 1)

```python
#!/usr/bin/env python3
# Cross-walk references (Strong's / GK) are populated where STEPBible TSV
# has data for the token. Target: >=85% of Hebrew Bible tokens with at
# least one of strong_number or gk_number populated.
# This validates Correction 1 (preserve concordance numbers as non-identity
# reference data) AND Correction 4 (STEPBible TSV restored as primary
# linguistic data source for cross_walk_references).
import json, sys
tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
total = len(tokens)
with_xref = 0
strong_only = 0
gk_only = 0
both = 0
for t in tokens:
    xref = t.get('cross_walk_references') or {}
    s = xref.get('strong_number')
    g = xref.get('gk_number')
    if s and g:
        both += 1
        with_xref += 1
    elif s:
        strong_only += 1
        with_xref += 1
    elif g:
        gk_only += 1
        with_xref += 1

pct = 100.0 * with_xref / max(total, 1)
print(f"Total tokens: {total}")
print(f"  with cross_walk_references populated: {with_xref} ({pct:.1f}%)")
print(f"  both strong+gk: {both}")
print(f"  strong_number only: {strong_only}")
print(f"  gk_number only: {gk_only}")
if pct >= 85.0:
    print(f"PASS: cross-walk coverage {pct:.1f}% >= 85%")
else:
    print(f"FAIL: cross-walk coverage {pct:.1f}% < 85%")
    print("  Note: ensure STEPBible TSV is fetched and joined per § F sourcing pipeline.")
    sys.exit(1)
```

### AC-14: Cross-walk references excluded from fingerprint (NEW per v3)

```python
#!/usr/bin/env python3
# Verify that fingerprint does NOT change when cross_walk_references is altered.
# This tests the explicit Section D exclusion: STEPBible Strong's↔GK updates
# must NOT invalidate fingerprints. Sample-based test: take 20 tokens, mutate
# their cross_walk_references in memory, recompute fingerprint, confirm equality.
import json, sys, hashlib, copy

def compute_fingerprint(token: dict) -> str:
    FIELDS = sorted(["token_id", "surface", "lemma", "lemma_vocalized",
                     "morphology_code", "binyan"])
    parts = [f"{f}={token.get(f) or ''}" for f in FIELDS]
    payload = "\x00".join(parts).encode("utf-8")
    return hashlib.blake2b(payload, digest_size=16).hexdigest()

tokens = [json.loads(l) for l in open('data/corpus/hebrew/v1.jsonl', encoding='utf-8')]
sample = tokens[:20] if len(tokens) >= 20 else tokens
mismatches = []
for t in sample:
    fp_original = compute_fingerprint(t)
    t_mutated = copy.deepcopy(t)
    # Mutate cross_walk_references arbitrarily
    t_mutated['cross_walk_references'] = {'strong_number': 'H9999', 'gk_number': 'H9999'}
    fp_mutated = compute_fingerprint(t_mutated)
    if fp_original != fp_mutated:
        mismatches.append((t['token_id'], fp_original, fp_mutated))

print(f"Sampled tokens: {len(sample)}")
if not mismatches:
    print("PASS: cross_walk_references mutation does not affect fingerprint")
else:
    print(f"FAIL: {len(mismatches)} fingerprints changed under cross_walk_references mutation")
    for tid, orig, mut in mismatches[:3]:
        print(f"  {tid}: original={orig} mutated={mut}")
    print("  This indicates a bug — cross_walk_references must be excluded from fingerprint inputs per § D.")
    sys.exit(1)
```

---

## H. Alternatives considered

### H.1 — Flat sentence-pair table (rejected)

The existing approach: `genesis_full_hebrew.json` provides verse-level Hebrew strings; `genesis_full_berean.json` provides English; `prepare_translate.py` joins them as flat pairs. Sufficient for chrF baseline but eliminates per-token identity, morphology, phrase role, lexicon link, genre context. The model trained on flat pairs cannot distinguish Qal from Niphal, narrative from poetry, wayyiqtol chain from waw-disjunctive. The rubric P1–P15 encode exactly the distinctions flat pairs erase. Rejected per `feedback_corpus_dimensions.md` and the project thesis.

### H.2 — Per-token without passage table (rejected)

Token-level data alone provides only the linguistic axis. Without passage metadata, the model cannot learn that the same morphological form (Niphal participle) functions differently in narrative, legal, and prophetic contexts; cannot represent literary devices spanning multiple tokens; cannot encode manuscript witnesses (passage-level information). `feedback_corpus_dimensions.md` identifies four dimensions (positional, linguistic, authorial, historical) as irreducible; authorial and historical live at passage grain. Rejected.

### H.3 — Document database (MongoDB / SQLite / DuckDB) as canonical storage (rejected)

JSONL is grep-able, diff-able, single-loop loadable, regenerable from scratch, compatible with Hugging Face `datasets`, line-level git diffable. If query performance becomes a bottleneck, JSONL loads into DuckDB or SQLite via a single-line read without changing canonical format. Rejected as canonical storage.

### H.4 — Single combined token+passage table (rejected)

~30 passage fields × ~470K tokens = ~14M redundant field instances. Every passage-level annotation change requires rewriting all tokens in that pericope. The two-table FK design is the standard normalized approach. Rejected per `feedback_corpus_dimensions.md`.

### H.5 — Source-ID-based lexicon join (Strong's / GK number) (rejected as join key per Correction 1; PRESERVED as cross-walk per v3 Q3=C Effect 1)

**Scope of the rejection (refined in v3):** Strong's/GK numbers are PRESERVED in `cross_walk_references` (non-identity, for external interop). They are REJECTED as the join key for lexicon-entry matching, which uses linguistic-match logic per § F. The v3 spec has both: cross-walk preservation AND linguistic-match joins. There is no contradiction — the preservation is for downstream consumers keyed by Strong's; the linguistic-match join is the corpus-internal lexicon-link computation.

**Rejection rationale (Strong's/GK as join key):**
1. **Linguistic-correctness:** Strong's number is a concordance index — one number maps to one "blanket meaning" for a word regardless of context. Two grammatically different uses of the same lemma (different binyan, different morphology, different sense-in-context) collapse to the same Strong's number. This is precisely the flattening the project thesis is designed to undo. The user's verbatim quote: "the Strong's concordance just does a blanket meaning for the word no matter the context incorrectly."
2. **Mechanical-correctness:** Even if Strong's were the right shape for a join key, BDB has 0/9,433 strongs populated and HALOT has 0/6,631; Strong's-based join is mechanically broken for the two largest Hebrew lexicons. KM has 98.5% strongs coverage but per (1) Strong's is not the right shape regardless.
3. **Fingerprint stability:** Including Strong's in the fingerprint would mean fingerprints flip whenever STEPBible TSV updates a Strong's↔GK mapping. Since Strong's is not linguistic identity, this would be spurious fingerprint churn. The v3 cross_walk_references field is explicitly excluded from fingerprint inputs (§ D) precisely to preserve this stability property — STEPBible Strong's updates are corpus-data updates, not curation-invalidation events.

**Preservation rationale (Strong's/GK as cross-walk reference data, v3):**
The user clarified on Q3=C that concordance numbers should be retained for external-resource interop. Many study Bibles, older commentaries, and third-party annotation tools are keyed by Strong's. Discarding the numbers entirely would prevent the corpus from cross-referencing those resources. Preserving them as `cross_walk_references` (non-identity, non-join, non-fingerprint) lets downstream consumers do Strong's-keyed lookups without compromising corpus design integrity. The numbers are descriptive metadata, not structural commitments.

**The correct architecture (v3):** lemma + morphology + binyan compatibility match against `headword_consonantal` for `lexicon_links` (§ F). Strong's and GK numbers stored on each token in `cross_walk_references` for external interop. `lexicon_links[].match_evidence` strings may mention Strong's/GK as descriptive evidence but the join itself is linguistic.

### H.6 — Per-chapter passage grain (rejected)

Chapter boundaries are 13th-century CE divisions with no authorial significance. Genesis 1 conflates the Elohim creation account (1.1–2.3) and the second account's transition (2.4a). Per-chapter erases distinctions directly relevant to the project thesis. Per-pericope chosen instead (§ E).

### H.7 — Per-verse passage grain with pericope grouping as metadata (rejected)

Hybrid: passage_id per-verse, with `pericope_group` field. Preserves 1:1 with `Gen.1.1` keys but means passage-metadata curation burden = 1,532 verses (Genesis alone) instead of ~200 pericopes. `genre`/`author_tradition` would be identical for every verse in a pericope = pure redundancy. Per-pericope with `verse_ref_start`/`verse_ref_end` provides equivalent verse-level lookup. Rejected.

### H.8 — Per-token translation strings (rejected per Correction 2)

The v1 spec briefly considered per-token translation glosses as a single field. Per Correction 2, this conflates two distinct artifacts:

(a) Per-token interlinear glosses are correctly per-token; the source data IS aligned per-token (.ainter, .agloss, STEPBible). This is `interlinear_glosses` field (Correction 3, kept).

(b) Per-passage prose translations (BSB, Luther, gold catalog, KJV) reorder words across the passage; "the words or phrasing are moved around" in the user's verbatim words. Storing target-language tokens against source tokens would require alignment work that we explicitly defer to v2. The right v1 design is per-passage prose, with token-to-prose alignment as a separate v2 artifact.

The current spec separates (a) into per-token and (b) into per-passage `translations.jsonl`. Per-token translation strings (treating prose translation as if it aligned per-token) is rejected.

### H.9 — Sense-disambiguated lexicon links in v1 (deferred not rejected)

A richer `lexicon_links` would carry not just the lexicon entry but also the specific sense within that entry that the token instance instantiates (e.g., BDB entry for ברא with senses I, II, III; this token at this position is sense II). Sense-aware joins are richer than concordance-flat (the user's intent in Correction 1 implies this is the eventual target). However, sense disambiguation requires per-token contextual judgment — exactly the curation work that the project's two-tier seam (`feedback_lexicon_corpus_design.md`) places in a separate annotation pass.

**Decision for v1:** `lexicon_links` carries lexicon + entry_ref only; sense disambiguation deferred to v2 curation tooling (§ J item 11). The match_evidence string captures the linguistic basis for the entry-level match; sense-level annotation is a separate field family added later.

---

## I. Migration / backfill path

### Existing fixtures unchanged

`data/fixtures/` remains as-is. `prepare_translate.py` and `score_translate.py` continue to read flat fixtures. Plan #6 outputs go to `data/corpus/hebrew/` — new directory, no conflict.

### Key namespace alignment

`genesis_full_hebrew.json` uses `Gen.1.1` verse keys. Plan #6 `token_id = Gen.1.1.0` etc. Verse ref recoverable via `token_id.rsplit('.', 1)[0]`. Gold catalog `Psalm.` entries normalized to `Ps.` by Builder canonicalization.

### Future `prepare_translate.py` revision path

Current pipeline reads flat verse strings. v2 will read `data/corpus/hebrew/v1.jsonl` and produce enriched BPE sequences with structural special tokens (per Phase 1 design). Out of scope for r8.

### v1 scope and v2 extension

**v1 scope: Genesis.** ~30K tokens; full pipeline validation possible; 67/95 gold entries are Genesis. Bugs at 30K scale are cheap.

**v2 extension to full Hebrew Bible:** Mechanical (`--books` parameter; same OSHB/Macula/STEPBible logic; AC-1 target updates). No schema changes required.

**Corpus version numbering:** `v1` is schema version. Source versions in `manifest.json`. Schema changes → `v2.jsonl`.

### Translations table extension path

v1 ships with Berean + gold. Adding KJV / Luther / Vulgate / NIV (proprietary_with_access) is mechanical: ingest source, produce `translations.jsonl` rows with appropriate `source_attribution` and `license_status`. No schema change. Future alignment artifacts populate `alignment_artifact_ref` (null in v1).

### Interlinear glosses extension path

v1 best-effort: STEPBible interlinear ingested if TSV columns present; `.agloss` / `.ainter` parsers as time permits in r8 envelope. v2 backfill: complete `.agloss` / `.ainter` parsers; re-run join; `interlinear_glosses` lists grow without schema change.

---

## J. Out-of-scope (explicit)

Not deliverables for Plan #6 / Builder r8:

1. **Training pipeline rewrite** — `prepare_translate.py` / `train_translate.py` unchanged. r10+ work.

2. **Greek track corpus** — Schema parity documented but no Greek assembly until Hebrew model trained.

3. **Curation tooling** — Manual binyan annotation, gold-token alignment, curated literary_devices: separate tooling rounds.

4. **Cross-canon link generation** — `cross_canon_links` field exists but null in v1; auto-generation is a separate annotation pass.

5. **Accordance `.atext` parser changes** — `.atext` (`MT-ETCBC-A`) requires new OakTree reader. Plan #6 uses OSHB instead.

6. **Accordance `.agloss` / `.ainter` parsers** — `interlinear_glosses` from these sources is best-effort in r8; null entries acceptable; backfill in later round.

7. **KM binyan audit** — KM iter-4 baseline acceptable as-is. Builder uses KM as-is.

8. **Disputed authorship curation** — `author_tradition` defaults `["traditional"]`. Source-critical positions require scholarly annotation, deferred.

9. **Anchor Bible Dictionary licensing review** — Separate decision. Builder uses mechanical defaults for `era_estimate`, `author_tradition`.

10. **Multi-witness token rows for variant readings** — v1 = MT only. DSS/LXX divergence flagged at passage level via `manuscript_witnesses`. Variant-as-row is v3+ schema concern.

11. **Sense-disambiguation in `lexicon_links`** (NEW per Correction 1 + H.9) — `lexicon_links` carries entry-level matches in v1; per-sense disambiguation (which BDB sub-sense within an entry the token instantiates) is a v2 curation artifact. Match_evidence strings capture the entry-level rationale; sense-level rationale added later.

12. **Token-to-prose alignment between source tokens and per-passage translations** (NEW per Correction 2) — v1 stores prose translations as plain text per passage; alignment to source tokens left for the model's attention to learn implicitly OR for a separate v2 explicit gold-alignment artifact at `data/corpus/hebrew/alignments/`. The `alignment_artifact_ref` field in `translations.jsonl` is reserved for v2 use; v1 leaves it null.

13. **Additional translation sources (Luther, KJV, Vulgate, NIV, etc.)** — Schema accommodates; v1 ships with Berean + gold catalog only. Future ingest is mechanical, no schema change.

### Explicitly NOT out-of-scope (clarification per v3 Q3=C)

For the avoidance of doubt, the following are explicitly IN scope for v1 and Builder r8:

- **`cross_walk_references` (Strong's, GK)** — Per Q3=C Effect 1: preserved on every token where STEPBible has data. Target ≥85% Hebrew Bible coverage (AC-13). NOT a join key, NOT in fingerprint, NOT identity — but populated and stored. Earlier v2 spec language that suggested concordance numbers were "removed entirely" is superseded; v3 has them as cross-walk reference data.
- **STEPBible TSV as primary linguistic data source** — Per Q3=C Effect 2: STEPBible feeds `lemma_vocalized` (primary), `cross_walk_references` (primary), `paragraph_marker_post` (primary), `interlinear_glosses` (one of several primary sources), AND cross-checks `lemma` and `morphology_code` against OSHB. Earlier v2 demotion to "paragraph-marker + interlinear-gloss only" is superseded.

---

## Appendix: Schema summary

### Output artifact locations

| artifact | path | format | rows in v1 |
|---|---|---|---|
| Token corpus | `data/corpus/hebrew/v1.jsonl` | NDJSON, 1 token per line | ~30K (Genesis) |
| Passage metadata | `data/corpus/hebrew/passages.jsonl` | NDJSON, 1 passage per line | ~14–25 (Genesis pericopes per § E table; Macula override may shift) |
| Translations | `data/corpus/hebrew/translations.jsonl` | NDJSON, 1 (passage, lang, source) row per line | ~14 Berean + ~67 gold-catalog rows for Genesis = ~80 rows |
| Manifest | `data/corpus/hebrew/manifest.json` | JSON, single object | 1 |

### Greek track schema parity note

When Greek track lights up:
- `binyan` field absent (or repurposed for Greek voice/mood — design decision)
- `lexicon_links[].lexicon` values become `BDAG`, `Thayer`, `LSJ`
- Linguistic-match logic same: lemma + morphology compatibility against headword
- `morphology_code` uses Robinson-Friberg or equivalent Greek tagging
- `interlinear_glosses` continues to work; sources include `.ainter` LXX-side, NA28 reverse-interlinears
- `translations.jsonl` extends naturally: `target_language` accepts any ISO 639-1 code; `source_attribution` accepts any Greek-source translation

The unified `token_id` namespace (`Matt.1.1.0`, `Gen.1.1.0`) requires no modification.

### Cross-cutting design principles (recap)

1. **Identity is linguistic, not source-derived** (Correction 1) — tokens are positions × surface × lemma × vocalization × morphology × binyan. Concordance numbers are metadata, not identity.
2. **Cross-walk metadata is preserved, not removed** (v3 Q3=C Effect 1) — Strong's/GK live in `cross_walk_references` for external interop; not identity, not join, not fingerprint, but stored on every token where STEPBible has data.
3. **Different artifacts go in different tables** (Correction 2) — per-token features stay per-token; passage-level prose stays per-passage; alignment is a separate concern.
4. **Source data structure dictates table grain** (Correction 3) — interlinear glosses are per-token because the source IS per-token; translations are per-passage because translators reorder, and per-token attribution would require alignment work we defer.
5. **STEPBible TSV is a normalized linguistic data source** (v3 Q3=C Effect 2) — primary for `lemma_vocalized`, `cross_walk_references`, `paragraph_marker_post`; cross-check for `lemma` and `morphology_code`; one of several primary sources for `interlinear_glosses`. Not a join key (Correction 1 still stands); not an indexing scheme.
6. **Comprehensive extraction; iterative consumption** (`feedback_lexicon_corpus_design.md`) — the corpus carries everything available; training-time field selection picks what each experiment needs.
7. **Multiple competing scholarly positions, not picked winners** (`feedback_corpus_dimensions.md`) — list-typed fields for `author_tradition`, `era_estimate`, `literary_devices`, `cross_canon_links`.
8. **Curation binds to fingerprints, not lemmas** (`feedback_token_as_first_class_instance.md`) — per-token instance with stable fingerprint; annotation work survives extraction iterations as long as the linguistic-identity fields don't shift.
