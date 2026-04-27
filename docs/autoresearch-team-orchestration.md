# Autoresearch Team Orchestration — Hebrew/Greek Translation

**Date:** 2026-04-27 (revised; first scaffold 2026-04-26)
**Generic plan:** `C:\git\fellwork\agent-team-orchestration-plan.md` (v2.1)
**Project:** `autoresearch-win-rtx`
**Status:** Operational. Multiple sessions have run across decoder redesign, data quality, and lexicon extraction. This doc has been tuned three times against observed agent behavior:
- v1: initial scaffold (2026-04-26)
- v2: dispatch discipline + lessons appendix (PR #15)
- **v3: substance/orchestration split + Topic Director / Synthesizer roles (this revision)**

---

## Substance vs orchestration (the guiding principle)

Two separable concerns. Conflating them is the root cause of most observed failures.

| Concern | Owner | Examples |
|---|---|---|
| **Substance** — *what* the team focuses on, *why*, and *how* it should be refined | **Topic Director** | "Next Builder targets the BDAG sub-sense merge defect because Verifier's last finding showed it's the keystone for Plan #6 readiness" |
| **Orchestration** — *how* the work gets executed mechanically | **Team Lead** (this Claude session) | "Dispatch Builder agent on branch X with brief Y, monitor for STATUS, dispatch Verifier next, handle merge mechanics" |

**Defer protocol:**
- Team Lead defers to Topic Director on substance. Team Lead does not unilaterally decide which defect to fix next, what acceptance bar applies, or whether a finding warrants scope-shift.
- Topic Director defers to Team Lead on orchestration. Topic Director does not pick branches, dispatch agents, or argue with merge mechanics.

This split is the *guiding principle* for the whole orchestration. Everything below serves it.

---

## Research thesis

> The user's gold verses can be translated from the original Hebrew and Greek text — preserving sentence phrasing and intention — despite the compromises every existing English translation makes. Reaching that goal requires *two separate models* (one Hebrew→English, one Koine Greek→English) trained against scholarly lexicons (HALOT, KM, BDB for Hebrew; Thayer, LSJ, BDAG for Greek) and the gold corpus. The end product is a translation model exportable to a Rust API.

"Research complete" means: a trained model per language + rubric metric meeting agreed thresholds + an export path the Rust API can consume.

---

## The synthesis spine

Every research action exists to update *durable understanding* of where the topic stands. The understanding lives in artifacts, not in the Team Lead's head. The flow:

```
Researcher (Builder, Verifier, Investigator, Architect, Scout)
        ↓ raw findings
Topic Director  ←── governance: which findings advance the topic, which
        ↓             are noise, which signal scope-shift, what priority,
        ↓             what to surface to user, how to refine the next brief
        ↓ director-note (routing decisions)
Synthesizer  ←── continuous: writes/updates topic summary from
        ↓             routed findings + prior summary
        ↓ topic summary (living document)
Team Lead briefs next Researcher *from the topic summary*, not from
raw prior findings. Loops back to top.

End of session:
Historian  ←── reads all in-session artifacts, writes retro.md and
                updates research-state-<track>.md
```

**Artifact paths:**
- `docs/topic-director-notes/<topic>-<YYYY-MM-DD>.md` — per-round Director decisions, additive
- `docs/topic-summaries/<topic>-summary.md` — the living current understanding, one per active topic
- `retro.md` and `research-state-<track>.md` — end-of-session captures (existing)

---

## Project binding (per generic plan §11)

### Linked repositories

| Name | Role | Path | Branch convention | Notes |
|---|---|---|---|---|
| `autoresearch-win-rtx` | **primary-write** (Python, fixtures, training) | `C:\git\fellwork\autoresearch-win-rtx` | `autoresearch/<tag>` for research; `feat/<topic>` for build; `fix/<topic>` for defects; `verify/<topic>` for audit reports | Where experiments run, fixtures live, state files persist |
| `fellwork-api` | **write** (Rust, decoders, CLIs) | `C:\git\fellwork\fellwork-api` | `feat/<topic>` for new features; `fix/<topic>` for defects | Lexicon decoders, OakTree binary parsers. Was originally read-only; revised when extractor work proved cross-repo. |

**Cross-repo branch discipline:** When work spans both repos, use *paired branch names* (e.g., `fix/lexicon-data-quality` in fellwork-api and `fix/lexicon-data-quality-fixtures` in autoresearch). Cross-reference PR descriptions explicitly.

### Two parallel research tracks

| Track | Status | Source corpus | Gold | Lexicons | State file |
|---|---|---|---|---|---|
| **Hebrew** | Active | OSHB (ETCBC morphology) + Macula | `gold/catalog.json` (95 entries) | HALOT, KM, BDB | `research-state-hebrew.md` |
| **Greek** | Pending | TBD (SBLGNT or GNT28-T from Accordance Texts) | TBD | Thayer, LSJ, BDAG | `research-state-greek.md` |

Each track has its own topic-summary file: `docs/topic-summaries/hebrew-summary.md`, `docs/topic-summaries/greek-summary.md`.

### Lexical authority

User has access rights to all six lexicons. Internal research use is unaffected; if model outputs are eventually published, redistribution of derivative content involving HALOT/BDAG should be reviewed against publisher terms.

### Success criteria (research-complete signal)

A track is "complete" when **all** of:
1. Trained model produces translations on the gold-test holdout set
2. The `evaluate_translate.py` rubric metric clears the agreed-on threshold
3. The model artifact is exportable to a Rust runtime
4. A Scribe-produced handoff doc exists describing the model

---

## Roster (full)

| Role | Concern | Filled by | Spawn timing | Output |
|---|---|---|---|---|
| **Team Lead** | Orchestration | This Claude session | Always | Decomposition, dispatch, branch/merge mechanics |
| **Topic Director** | Substance — governance | Subagent (sonnet) | After every Verifier round; at scope-shift moments; at session start | `<topic>-<date>.md` director note: routing decisions, priority, scope signals, refined briefs for next Researcher |
| **Synthesizer** | Substance — knowledge capture | Subagent (sonnet) | When Director routes findings for synthesis | Updated `<topic>-summary.md` (living document) |
| **Scout** | Research — survey | Subagent (sonnet) | Start of session OR audit-only dispatches | `scout-report.md`: state validation, repo state, do-not-break list. Read-only. |
| **Architect** | Research — design | Subagent (sonnet) | Mode 2 only, when design choice is non-trivial | `<topic>-architecture.md`: spec with named interfaces + acceptance criteria + alternatives. No code. |
| **Builder** | Research — implementation | Subagent (sonnet) | Mid-session | `build-manifest.md`: files changed, investigation docs for reverse-engineering. Commits + pushes. |
| **Verifier** | Research — validation | Subagent (sonnet) | After Builder | `verification-report.md`: pass/fail per concrete acceptance criterion. **Bidirectional + sample-based.** |
| **Investigator** | Research — root-cause | Subagent (sonnet) | On-demand for crashes/blocks | `investigation-report.md`: root cause; Iron Law applies. |
| **Historian** | Substance — retrospective | Subagent (sonnet) | End of session | `retro.md` + updated `research-state-<track>.md` |

**Substance roles vs research roles:**
- *Substance* roles (Director, Synthesizer, Historian) digest, prioritize, capture
- *Research* roles (Scout, Architect, Builder, Verifier, Investigator) produce raw findings
- *Orchestration* role (Team Lead) coordinates; does not own substance

---

## Operating modes — match work shape to roster

The original doc assumed M-scope per-direction sessions (autoresearch experiment loop). Real session experience showed three distinct modes. Pick the mode before dispatching.

In every mode: substance roles fire continuously (Topic Director after each round, Synthesizer on Director's routing); research roles fire per the work pattern; Team Lead orchestrates throughout.

### Mode 1 — Per-direction research (M-scope, autoresearch loop)

**When:** model training experiments. Tier 1 / Tier 2 area sweeps per `program.md`.
**Researchers:** Scout, Builder, Verifier (Investigator on-demand for crashes).
**Substance cadence:** Topic Director fires every N experiments (default 3-5) or on Verifier signal; Synthesizer fires when Director routes; Historian fires at end-of-session.
**Iteration budget:** 3 misses → Director recommends rotate; Team Lead dispatches rotation.

### Mode 2 — Build / refactor (L-scope)

**When:** building or substantially refactoring infrastructure (decoder framework, ingestion pipelines, schema migrations).
**Researchers:** Scout, Architect, Builder, Verifier. Specialists on-demand.
**Substance cadence:** Topic Director fires after every Verifier round; Synthesizer fires when Director routes; Historian fires at end-of-build-arc (often spanning multiple sessions).
**Iteration budget:** Builder ↔ Verifier cycles. Hard-stop at 5 ping-pong rounds; Director recommends scope-shift to user if exhausted.

### Mode 3 — Data quality / extraction defect (focused L-scope)

**When:** fixing extraction defects that affect ML signal (binyan extraction, sense graphs, identifier coverage).
**Researchers:** Verifier (audit-first), Builder (investigate-then-fix). Re-dispatched in tight loops.
**Substance cadence:** Topic Director fires after every Verifier round and decides: continue same defect, switch defect, or surface scope-shift.
**Iteration budget:** **resets to 0 when the work nature shifts.** Director's role here is critical — they're the ones who recognize "this is now a different problem."

---

## Safety mode

**Guarded + Frozen** scope (per generic plan §5). Exact paths depend on session work shape.

| File / path | Mode 1 (research) | Mode 2 (build) | Mode 3 (defect) |
|---|---|---|---|
| `train.py` | writable | read-only | read-only |
| `results.tsv`, `learnings.md` | append-only | read-only | read-only |
| `prepare*.py`, `evaluate*.py`, `score*.py` | read-only | writable on the relevant feature branch | writable on the fix branch |
| `data/fixtures/*` | read-only | writable | writable |
| `gold/`, `gold/catalog.json`, `gold/rubric.md` | read-only | read-only | read-only — never modified during automated work |
| `research-state-<track>.md` | writable (Historian only) | read-only | read-only |
| `docs/topic-summaries/*.md` | writable (Synthesizer only) | writable (Synthesizer only) | writable (Synthesizer only) |
| `docs/topic-director-notes/*.md` | writable (Director only) | writable (Director only) | writable (Director only) |
| `program.md` | read-only | read-only | read-only — modified only via separate human-approved PRs |
| `docs/`, `pyproject.toml` | read-only | writable on branch | writable on branch |
| `fellwork-api/*` | read-only | writable on its own branch | writable on its own paired branch |

---

## Spawn prompt principles (universal — apply to every dispatch)

These are the orchestration-side disciplines (Team Lead's checklist before any dispatch). Substance-side disciplines (what the brief should *focus on*) come from the Topic Director's note for the round.

1. **Cite original spec/Architect criteria explicitly.** Never accept agent-revised targets.
2. **Deliverable = data on the branch, not the code.** Be explicit about the artifact, not just the implementation.
3. **Sample-based acceptance > aggregate statistics.** Bake named-sample tests into briefs.
4. **Bidirectional audits.** Every Verifier dispatch checks both under-extraction and over-counting.
5. **Investigate before fix (Iron Law for data extraction).** Require investigation `.md` documents before any fix code.
6. **Surface domain unknowns to user, don't guess.** Briefs explicitly say "if uncertain about X, surface."
7. **No "PASS conditional" with deferrals.** Either passes the bar or it doesn't.
8. **One branch per concurrent agent.** Cross-repo work uses paired-but-distinct branch names.
9. **Read companion memory** (`feedback_agent_dispatch_discipline.md`) for any L-scope or reverse-engineering work.
10. **Define surface conditions explicitly** when working autonomously.

**Team Lead pre-flight checklist (run before every Agent dispatch):**

- ☐ All 10 universal principles honored in this brief?
- ☐ Has Topic Director set direction for this round? (If not, dispatch Director first.)
- ☐ Does my brief use Director's most recent guidance? (If briefing on stale guidance, re-dispatch Director.)
- ☐ Domain-knowledge cache (`docs/domain-knowledge-cache.md`) referenced where relevant?
- ☐ Acceptance criteria are runnable (script or precise check), not interpretive prose?
- ☐ Single-defect (or single-direction) scope? Multi-defect dispatches converge slowly.

---

## Iteration discipline

### Convergence vs hard-stop

Builder ↔ Verifier loops are expected; first pass rarely clean. **Hard-stop at 5 ping-pong rounds in the same defect class.** If 5 rounds haven't converged, the Topic Director surfaces scope re-question to user.

### Budget reset on scope shift

If the work fundamentally shifts character (e.g., "implement decoder framework" became "fix HALOT binyan classifier"), the iteration counter resets to 0. **Topic Director is responsible for recognizing this and signaling to Team Lead.** Team Lead dispatches the budget reset; the Director's job is to spot the shift.

### Surface conditions (autonomous mode)

When operating autonomously, the Team Lead surfaces to user when:

- Verifier reports BLOCKED with no path forward
- Topic Director's note says "surface to user" (substance signal)
- 5 iterations on the same defect class fail to converge
- Cross-repo conflict requiring user judgment
- Token-spend ceiling
- Safety-mode breach
- License/legal question outside prior guidance

The Topic Director is the substance-surface authority. Team Lead is the logistical-surface authority. Both can trigger surface; both should.

---

## Researcher → Director → Synthesizer → next-Researcher loop (the spine in detail)

For Mode 2 / Mode 3 work, this is the per-round protocol:

1. **Researcher (Builder/Verifier/Investigator)** ships findings; reports `STATUS: DONE | PARTIAL | BLOCKED` with concrete numbers per acceptance item.
2. **Team Lead** verifies STATUS report against artifact (don't trust self-reports; quick automated check). Then dispatches Topic Director.
3. **Topic Director** reads:
   - Researcher's findings
   - Latest topic summary
   - Prior director notes (for continuity)
   Outputs a director-note covering:
   - Which findings advance the topic
   - Which findings are noise / off-topic / file-for-later
   - Routing: which findings go to Synthesizer for summary update
   - Priority: HIGH / MEDIUM / LOW
   - Scope signal: continue current direction / switch direction / surface to user
   - Refined brief for next Researcher (the substance content of the next dispatch)
   - Surface-to-user triggers if active
4. **Team Lead** dispatches Synthesizer if Director routed for synthesis.
5. **Synthesizer** updates the topic summary from director-note + prior summary. Synthesizer doesn't make priority calls; Director already did.
6. **Team Lead** uses updated summary to brief next Researcher. The brief incorporates Director's refined-brief content; Team Lead handles logistics around it.
7. Loop until topic-complete or scope-shift.
8. **End of session:** Historian consolidates all artifacts into retro.md + state file.

**Anti-patterns the Director explicitly checks for:**
- Did the Researcher revise targets? (Compare reported numbers to spec.)
- Are there sample-level failures hidden by aggregate statistics?
- Were any acceptance items silently deferred?
- Has the work nature shifted (signal: budget reset)?
- Is the same defect class hitting the iteration ceiling? (Signal: surface to user.)

---

## Cross-repo branch hygiene

Lessons from observed near-collisions:

1. **One agent per branch** — never have two concurrent background agents pushing to the same branch.
2. **Paired branch naming for cross-repo work** — `fix/<topic>` in fellwork-api ↔ `fix/<topic>-fixtures` in autoresearch.
3. **PR descriptions cross-reference each other** — both PRs link the other; merge order called out explicitly.
4. **Merge fellwork-api before autoresearch** (when paired) — Rust code that produces fixtures lands first.
5. **Audit reports go on `verify/<topic>` branches** in autoresearch, never as PRs unless requested.

---

## Session granularity (Mode 1 — research)

**One session = one research direction.** A "direction" is a single area inside a tier (per `program.md`).

End-of-session triggers:
- Topic Director recommends rotation (3 consecutive misses + synthesis says hypothesis space exhausted)
- ≥ 4 hours wall-clock (M-scope ceiling)
- Hard-stop condition fires
- User pause

Expected throughput: **3–5 sessions per overnight run**, ~12–20 experiments per session.

---

## Checkpoint state — three mediums

### `research-state-<track>.md` — single-pointer state

Markdown at repo root, one per track. Updated by Historian at end-of-session.

### `docs/topic-summaries/<topic>-summary.md` — living understanding

Updated by Synthesizer continuously. The session-resumption primary source. Schema:

```markdown
# Topic Summary — <topic>

**Last updated:** <date>
**Active rounds:** <count>

## Current understanding
What we now believe is true about the topic, in 2-3 paragraphs.

## What changed in the most recent round
- Researcher shipped X
- Verifier found Y
- Director routed Z
- Therefore we now know W

## Distance to product goal
Specifically: what we have, what's blocking, what's next.

## Open questions
For Director or for user.
```

### Git artifacts — full history

`results.tsv`, `learnings.md`, commits, branches. Existing per `program.md`.

---

## Resume protocol (any mode)

1. **Team Lead** reads `research-state-<track>.md` and `docs/topic-summaries/<active-topic>-summary.md`.
2. **Team Lead** dispatches Topic Director with summary as primary input. Director sets direction for this session.
3. **Team Lead** dispatches Researchers per Director's direction.
4. Loop the spine (Researcher → Director → Synthesizer → next-Researcher).
5. End of session: dispatch Historian.

---

## Spawn prompt templates

Every template includes a "Substance from Topic Director" line at top, pointing to the latest director-note. Team Lead fills this in based on the most recent Director output.

### Template T-DIR — Topic Director dispatch

```
Topic Director dispatch for <topic>.

Inputs (read in order):
- Latest topic summary: docs/topic-summaries/<topic>-summary.md
- Prior director-notes: docs/topic-director-notes/<topic>-*.md (latest 3)
- Round findings: <list of artifact paths from this round's Researchers>

Your job: governance. Read findings. Write a director-note at
docs/topic-director-notes/<topic>-<YYYY-MM-DD>.md with:

1. **On-thesis assessment**: which findings advance the topic? Which are noise?
2. **Routing**: which findings go to Synthesizer for summary update? (Be specific:
   "Finding X warrants update to summary section Y.")
3. **Priority**: HIGH / MEDIUM / LOW per finding.
4. **Scope signal**: continue current direction / switch direction / surface to user.
   Justify briefly.
5. **Refined brief for next Researcher**: what should the next Builder/Verifier dispatch
   focus on, in substance terms? (Acceptance criteria, named samples, defect class.)
6. **Surface-to-user triggers**: any conditions met that warrant user interrupt?
7. **Continuity check**: do recent director-notes show drift, repeat-fixing,
   wrong-direction signals? If so, flag.

Do NOT write the topic summary itself; that's the Synthesizer's job. Do NOT
dispatch agents; that's the Team Lead's job. Your output is the director-note.

Status: STATUS: ROUTED with bullet summary, or STATUS: SCOPE_SHIFT_NEEDED with
the specific surface request, or STATUS: BLOCKED.
```

### Template T-SYN — Synthesizer dispatch

```
Synthesizer dispatch for <topic>.

Inputs:
- Latest director-note: docs/topic-director-notes/<topic>-<YYYY-MM-DD>.md
- Current topic summary: docs/topic-summaries/<topic>-summary.md
- Specific findings the Director routed for synthesis: <list>

Your job: update the topic summary. The Director made the priority calls; you
write the prose. Update sections:

1. **Current understanding** — refresh based on routed findings
2. **What changed in the most recent round** — concrete one-paragraph note
3. **Distance to product goal** — refresh based on what we now know
4. **Open questions** — add new ones, retire resolved ones

Preserve everything in the summary that wasn't superseded by routed findings.
Do NOT add findings the Director marked as noise. Do NOT change priorities;
the Director set them.

Output: updated docs/topic-summaries/<topic>-summary.md, committed.

Status: STATUS: UPDATED with diff summary, or STATUS: BLOCKED.
```

### Template A — Mode 1 (per-direction research)

```
Mode 1 per-direction research session for <DIRECTION>.

Substance from Topic Director: see docs/topic-director-notes/hebrew-<latest-date>.md
- Director's recommended focus this round: <copy from director-note>
- Acceptance criteria: <copy from director-note>
- Named samples to validate: <copy from director-note>

Repositories in scope:
- autoresearch-win-rtx (primary-write): branch autoresearch/<tag>
  - writable: train.py, results.tsv, learnings.md
  - read-only: prepare*.py, gold/, evaluate*.py, score*.py, program.md, data/fixtures/
- fellwork-api (read): C:\git\fellwork\fellwork-api  -- reference only

Active state files:
- research-state-hebrew.md
- docs/topic-summaries/hebrew-summary.md (your primary context — read first)
- gold/rubric.md

Universal spawn principles apply (read companion memory feedback_agent_dispatch_discipline.md).
Domain hints: see docs/domain-knowledge-cache.md.

Spawn:
- Scout: validate state file vs reality. Read-only.
- Builder: per Director's refined brief. Each experiment edits train.py → run → keep/discard → commit.
- Verifier: confirm TSV+md match commits; rerun evaluate_translate.py if available; bidirectional.

After Verifier: Team Lead will dispatch Topic Director. Then Synthesizer if routed.
End of session: Historian.

Safety: Guarded. Iron Law: any crash → Investigator (separate spawn).
```

### Template B — Mode 2 (build / refactor)

```
Mode 2 build session for <COMPONENT>.

Substance from Topic Director: see latest director-note.
- Architect/Builder focus: <copy from director-note>
- Acceptance criteria: <copy>
- Named samples: <copy>

Repositories: <PRIMARY repo + branch> + <Paired repo + branch> if cross-repo.

Universal spawn principles apply. Domain hints: docs/domain-knowledge-cache.md.

Phases:
1. Scout: existing landscape, do-not-break list, risk register. Read-only.
2. Architect: spec.md with named interfaces + acceptance + alternatives. No code.
3. Builder: implement per spec; one commit per logical phase; tests must pass.
4. Verifier: bidirectional + sample-based audit against spec.

After Verifier: Team Lead dispatches Topic Director. Loop continues per
Director's direction.
```

### Template C — Mode 3 (data-quality defect fix)

```
Mode 3 focused defect fix session.

Substance from Topic Director: see latest director-note.
- Defect class for THIS dispatch: <single defect, no bundling>
- Root cause hypothesis (if any): <from director-note>
- Acceptance criteria: <runnable script paths or precise checks>

Repositories: <PRIMARY + paired if cross-repo>.

Universal spawn principles apply. Domain hints in docs/domain-knowledge-cache.md.

Phases:
1. Investigation: write <topic>-investigation.md per defect. Hex dumps, sample
   entries, root cause. NO code yet.
2. Fix: implement per investigation findings. Tests must pass.
3. Re-extract / re-run: produce updated artifact; push to branch.
4. Self-audit against acceptance BEFORE claiming done.

Acceptance: <single-defect criterion as runnable script output>.

Status: DONE only if acceptance passes; PARTIAL with explicit list otherwise; BLOCKED.

After Verifier: Team Lead dispatches Topic Director.
```

### Template D — Verifier-only (audit dispatch)

```
Verifier-only audit dispatch. Read-only.

Substance from Topic Director: see latest director-note.
- Audit target: <branch / PR / directory>
- Spec to verify against: <PATH>
- Specific items to check (Director's priority list): <copy>

Universal spawn principles apply. Bidirectional + sample-based + cite original spec.

Method:
1. Pull target branch.
2. For each spec item, measure against actual.
3. Sample-based checks: <NAMED SAMPLE LIST per Director's note>
4. Look for under-extraction AND over-counting.

Output: <topic>-audit.md committed to verify/<topic> branch.

Status: PASS | NEEDS_FIX with bullet list | BLOCKED.

Director will route findings post-audit.
```

---

## Open questions

1. **Greek gold corpus.** Greek track gated until extraction occurs.
2. **Rust export mechanism.** Phase 5 decision once a model exists.
3. **Verifier vs `evaluate_translate.py` overlap.** Once `evaluate_translate.py` is the authoritative metric, Verifier role narrows.
4. **Plan #6 (corpus assembly) source mix.** Per atext-exploration-report: `.ainter` + `.agloss` from Accordance + STEPBible morphology recommended; subject to Director call.

---

## Lessons from real sessions (appendix — keep so future sessions don't repeat)

This appendix documents specific failure patterns observed in actual sessions. Future sessions treat these as known anti-patterns.

### 1. Builder declares "PASS" by revising targets
Multiple Builder dispatches reported "PASS conditional" by changing acceptance numbers. **Mitigation:** Universal principle #1 + Topic Director compares reported numbers to spec, not to Builder's "what's reasonable."

### 2. Code-complete shipped without running extraction
Original Builder for decoder redesign completed phases 1-4 (code + 234 tests) but didn't execute Phase 5 (run extraction → commit fixtures → open PR). **Mitigation:** Universal principle #2 — deliverable framing + Team Lead pre-flight check verifies STATUS reports against artifact.

### 3. "PASS conditional" deferrals were the actual blockers
HALOT cognates "deferred per Builder Decision J.4" was 100% empty across all entries. **Mitigation:** Universal principle #7 + Topic Director's anti-pattern checks include "any acceptance items silently deferred?"

### 4. Aggregate stats hid sample-level failures
"95.6% HALOT verbs have binyanim" hid 10/12 well-known verbs being mistagged as nouns. **Mitigation:** Universal principle #3 + Director's named-sample selection.

### 5. Wrong-direction stalls
Builder stalled at 600s hand-writing 9,000-entry Strong's→GK lookup table. **Mitigation:** Briefs include "do not do X" guardrails; Director's anti-pattern checks include "is the Researcher heading the wrong direction?"

### 6. Domain knowledge gaps
User-supplied hints (Helena.otf, Mounce anchor, font CMAP) were each key unblocks. **Mitigation:** Universal principle #6 + `docs/domain-knowledge-cache.md` is referenced from every brief.

### 7. Cross-repo branch collision
Two background agents on same branch caused near-conflict. **Mitigation:** Universal principle #8 + cross-repo branch hygiene section.

### 8. Iteration budget exhausted on the wrong problem
Iters 1-4 were design + framework redesign; iter 4 audit revealed core signal missing. **Mitigation:** Topic Director's "scope-shift" signal triggers budget reset.

### 9. Initial Verifier dispatch missed under-extraction
Iter-2 Verifier audited only over-counting. **Mitigation:** Universal principle #4 — every Verifier dispatch is bidirectional.

### 10. Iron Law violations on data extraction
Iter-2 Builder added heuristic patches without root-cause investigation. **Mitigation:** Universal principle #5 — investigation `.md` documents required.

### 11. Team Lead conflated orchestration with substance (this revision)
For most of the session, the Team Lead made substance decisions inline (which defect to fix next, what acceptance bar to apply, when to scope-shift). This created the conditions for failures #1–#10 because the Team Lead's substance reasoning was implicit, not durable, and not separable from orchestration logistics. **Mitigation:** This v3 revision — Topic Director owns substance; Team Lead defers on substance, owns orchestration; the synthesis spine is the connective tissue.

---

## References

- Generic plan: `C:\git\fellwork\agent-team-orchestration-plan.md` (v2.1)
- Phase 1 spec: `docs/superpowers/specs/2026-04-25-phase-1-design.md`
- Translation rubric: `gold/rubric.md`
- Gold corpus: `gold/catalog.json`
- Decoder redesign architecture: `C:\git\fellwork\fellwork-api\docs\decoder-redesign-architecture.md`
- Atext exploration: `C:\git\fellwork\fellwork-api\docs\atext-exploration-report.md`
- Domain knowledge cache: `docs/domain-knowledge-cache.md`
- Program guidance: `program.md`
- **Companion memory files**:
  - `feedback_agent_dispatch_discipline.md` — 10 agent-side patterns
  - `feedback_team_lead_practice.md` — 8 Team-Lead-side commitments
  - `feedback_lexicon_corpus_design.md`, `feedback_token_as_first_class_instance.md`, `feedback_corpus_dimensions.md` — corpus design principles
