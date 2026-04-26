# Autoresearch Team Orchestration — Hebrew/Greek Translation

**Date:** 2026-04-26
**Generic plan:** `C:\git\fellwork\agent-team-orchestration-plan.md` (v2.1)
**Project:** `autoresearch-win-rtx`
**Status:** Initial scaffold; first session has not yet run.

This document binds the project-agnostic Agent Team Orchestration Plan v2.1 to *this* project's research. It defines roster, checkpoint format, resume protocol, and spawn templates so each new session can pick up exactly where the previous one left off.

---

## Research thesis

> The user's gold verses can be translated from the original Hebrew and Greek text — preserving sentence phrasing and intention — despite the compromises every existing English translation makes. Reaching that goal requires *two separate models* (one Hebrew→English, one Koine Greek→English) trained against scholarly lexicons (HALOT, KM, BDB for Hebrew; Thayer, LSJ, BDAG for Greek) and the gold corpus. The end product is a translation model exportable to a Rust API.

This research thesis is the success criterion. "Research complete" means: a trained model per language + rubric metric meeting agreed thresholds + an export path the Rust API can consume.

---

## Project binding (per generic plan §11)

### Linked repositories

| Name | Role | Path | Branch | Notes |
|---|---|---|---|---|
| `autoresearch-win-rtx` | **primary-write** | `C:\git\fellwork\autoresearch-win-rtx` | `autoresearch/<tag>` per session | Where experiments run and state files live |
| `fellwork-api` | **read** | `C:\git\fellwork\fellwork-api` | n/a | Reference for prior rule work; eventual rebuild target. **Never written by the team.** |

### Two parallel research tracks

| Track | Status | Source corpus | Gold | Lexicons | State file |
|---|---|---|---|---|---|
| **Hebrew** | Active | OSHB (ETCBC morphology) + Macula | `gold/catalog.json` (95 entries) | HALOT, KM, BDB | `research-state-hebrew.md` |
| **Greek** | Pending | TBD (SBLGNT?) | TBD | Thayer, LSJ, BDAG | `research-state-greek.md` |

Tracks share orchestration scaffolding (this doc + roster + protocol) but iterate independently with separate state files. A session targets exactly one track.

### Lexical authority

Each track names the lexicons whose entries are loaded by `prepare_translate.py` as part of the per-token feature set the model sees. Lexicons are loaded into a side-table keyed by lemma; the training data references the side-table by lookup.

**Licensing:** The user has access rights to all six lexicons (HALOT, KM, BDB for Hebrew; Thayer, LSJ, BDAG for Greek), so the full lexicon set is in scope. *Note for downstream:* if the trained model or its outputs are eventually published, redistribution of derivative content involving HALOT/BDAG should be reviewed against those publishers' terms. Internal research use is unaffected.

### Success criteria (research-complete signal)

A track is "complete" when **all** of:
1. Trained model produces translations on the gold-test holdout set.
2. The `evaluate_translate.py` rubric metric clears the agreed-on threshold (TBD by Phase 5).
3. The model artifact is exportable to a Rust runtime usable by the `fellwork-api` rebuild (Candle, Burn, ONNX, or distilled-rule code-gen — pick later).
4. A Scribe-produced handoff doc exists describing the model, its eval results, and how to load it.

---

## Roster (M-scope default per generic plan §2)

The M-scope sweet spot — Team Lead + Scout + Builder + Verifier — fits a single per-direction session (1–4 hours of work). Specialists spawn on-demand.

| Role | Filled by | Spawn timing | Output |
|---|---|---|---|
| **Team Lead** | This Claude session | Always | Decomposition, role assignment, safety policy, final handback |
| **Scout** | Subagent (sonnet) | Start of session | `scout-report.md`: state-file validation, repo state, do-not-break list |
| **Builder** | Subagent (sonnet) | Mid-session | `build-manifest.md`: experiments run, files changed, results.tsv updates |
| **Verifier** | Subagent (sonnet) | After Builder | `verification-report.md`: pass/fail per spec, regression check |
| **Investigator** | Subagent (sonnet) | On-demand | `investigation-report.md`: root cause for crashes; Iron Law applies |
| **Historian** | Subagent (sonnet) | End of session | New `research-state-<track>.md` + `retro.md` |

**No Architect** in the default per-direction session — `program.md` already defines the experimental approach. Architect is needed only when a *new direction* requires a non-trivial design choice (e.g., switching from Tier 1 to a brand-new Tier 2 architectural variant); spawn ad-hoc in that case and bump session scope to L.

**No Releaser** — autoresearch experiments live on the per-session branch and are not deployed. The only "release" is when a track's research-complete signal triggers a final PR; that is a separate L-scope session with a Releaser.

---

## Safety mode

