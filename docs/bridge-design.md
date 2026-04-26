# Hebrew/Greek Translation Bridge — JSON Export Design

**Status:** Future-option reference. **Not** part of Phase 1.
**Date:** 2026-04-25 (status revised 2026-04-26)

> **Architectural note:** This document was originally written assuming `fellwork-api` would feed structured input to the autoresearch ML pipeline. That assumption has been revised — `fellwork-api` is downstream of this research, not upstream, and will be rebuilt later informed by Phase 1–5 outputs. The ML research uses public-domain structural sources directly (OSHB for morphology, Macula for phrase nodes). This bridge design is preserved as a reference for if/when a runtime integration becomes useful in a future phase. See `docs/superpowers/specs/2026-04-25-phase-1-design.md` for the active Phase 1 design.

---

## 1. Per-verse JSON schema

Each line of the JSONL file is one verse. Concrete shape (Gen 1:1):

```json
{
  "schema_version": 1,
  "generator_commit": "a4123c6",
  "generated_at": "2026-04-25T14:30:00Z",
  "verse_ref": "Gen.1.1",
  "book": "Gen",
  "chapter": 1,
  "verse": 1,
  "language": "hbo",
  "tokens": [
    {
      "position": 0,
      "surface": "בְּרֵאשִׁ֖ית",
      "lemma": "רֵאשִׁית",
      "strong_number": "H7225",
      "morphology_code": "Rd/Ncfsa",
      "morph": {
        "pos": "Noun",
        "state": "absolute",
        "gender": "feminine",
        "number": "singular",
        "has_conjunction": false,
        "has_article": false,
        "preposition": "in"
      },
      "rendering": {
        "english": "In the beginning",
        "prefix": "in",
        "subject": null,
        "core": "beginning",
        "suffix": null,
        "rare_stem_fallback": false,
        "pluralization_suppressed": false
      },
      "resolution": {
        "winner": "SenseDefinition",
        "chain": [
          { "level": 1, "name": "Override",        "available": false, "reason": "no_entry" },
          { "level": 2, "name": "WordStudy",        "available": false, "reason": "no_entry" },
          { "level": 3, "name": "Fingerprint",      "available": false, "reason": "no_entry" },
          { "level": 4, "name": "StemGloss",        "available": false, "reason": "non_content_pos" },
          { "level": 5, "name": "SenseDefinition",  "available": true,  "winner": true,
            "source": "bdb", "extracted": "beginning", "sense_index": 1 },
          { "level": 6, "name": "ShortGloss",       "available": true  },
          { "level": 7, "name": "TokenGloss",       "available": true  }
        ]
      },
      "applied_layers": [],
      "fingerprint": null,
      "sense": {
        "source": "bdb",
        "extracted_gloss": "beginning",
        "sense_index": 1,
        "binyan": null,
        "binyan_match": "index_1_fallback"
      }
    }
  ],
  "clauses": [
    {
      "clause_id": "uuid-of-phrase-node",
      "role_label": "Clause",
      "depth": 2,
      "indent": 0,
      "token_positions": [1, 2, 3, 4, 5, 6, 7],
      "first_token_morphology": "C/Vqw3ms"
    }
  ],
  "display_mode": "NARRATIVE",
  "verse_english": "In the beginning God created the heavens and the earth"
}
```

**Key fields by object:**

| Object | Fields | Source |
|--------|--------|--------|
| Root | `schema_version`, `generator_commit`, `generated_at`, `verse_ref`, `book`, `chapter`, `verse`, `language` | Provenance |
| `tokens[]` | `position` (0-indexed), `surface`, `lemma`, `strong_number`, `morphology_code` | `passage_tokens` |
| `tokens[].morph` | `pos`, `stem`, `conjugation`, `person`, `gender`, `number`, `state`, `has_article`, `has_conjunction`, `preposition`, `tense`, `voice`, `mood`, `case` | `resolved_tokens.morph` JSONB |
| `tokens[].rendering` | `english`, `prefix`, `subject`, `core`, `suffix`, `rare_stem_fallback`, `pluralization_suppressed` | `resolved_tokens.rendering` JSONB |
| `tokens[].resolution` | `winner`, `chain[7]` with per-level availability and rejection reasons | `resolved_tokens.resolution` JSONB |
| `tokens[].applied_layers` | Layer names that mutated this token: `["hiphil"]`, `["subject"]`, etc. | `VerseToken.applied_layers` from `fw-translate-layers` |
| `tokens[].fingerprint` | `rendering`, `base_confidence`, `adjusted_confidence`, `source` | `resolved_tokens.fingerprint` JSONB |
| `tokens[].sense` | `source`, `extracted_gloss`, `sense_index`, `binyan`, `binyan_match` | `resolved_tokens.sense` JSONB |
| `clauses[]` | `clause_id`, `role_label`, `depth`, `indent`, `token_positions`, `first_token_morphology` | `resolved_tokens` JOIN `phrase_structure_nodes` |
| `display_mode` | `NARRATIVE`, `POETRY`, `ARGUMENT`, `HYBRID`, `VISION` | `fw-phrase` genre detect |
| `verse_english` | Assembled sentence from tokens | Concatenated from token `english` fields |

The `position` field in `tokens[]` is 0-indexed (matching `passage_tokens.position`). The `token_positions` array in `clauses[]` is 1-indexed (matching `phrase_structure_nodes.token_positions`).

---

## 2. Where the export lives

**New binary crate: `crates/fw-export-ml`**

