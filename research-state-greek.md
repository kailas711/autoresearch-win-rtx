# Research state — Greek

**Last session:** 2026-04-26 (placeholder; track gated on prerequisites)
**Last commit:** n/a
**Branch:** none
**Phase:** *Pending — track not yet runnable.*
**Current direction:** *None — track gated.*

## Direction status

- Misses on current direction: n/a
- Best result this direction: n/a

## Tried / kept / discarded

| Commit | val_bpb | Status | Description |
|---|---|---|---|
| _(track not yet started)_ | | | |

## Prerequisites (must be met before first session)

The Greek track is gated until *all* of the following are in place:

- [ ] **Greek gold corpus.** Either:
  - (a) Greek teaching materials analogous to the Genesis 1-11 PDFs are added to `gold/` and extracted via the same pdftotext + agent pipeline, OR
  - (b) The user provides Greek gold translations directly (image, doc, or text).
- [ ] **Greek source text.** SBLGNT (or another Koine NT edition) selected and ingested.
- [ ] **Greek morphology + phrase data.** Macula Greek / OpenGNT alignments fetched.
- [ ] **Greek lexicon access.** Confirmed derivative-use rights for BDAG (commercial). Public-domain fallback: Thayer + LSJ only.
- [ ] **Hebrew track validation.** The Hebrew track has at least produced a working baseline + first autoresearch loop iteration. This validates the methodology before duplicating infrastructure for Greek.

## Open questions

- **Greek-specific rubric.** The current `gold/rubric.md` is Hebrew-focused. Greek has its own structural distinctives (article patterns, participial constructions, μέν…δέ correlative pairs, aorist vs imperfect aspect). A `gold/rubric-greek.md` will need to be extracted once Greek gold exists.
- **Same model or separate?** User stated "I need separate models" — confirmed separate. But the *infrastructure* (tokenizer, training loop, eval harness) is shared. Need to decide: shared infrastructure with two model heads, or two parallel projects.
- **Order of work.** Run Greek track *after* Hebrew track validates the methodology, or *in parallel* once Hebrew Phase 1 exists?

## Next-session entry point

**Track is not runnable.** The next *productive* work for the Greek track is **gathering Greek gold corpus** — either by adding Greek teaching PDFs and running the same extraction pipeline used for Hebrew, or by having the user provide Greek gold translations directly. Until that exists, this state file is a placeholder.

Once Greek prerequisites are met:
1. Mirror the Hebrew Phase 1 deliverables for Greek (separate `prepare_translate_greek.py` or shared with track flag).
2. First autoresearch direction will mirror Hebrew's first direction (Tier 1 — LR schedule sweep) but on Greek-specific data.

## Provenance

- Lexicons in scope: Thayer, LSJ, BDAG
- Source corpus: TBD (SBLGNT candidate)
- Gold corpus: TBD (no extraction yet)