**Guarded + Frozen** scope (per generic plan §5).

| File / path | Access | Reason |
|---|---|---|
| `train.py` | **writable** | The agent's edit target per `program.md` |
| `results.tsv`, `learnings.md` | **append-only** | Per-experiment records per `program.md` |
| `research-state-<track>.md` | **writable** (Historian only) | Session checkpoint |
| `prepare.py`, `prepare_translate.py` | **read-only** | Fixed evaluation harness |
| `gold/`, `gold/catalog.json`, `gold/rubric.md` | **read-only** | Ground truth; not modified during research |
| `evaluate_translate.py` | **read-only** | Metric is the contract |
| `program.md` | **read-only within session** | Direction guidance; modified only via separate human-approved PRs |
| `docs/`, `pyproject.toml`, `fellwork-api/*` | **read-only** | Out of scope |

Hard stops carried forward from generic plan §6:
- Builder ↔ Verifier ping-pong > 3 rounds → Team Lead intervenes
- Investigator rejects 3 hypotheses without root cause → escalate
- Crash that Investigator cannot root-cause → freeze direction, switch
- Token-spend ceiling → pause
- Direction stalls (3 misses per `program.md`) → Historian rotates direction
- Safety-mode breach → hard stop

---

## Session granularity (Q1 = b)