- A thin CLI binary that depends on `fw-translate-types`, `fw-phrase`, `sqlx`, `serde_json`, and `tokio`.
- Does NOT belong in `fw-translate` (different concern: export vs. translate).
- Add as workspace member: `"crates/fw-export-ml"` in root `Cargo.toml`.

**Output format: JSONL** — one JSON object per line, one file per run.

- Streaming-friendly: Python can iterate line by line without loading ~31k verses into RAM.
- Append-safe: can resume after crash at the last verse boundary.
- Single file is adequate for Hebrew OT (~23k verses). Greek NT can be a second file.

---

## 3. Build/run command

```bash
# From fellwork-api repo root:
cargo run --release --bin export-ml -- \
  --database-url "$DATABASE_URL" \
  --output "../autoresearch-win-rtx/data/hebrew-bridge.jsonl" \
  --language hbo \
  --books Gen,Exod,Lev     # optional filter; omit for all OT

# Or with an .env file:
cargo run --release --bin export-ml -- \
  --env apps/api/.env \
  --output ../autoresearch-win-rtx/data/hebrew-bridge.jsonl
```

The binary queries `resolved_tokens` (the authoritative post-pipeline table) joined to `passage_tokens` and `phrase_structure_nodes`. It does not re-run the translation pipeline — it exports what was already computed and stored.

---

## 4. Python ingest side

Suggested file: `prepare_translate.py` (alongside existing `prepare.py`).

```python
"""
prepare_translate.py — ingest hebrew-bridge.jsonl into tokenized training tensors.

Each verse becomes one sequence:
  [VERSE_REF] [HEB_TOKEN_1] [MORPH_1] ... [ENG_1] ... [/VERSE]

Usage:
    python prepare_translate.py \
        --input data/hebrew-bridge.jsonl \
        --output data/translate_train.bin
"""

import json, pathlib, struct, sys
import torch

INPUT  = pathlib.Path("data/hebrew-bridge.jsonl")
OUTPUT = pathlib.Path("data/translate_train.bin")

def verse_to_text(verse: dict) -> str:
    parts = [f"[{verse['verse_ref']}]"]
    for t in verse["tokens"]:
        morph = t["morph"]
        parts.append(t["surface"])
        parts.append(t["morphology_code"])
        parts.append(t["rendering"]["english"])
        if t["rendering"].get("rare_stem_fallback"):
            parts.append("[RARE_STEM]")
        if t["applied_layers"]:
            parts.append(f"[LAYERS:{','.join(t['applied_layers'])}]")
    parts.append(f"[EN] {verse['verse_english']}")
    return " ".join(parts)

sequences = []
with open(INPUT) as f:
    for line in f:
        verse = json.loads(line)
        sequences.append(verse_to_text(verse))

# Caller then tokenizes `sequences` with the existing BPE tokenizer from prepare.py
# and writes binary shards in the same format as tinystories.
```

The caller re-uses the `rustbpe` tokenizer already present in `prepare.py`. No new tokenizer training is needed unless a Hebrew-specific vocabulary is desired.

---

## 5. Versioning and provenance

Every JSONL file carries three fields on every line (redundant but safe for sharded files):

| Field | Value | Source |
|-------|-------|--------|
| `schema_version` | Integer, starts at `1` | Bumped on breaking schema changes |
| `generator_commit` | 7-char git SHA from `git rev-parse --short HEAD` at build time (via `build.rs` or `env!`) | Identifies exporter code |
| `generated_at` | RFC-3339 UTC timestamp | `chrono::Utc::now()` |

A companion sidecar file `hebrew-bridge.jsonl.meta.json` records corpus stats:
```json
{ "schema_version": 1, "generator_commit": "a4123c6", "generated_at": "...",
  "verse_count": 23145, "token_count": 306821, "language": "hbo",
  "resolved_tokens_coverage": 0.997 }
```

---

## 6. Estimated effort

| Task | Estimate |
|------|----------|
| `fw-export-ml` crate scaffold + Cargo wiring | 1h |
| DB query layer (resolved_tokens + passage_tokens + phrase_structure_nodes JOIN) | 2h |
| JSON serialization + JSONL writer | 1h |
| CLI arg parsing (`clap`) + `.env` support | 1h |
| `applied_layers` passthrough (requires `resolved_tokens` to store it, or re-derive from `resolution.chain`) | 2h |
| `prepare_translate.py` + integration test against 10-verse sample | 2h |
| End-to-end smoke test (Gen 1–3) | 1h |

**Total: ~10 hours for a working exporter covering Hebrew.**

The main scope risk is `applied_layers`. The `VerseToken.applied_layers` field tracks which post-rendering layers (`hiphil`, `subject`, `participle`) mutated a token, but this is currently ephemeral — it is never written to `resolved_tokens`. Either (a) add a `layers_applied` JSONB column to `resolved_tokens` before running the exporter, or (b) re-derive it at export time by diffing `rendering.english` against `resolution.chain` winner — option (b) is brittle. **Recommended: add the column first (1h migration).**

---

## 7. Out of scope / deferred

- Greek (NT): same architecture, second output file. ~6h after Hebrew works.
- Database schema changes beyond the `layers_applied` column.
- Real-time streaming or incremental export (JSONL file is regenerated in full).
- Gold-standard alignment supervision (word_alignments table has 1.15M rows — reserved for a future supervised training experiment).
- Python model changes: `prepare_translate.py` feeds the existing training loop; training code changes are a separate task.