**One session = one research direction.** A "direction" is a single area inside a tier (per `program.md`'s Tier 1 / Tier 2 split):

- Tier 1 example: tune `MATRIX_LR` over a sweep until 3 consecutive misses
- Tier 2 example: ablate `WINDOW_PATTERN` variants until 3 consecutive misses

End-of-session is triggered by:
- 3 consecutive misses in the active direction → Historian rotates and writes new state
- ≥ 4 hours of wall-clock work (M-scope ceiling)
- Hard-stop condition fires
- User pause

Expected throughput: **3–5 sessions per overnight run**, ~12–20 experiments per session (each ~5 min training + setup overhead).

---

## Checkpoint state (Q2 = both)

Two complementary mediums.

### `research-state-<track>.md` — single-pointer state

A markdown document at repo root, one per track. Updated by the Historian at end-of-session. Schema:

```markdown
# Research state — <track>

**Last session:** <YYYY-MM-DD HH:MM>
**Last commit:** <short-sha>
**Branch:** <autoresearch/<tag>>
**Phase:** <Phase 1 | Phase 2 | ...>
**Current direction:** <e.g., "Tier 1 — LR schedule sweep">

## Direction status
- Misses on current direction: <N> / 3
- Best result this direction: val_bpb=<x.xxxxxx>, commit=<sha>

## Tried / kept / discarded (this branch)
| Commit | val_bpb | Status | Description |
| ... | ... | keep | ... |
| ... | ... | discard | ... |
| ... | ... | crash | ... |

## Open questions
- <bullet list>

## Next-session entry point
<short prose describing exactly what the next session should do>
```

The Historian's job at end-of-session is to produce this file from the session's events. Scout's first task at start-of-session is to *validate* this file against actual git/filesystem state and flag drift.

### Git artifacts — full history

The existing `program.md` contract continues:
- Branches: `autoresearch/<tag>` per session-arc
- `results.tsv`: append-only per-experiment row
- `learnings.md`: append-only per-experiment prose entry
- Commits: each kept experiment is one commit

The single-pointer `research-state-<track>.md` is a *summary* of git artifacts, not a replacement.

---

## Resume protocol

Steps to start a new session on an existing track:

1. **Team Lead** opens new Claude session in `autoresearch-win-rtx`.
2. **Team Lead** reads `research-state-<track>.md` and the current branch's `results.tsv` + `learnings.md`.
3. **Team Lead** decides: continue current direction (if misses < 3) or rotate direction.
4. **Team Lead** spawns Pattern B team (Scout + Builder + Verifier) per `agent-team-orchestration-plan.md` §8.
5. **Scout** validates state file matches actual git state; flags drift; produces `scout-report.md`.
6. **Builder** runs experiments per the active direction; commits each kept improvement; appends to `results.tsv` and `learnings.md`.
7. **Verifier** scores experiments against rubric metric; reports pass/fail.
8. **Investigator** spawns on-demand for any crash Builder cannot self-fix in one round.
9. End-of-session triggers (3 misses / wall-clock / hard stop): **Historian** spawns; rewrites `research-state-<track>.md`; produces `retro.md`.
10. **Team Lead** commits Historian's outputs and reports session summary to user.

---

## Spawn prompt template — Hebrew direction (Pattern B, M-scope)

Copy-paste below at start of a Hebrew-track session. Replace `<DIRECTION>` and `<DESCRIPTION>` from `research-state-hebrew.md`'s "Current direction" and "Next-session entry point" sections.

```
Create a team of three teammates to advance Hebrew→English autoresearch on
the active direction "<DIRECTION>". This is a per-direction M-scope session
under the autoresearch team orchestration (docs/autoresearch-team-orchestration.md).

Repositories in scope:
- autoresearch-win-rtx (primary-write): C:\git\fellwork\autoresearch-win-rtx
  - branch: autoresearch/<tag-from-state-file>
  - writable: train.py, results.tsv, learnings.md
  - read-only: prepare*.py, gold/, evaluate*.py, program.md
- fellwork-api (read): C:\git\fellwork\fellwork-api  -- reference only

Active state files:
- research-state-hebrew.md
- gold/rubric.md (P1, P3, P4, P6, P8, P10, P12 are the highly-automatable
  rubric patterns; metric weights live in evaluate_translate.py)

Spawn:

- Scout: read research-state-hebrew.md, results.tsv, learnings.md, current
  branch HEAD. Validate state file matches reality (commits, metrics).
  Produce scout-report.md flagging any drift. External research: none unless
  the direction explicitly requires it.

- Builder: implement experiments for <DIRECTION>. <DESCRIPTION>. Each
  experiment edits train.py, runs `uv run train.py > run.log 2>&1`, captures
  results, decides keep/discard per program.md rules, commits if kept,
  appends to results.tsv and learnings.md. Stop after 3 consecutive misses
  or 4-hour wall clock. Produce build-manifest.md.

- Verifier: for each kept experiment, confirm results.tsv and learnings.md
  match commit metadata; rerun evaluate_translate.py if available; flag any
  mismatch between claimed and measured val_bpb. Produce verification-report.md.

Safety mode: Guarded. Frozen scope: only train.py, results.tsv, learnings.md
are writable. program.md, prepare*.py, gold/, evaluate*.py, docs/ are
read-only this session.

Dependency chain: Scout → Builder → Verifier. Peer messaging allowed.
Hard stops: 3 ping-pong rounds, 3 unsolved hypotheses (Investigator), token
ceiling, safety breach.

Iron Law: any crash Builder cannot self-fix in one round triggers
Investigator (separate spawn). No fixes without root cause.

End of session: Team Lead spawns Historian to rewrite
research-state-hebrew.md and produce retro.md.
```

---

## Spawn prompt template — Greek direction

**Status:** Not runnable until Greek prerequisites are met (see
`research-state-greek.md`). Once met, mirror the Hebrew template substituting:

- Track-specific state file: `research-state-greek.md`
- Lexicons: Thayer, LSJ, BDAG
- Source corpus: SBLGNT (or chosen Greek source)
- Gold corpus: TBD

---

## Open questions (TODO before first real session)

These do not block writing this orchestration doc, but they block running
the first productive Builder session:

1. **Phase 1 spec simplification (PR #5).** This doc currently references
   `prepare_translate.py` and `evaluate_translate.py` as if they exist.
   They do not — they are Phase 1 deliverables. The first Phase-1-build
   sessions will produce them. Open question: do per-direction sessions
   make sense for *building* Phase 1 deliverables, or only for *iterating*
   on a working baseline (Phase 2+)? Recommendation: Phase 1 build is more
   linear; reserve this orchestration for Phase 2+. Use a simpler L-scope
   feature-dev session for Phase 1 build itself.

2. **Greek gold corpus.** No Greek teaching materials extracted yet. Greek
   track is gated until either (a) Greek-equivalent PDFs are added to
   `gold/` and extracted, or (b) the user provides Greek gold translations
   directly.

3. **Rust export mechanism.** Candle vs Burn vs ONNX vs distilled-rules. To
   be decided in Phase 5 once a model exists; recorded here as an open
   question so it does not get forgotten.

4. **Verifier vs evaluate_translate.py overlap.** The Verifier role and
   `evaluate_translate.py` both score experiments. Once `evaluate_translate.py`
   exists, the Verifier's job collapses to "run the script and confirm
   results.tsv row matches script output." Worth simplifying then.

**Resolved:** Lexicon access for HALOT, KM, BDB, Thayer, LSJ, and BDAG is
confirmed (2026-04-26). All six are in scope.

---

## References

- Generic plan: `C:\git\fellwork\agent-team-orchestration-plan.md` (v2.1)
- Phase 1 spec: `docs/superpowers/specs/2026-04-25-phase-1-design.md`
  (live revision in PR #5 simplifies away fellwork-api integration)
- Translation rubric: `gold/rubric.md`
- Gold corpus: `gold/catalog.json`
- Existing rule pipeline (read reference): `C:\git\fellwork\fellwork-api\crates\fw-translate-hebrew`
- Program guidance: `program.md` (research priorities, tier rules,
  experiment loop, learnings.md format)
