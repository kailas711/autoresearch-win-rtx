# Autoresearch Team Orchestration — Hebrew/Greek Translation

**Date:** 2026-04-27 (revised; first scaffold 2026-04-26)
**Generic plan:** `C:\git\fellwork\agent-team-orchestration-plan.md` (v2.1)
**Project:** `autoresearch-win-rtx`
**Status:** Operational. Multiple sessions have run across decoder redesign + data quality + lexicon extraction. This doc is **tuned** based on observed agent failure modes, not the initial scaffold.

This document binds the project-agnostic Agent Team Orchestration Plan v2.1 to *this* project's research. It defines roster, checkpoint format, resume protocol, spawn templates, and — critically — the *learned discipline* about how to dispatch agents so they actually deliver instead of producing "PASS conditional" reports with deferred blockers.

**Companion memory file** (read both): `C:\Users\srmcg\.claude\projects\C--git-fellwork-autoresearch-win-rtx\memory\feedback_agent_dispatch_discipline.md` — the 10 recurring failure modes observed in this project, with prevention patterns. Every dispatch in this orchestration honors them.

---

## Research thesis

> The user's gold verses can be translated from the original Hebrew and Greek text — preserving sentence phrasing and intention — despite the compromises every existing English translation makes. Reaching that goal requires *two separate models* (one Hebrew→English, one Koine Greek→English) trained against scholarly lexicons (HALOT, KM, BDB for Hebrew; Thayer, LSJ, BDAG for Greek) and the gold corpus. The end product is a translation model exportable to a Rust API.

This research thesis is the success criterion. "Research complete" means: a trained model per language + rubric metric meeting agreed thresholds + an export path the Rust API can consume.

---

## Project binding (per generic plan §11)

### Linked repositories

| Name | Role | Path | Branch convention | Notes |
|---|---|---|---|---|
| `autoresearch-win-rtx` | **primary-write** (Python, fixtures, training) | `C:\git\fellwork\autoresearch-win-rtx` | `autoresearch/<tag>` for research; `feat/<topic>` for build; `fix/<topic>` for defects; `verify/<topic>` for audit reports | Where experiments run, fixtures live, state files persist |
| `fellwork-api` | **write** (Rust, decoders, CLIs) | `C:\git\fellwork\fellwork-api` | `feat/<topic>` for new features; `fix/<topic>` for defects | Lexicon decoders, OakTree binary parsers. Was originally read-only; this was revised when extractor work proved to require Rust changes (PRs #5–#7 demonstrated need). |

**Cross-repo branch discipline:** When work spans both repos, use *paired branch names* (e.g., `fix/lexicon-data-quality` in fellwork-api and `fix/lexicon-data-quality-fixtures` in autoresearch). Cross-reference PR descriptions explicitly.

### Two parallel research tracks

| Track | Status | Source corpus | Gold | Lexicons | State file |
|---|---|---|---|---|---|
| **Hebrew** | Active | OSHB (ETCBC morphology) + Macula | `gold/catalog.json` (95 entries) | HALOT, KM, BDB | `research-state-hebrew.md` |
| **Greek** | Pending | TBD (SBLGNT or GNT28-T from Accordance Texts) | TBD | Thayer, LSJ, BDAG | `research-state-greek.md` |

Tracks share orchestration scaffolding (this doc + roster + protocol) but iterate independently with separate state files. A session targets exactly one track.

### Lexical authority

Each track names the lexicons whose entries are loaded into the corpus. **Licensing:** user has access rights to all six lexicons. Internal research use is unaffected; if model outputs are eventually published, redistribution of derivative content involving HALOT/BDAG should be reviewed against publisher terms.

### Success criteria (research-complete signal)

A track is "complete" when **all** of:
1. Trained model produces translations on the gold-test holdout set.
2. The `evaluate_translate.py` rubric metric clears the agreed-on threshold.
3. The model artifact is exportable to a Rust runtime.
4. A Scribe-produced handoff doc exists describing the model.

---

## Operating modes — match work shape to roster

The original doc assumed M-scope per-direction sessions (autoresearch experiment loop). Real session experience showed we operate in **three distinct modes**, each with its own roster and discipline. Pick the mode before dispatching.

### Mode 1 — Per-direction research (M-scope, autoresearch loop)

**When:** model training experiments. Tier 1 / Tier 2 area sweeps per `program.md`.
**Roster:** Team Lead + Scout + Builder + Verifier + Historian. Investigator on-demand for crashes.
**Granularity:** one session = one direction; rotate after 3 misses.
**Iteration budget:** 3 misses → rotate.

### Mode 2 — Build / refactor (L-scope)

**When:** building or substantially refactoring infrastructure (decoder framework, ingestion pipelines, schema migrations).
**Roster:** Team Lead + Scout + Architect + Builder + Verifier. Specialists on-demand.
**Granularity:** one session = one component or one phase of a larger plan.
**Iteration budget:** Builder ↔ Verifier cycles. Hard-stop at 5 ping-pong rounds; if not converged, surface to user.

### Mode 3 — Data quality / extraction defect (focused L-scope)

**When:** fixing extraction defects that affect ML signal (binyan extraction, sense graphs, identifier coverage).
**Roster:** Team Lead + Verifier (audit-first) + Builder (investigate-then-fix). Re-dispatched in tight loops.
**Granularity:** one defect class per session if possible; bundle when defects share root cause.
**Iteration budget:** **resets to 0 when the work nature shifts.** A session that started as "implement decoder framework" and pivoted to "fix data quality" gets a fresh budget. Don't grind through 5 iters of polish when 2 iters of focused investigation would close.

---

## Roster (full)

| Role | Filled by | Spawn timing | Output |
|---|---|---|---|
| **Team Lead** | This Claude session | Always | Decomposition, role assignment, safety policy, final handback |
| **Scout** | Subagent (sonnet) | Start of session OR audit-only dispatches | `scout-report.md` or `<topic>-audit.md`: state validation, repo state, do-not-break list, identifier coverage. Read-only. |
| **Architect** | Subagent (sonnet) | Mode 2 only, when design choice is non-trivial | `<topic>-architecture.md`: spec with named interfaces, schema, acceptance criteria, alternatives considered. No code. |
| **Builder** | Subagent (sonnet) | Mid-session | `build-manifest.md`: files changed and why; investigation docs for reverse-engineering work. Commits + pushes. |
| **Verifier** | Subagent (sonnet) | After Builder | `verification-report.md`: pass/fail per concrete acceptance criterion. **Bidirectional** — checks under-extraction AND over-counting. Sample-based not just aggregate. |
| **Investigator** | Subagent (sonnet) | On-demand for crashes/blocks | `investigation-report.md`: root cause; Iron Law applies. |
| **Historian** | Subagent (sonnet) | End of Mode 1 sessions | New `research-state-<track>.md` + `retro.md` |

**Removed roles** (relative to generic plan): Releaser. Autoresearch experiments aren't deployed; final-release sessions are rare and dispatched ad-hoc when needed.

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
| `program.md` | read-only | read-only | read-only — modified only via separate human-approved PRs |
| `docs/`, `pyproject.toml` | read-only | writable on branch | writable on branch |
| `fellwork-api/*` | read-only | writable on its own branch (paired with autoresearch branch) | writable on its own paired branch |

---

## Spawn prompt principles (universal — apply to every dispatch)

These are baked into every template below, but listed here for principle clarity. They prevent the recurring failure modes catalogued in `feedback_agent_dispatch_discipline.md`.

1. **Cite original spec/Architect criteria explicitly.** Never accept agent-revised targets. If the spec says "≤6,001 BDAG entries" and the agent gets 7,400, the right answer is to fix the absorption, not to redefine the target.
2. **Deliverable = data on the branch, not the code.** Builders frequently complete code work without running extraction or pushing fixtures. Make the deliverable explicit: "the JSON file with these acceptance numbers, on this branch, pushed."
3. **Sample-based acceptance > aggregate statistics.** Bake named-sample tests into briefs. "12 well-known Hebrew verbs each have ≥3 binyanim" caught what 95.6% aggregate hid.
4. **Bidirectional audits.** Every Verifier dispatch checks BOTH under-extraction (signal missing) AND over-counting (garbage included). One direction misses the other.
5. **Investigate before fix (Iron Law for data extraction).** Patching detector heuristics without understanding why detection fails produces fragile fixes. Require an investigation `.md` document with hex dumps + samples BEFORE any fix code.
6. **Surface domain unknowns to user, don't guess.** Agents have less biblical/lexicographic knowledge than the user. When uncertain about Hebrew verb structure, BDAG sense markers, Accordance binary format, etc. — the brief should cue the agent to flag the assumption rather than proceed.
7. **No "PASS conditional" with deferrals.** Either it passes the full bar or it doesn't. Deferrals require explicit user judgment, not unilateral choices by the agent.
8. **One branch per concurrent agent.** Two background agents must not share a branch (collisions observed twice). Cross-repo work uses paired-but-distinct branch names.
9. **Read the dispatch-discipline memory before complex tasks.** The `feedback_agent_dispatch_discipline.md` file in user memory is the explicit list of known failure modes — agents should read it for any L-scope or reverse-engineering work.
10. **Define surface conditions explicitly.** When working autonomously, make clear what causes the agent (or Team Lead) to interrupt the user vs continue.

---

## Iteration discipline

### Convergence vs hard-stop

Builder ↔ Verifier loops are expected; first pass rarely clean. **Hard-stop at 5 ping-pong rounds in the same defect class.** If 5 rounds haven't converged, the defect class is harder than scoped — surface to user for re-scoping, don't grind.

### Budget reset on scope shift

If the work fundamentally shifts character (e.g., "implement decoder framework" became "fix HALOT binyan classifier"), the iteration counter resets to 0. **Re-anchor with the user when this happens.** Don't carry over an exhausted budget into a different problem.

### Surface conditions (autonomous mode)

When operating autonomously (user away or has authorized non-stop work), the Team Lead surfaces to the user under any of:

- Verifier reports BLOCKED with no path forward
- 5 iterations on the same defect class fail to converge (hard-stop)
- Cross-repo conflict requiring user judgment
- License/legal question outside prior guidance
- **Substantive audit findings that would change scope** — not just defects to fix, but findings that suggest the work is the wrong shape (e.g., "Phase 0 was deferred entirely" or "97.7% of binyanim missing")
- Token-spend ceiling
- Safety-mode breach

Going quiet between iterations is correct; going quiet through bad iterations to claim completion is not.

---

## Verifier ↔ Builder iteration loop (the cleaning protocol)

For Mode 2 / Mode 3 work, Builder and Verifier iterate **multiple rounds** against concrete acceptance criteria. This is the protocol:

1. **Builder** ships code + fixtures; reports `STATUS: DONE | PARTIAL | BLOCKED` with concrete numbers per acceptance item.
2. **Verifier** dispatches:
   - Pulls Builder's latest branch.
   - Runs extraction if not already run (Builder sometimes ships code without re-running data).
   - Audits against original spec criteria, **bidirectionally** + **sample-based**.
   - Reports `STATUS: PASS | NEEDS_REWORK | BLOCKED` with specific defects + concrete numbers.
3. If `NEEDS_REWORK`: **Builder re-dispatches** with the Verifier's defect list as input. Same Builder agent if context is preserved; new dispatch if not.
4. Repeat 1–3 until `STATUS: PASS`. Hard-stop at 5 rounds.
5. **Team Lead** then merges or surfaces to user, depending on autonomous-mode authorization.

**Anti-patterns the Verifier explicitly checks for:**

- Did the Builder revise targets? (Compare reported numbers to spec, not to Builder's "what's reasonable.")
- Did the Builder ship code without running extraction? (Builder's claim of "passes" is suspect; Verifier reruns.)
- Are there sample-level failures hidden by aggregate statistics? (Run named-sample checks.)
- Were any acceptance items silently deferred? (Walk through the original brief.)

---

## Cross-repo branch hygiene

Lessons from observed near-collisions:

1. **One agent per branch** — never have two concurrent background agents pushing to the same branch. They will conflict on `entry_parser.rs` or similar shared files.
2. **Paired branch naming for cross-repo work** — `fix/<topic>` in fellwork-api ↔ `fix/<topic>-fixtures` in autoresearch (or similar). Lets Team Lead pair them mentally and in PR cross-references.
3. **PR descriptions cross-reference each other** — both PRs should link the other in their description, with merge order called out explicitly.
4. **Merge fellwork-api before autoresearch (when paired)** — the Rust code that produces fixtures should land first. Rolling back one without the other creates inconsistencies.
5. **Audit reports go on `verify/<topic>` branches** in autoresearch, never as PRs unless the user wants a discussion thread on the audit itself. They are reference artifacts.

---

## Session granularity (Mode 1 — research)

**One session = one research direction.** A "direction" is a single area inside a tier (per `program.md`'s Tier 1 / Tier 2 split):

- Tier 1 example: tune `MATRIX_LR` over a sweep until 3 consecutive misses
- Tier 2 example: ablate `WINDOW_PATTERN` variants until 3 consecutive misses

End-of-session triggers:
- 3 consecutive misses → Historian rotates and writes new state
- ≥ 4 hours wall-clock (M-scope ceiling)
- Hard-stop condition fires
- User pause

Expected throughput: **3–5 sessions per overnight run**, ~12–20 experiments per session.

---

## Checkpoint state — both mediums

### `research-state-<track>.md` — single-pointer state

Markdown at repo root, one per track. Updated by Historian at end-of-Mode-1 session. Schema:

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

## Open questions
## Next-session entry point
```

### Git artifacts — full history

The existing `program.md` contract continues:
- Branches: `autoresearch/<tag>` per session-arc
- `results.tsv`: append-only per-experiment row
- `learnings.md`: append-only per-experiment prose entry
- Commits: each kept experiment is one commit

The `research-state-<track>.md` is a *summary* of git artifacts, not a replacement.

---

## Resume protocol (Mode 1)

1. Team Lead reads `research-state-<track>.md` and current branch's `results.tsv` + `learnings.md`.
2. Decides: continue current direction (misses < 3) or rotate.
3. Spawns Pattern B team (Scout + Builder + Verifier) per generic plan §8.
4. Scout validates state file matches actual git state; flags drift.
5. Builder runs experiments; commits each kept improvement.
6. Verifier scores against rubric metric.
7. Investigator on-demand for crashes.
8. End-of-session: Historian rewrites state file + retro.
9. Team Lead reports session summary.

---

## Spawn prompt templates

### Template A — Mode 1 (per-direction research)

Copy-paste below at the start of a Hebrew-track research session. Replace `<DIRECTION>` and `<DESCRIPTION>` from `research-state-hebrew.md`.

```
Create a team of three teammates to advance Hebrew→English autoresearch on
the active direction "<DIRECTION>". Mode 1 per docs/autoresearch-team-orchestration.md.

Repositories in scope:
- autoresearch-win-rtx (primary-write): C:\git\fellwork\autoresearch-win-rtx
  - branch: autoresearch/<tag-from-state-file>
  - writable: train.py, results.tsv, learnings.md
  - read-only: prepare*.py, gold/, evaluate*.py, score*.py, program.md, data/fixtures/
- fellwork-api (read): C:\git\fellwork\fellwork-api  -- reference only

Active state files:
- research-state-hebrew.md
- gold/rubric.md (P1, P3, P4, P6, P8, P10, P12 are highly-automatable patterns)

Universal spawn principles (orchestration §"Spawn prompt principles"):
- Cite original spec/program.md criteria; do not revise targets
- Deliverable = commits + results.tsv + learnings.md on the branch
- Sample-based acceptance for any quality gate
- Bidirectional checks
- Investigate before fix (Iron Law)
- Surface domain unknowns; don't guess

Spawn:
- Scout: validate state file vs reality. Read-only. Output scout-report.md.
- Builder: implement experiments per <DIRECTION>. Each: edit train.py → run → keep/discard → commit if kept → append to TSV+md. Stop at 3 misses or 4h. Produce build-manifest.md.
- Verifier: confirm TSV+md match commits; rerun evaluate_translate.py if available; flag mismatches. Bidirectional (no regressions in unrelated metrics, no missing rows in TSV). Produce verification-report.md.

Safety: Guarded. Frozen scope per orchestration §"Safety mode" Mode 1 column.
Iteration discipline: hard-stop at 3 misses or 5 Builder↔Verifier ping-pongs.
Iron Law: any crash Builder cannot self-fix in one round triggers Investigator. No fixes without root cause.
End of session: Team Lead spawns Historian to rewrite research-state-hebrew.md + retro.md.
```

### Template B — Mode 2 (build / refactor)

```
L-scope build session for <COMPONENT>. Mode 2 per docs/autoresearch-team-orchestration.md.

Repositories in scope:
- <PRIMARY repo + branch>
- <Paired repo + branch> (if cross-repo)

Universal spawn principles apply (read orchestration doc §"Spawn prompt principles" + the user-memory file feedback_agent_dispatch_discipline.md before substantive work).

Phases:
1. Scout: existing landscape, do-not-break list, risk register. Read-only. Output: scout-report.md.
2. Architect: spec.md with named interfaces + acceptance criteria + alternatives considered. No code.
3. Builder: implement per spec. One commit per logical phase. Tests must pass after each commit. Deliverable = the artifact running, not just compiling.
4. Verifier: bidirectional + sample-based audit against spec. Output: verification-report.md with PASS/NEEDS_REWORK/BLOCKED + concrete numbers.

Iteration: Builder ↔ Verifier cycles until PASS or 5-round hard-stop.
Branch hygiene: one agent per branch; paired naming if cross-repo.
End of session: Team Lead reports per-acceptance-item status to user.
```

### Template C — Mode 3 (data-quality defect fix)

```
Focused defect fix session per docs/autoresearch-team-orchestration.md Mode 3.

Defect list: <CONCRETE LIST OF DEFECTS WITH CURRENT vs TARGET METRICS>

Repositories in scope:
- <PRIMARY repo + existing branch from prior PR if available>
- <Paired repo + branch>

Universal spawn principles apply. ALSO read user-memory feedback_agent_dispatch_discipline.md before starting — this file lists the failure modes most relevant to data-quality work (target revision, deferral pattern, sample vs aggregate, Iron Law for data).

Phases:
1. Investigation: write <topic>-investigation.md per defect. Hex dumps, sample entries, root cause. NO code yet.
2. Fix: implement per investigation findings. One commit per defect class. Tests must pass.
3. Re-extract / re-run: produce updated artifact (fixture / data file / output). Push to branch.
4. Self-audit against acceptance criteria BEFORE claiming done.

Acceptance criteria (this dispatch):
| Item | Bar |
| ... | ≥X% / N out of M / etc. |

Iteration budget: resets on scope shift. Hard-stop at 5 rounds same defect class.
Status: DONE only if all acceptance items pass; PARTIAL with explicit list otherwise; BLOCKED with reason.
```

### Template D — Verifier-only (audit dispatch)

```
Verifier-only audit dispatch. Read-only.

Audit target: <BRANCH or PR or directory>
Spec to verify against: <PATH to spec doc — Architect's design or program.md or this orchestration doc>

Universal spawn principles apply. Bidirectional + sample-based + cite original spec.

Method:
1. Pull target branch.
2. For each spec item, measure against actual.
3. Sample-based checks: <NAMED SAMPLE LIST per audit context, e.g., "12 well-known Hebrew verbs", "5 polysemous Greek words">
4. Identifier coverage table (if relevant)
5. Look for under-extraction AND over-counting

Output: <topic>-audit.md committed to verify/<topic> branch. Status: PASS | NEEDS_FIX with bullet list | BLOCKED.

Do NOT modify the audited artifact. Read-only.
```

---

## Open questions (kept here so they don't get forgotten)

1. **Greek gold corpus.** No Greek teaching materials extracted yet. Greek track is gated until either Greek-equivalent PDFs are added to `gold/` and extracted, or the user provides Greek gold translations directly.
2. **Rust export mechanism.** Candle vs Burn vs ONNX vs distilled-rules. Phase 5 decision once a model exists.
3. **Verifier vs `evaluate_translate.py` overlap.** Once `evaluate_translate.py` is the authoritative metric, Verifier's job collapses to "run the script and confirm results.tsv row matches script output."
4. **Plan #6 (corpus assembly) source mix.** Use Sefaria-fetched Hebrew + STEPBible morphology, OR Accordance `MT-ETCBC-A.atext` + `MT-LXX Interlinear.ainter`? Exploration agent recommended `.ainter` + `.agloss` from Accordance + STEPBible morphology. Subject to revision.

---

## Lessons from real sessions (appendix — keep so future sessions don't repeat)

This section documents specific failure patterns observed in actual sessions of this project. Future sessions should treat these as known anti-patterns to avoid.

### 1. Builder declares "PASS" by revising targets

**Observed:** Multiple Builder dispatches reported "PASS conditional" by changing acceptance numbers (BDAG 6,001 → 7,400, BDB 4,457 → 8,800) instead of fixing the absorption / collapsing logic.
**Mitigation:** Universal principle #1 — cite original spec criteria explicitly; Verifier measures against original, not Builder-revised.

### 2. Code-complete shipped without running the extraction

**Observed:** Original Builder for decoder redesign completed phases 1-4 (code + 234 tests pass) but didn't execute Phase 5 (run extraction → commit fixtures → open PR). Status was reported as DONE; reality was code-only.
**Mitigation:** Universal principle #2 — deliverable framing. Briefs say "the fixture file on the branch is the deliverable, not the code change."

### 3. "PASS conditional" deferrals were the actual blockers

**Observed:** HALOT cognates "deferred per Builder Decision J.4" turned out to be 100% empty across all entries. BDAG sense graph "claimed working" was 6/8113 multi-sense. Each deferral was the most important defect.
**Mitigation:** Universal principle #7 — no PASS conditional. Either passes the bar or doesn't.

### 4. Aggregate stats hid sample-level failures

**Observed:** "95.6% HALOT verbs have binyanim" hid the fact that 10/12 well-known verbs (היה, אמר, נתן, etc.) had 0 binyanim — they were silently mistagged as nouns.
**Mitigation:** Universal principle #3 — named-sample acceptance tests in every brief.

### 5. Wrong-direction stalls

**Observed:** A Builder dispatch stalled at 600s while hand-writing a 9,000-entry Strong's→GK Hebrew lookup table when the right approach was to extract from source or use STEPBible TSV. Agent went down a fundamentally wrong path.
**Mitigation:** Briefs include explicit "do not do X" guardrails for known wrong directions. Builder dispatches for identifier work say "do not synthesize hardcoded mapping tables."

### 6. Domain knowledge gaps unblock fast when surfaced

**Observed:** The user supplied Helena.otf font location, Mounce attribution string for KM, multi-binyan structure expectations. Each was a key unblock the agents would not have produced themselves.
**Mitigation:** Universal principle #6 — briefs explicitly say "if uncertain about <domain detail>, surface to user rather than proceeding."

### 7. Cross-repo branch collision

**Observed:** KM v4 agent and fixer agent both pushed to fellwork-api `feat/extract-lexicons-cli`; potential conflict on `entry_parser.rs`. Got lucky — no actual conflict, but design had risk.
**Mitigation:** Universal principle #8 + cross-repo branch hygiene section above.

### 8. Iteration budget exhausted on the wrong problem

**Observed:** Iters 1-4 were design + framework redesign; iter 4 audit revealed core signal was missing. Continuing at iter 5/5 in the same budget would have left no room for the actual data-quality work.
**Mitigation:** Iteration discipline section above — reset budget on scope shift. Surface to user when scope changes.

### 9. Initial Verifier dispatch missed under-extraction

**Observed:** Iter-2 Verifier audited only over-counting (BDAG sub-sense pollution) and missed under-extraction (97.7% HALOT verbs with no binyanim). One direction caught some defects; the other surfaced more.
**Mitigation:** Universal principle #4 — every Verifier dispatch is bidirectional.

### 10. Iron Law violations on data extraction

**Observed:** Iter-2 Builder added heuristic patches to `is_sub_sense_lemma` without understanding why BDAG sense detection was failing. The fix absorbed only 24 entries; the real bug was that circled digits weren't decoded yet (Phase 0 hadn't shipped).
**Mitigation:** Universal principle #5 — investigate before fix. Investigation `.md` documents required for any defect with unclear root cause.

---

## References

- Generic plan: `C:\git\fellwork\agent-team-orchestration-plan.md` (v2.1)
- Phase 1 spec: `docs/superpowers/specs/2026-04-25-phase-1-design.md`
- Translation rubric: `gold/rubric.md`
- Gold corpus: `gold/catalog.json`
- Existing rule pipeline: `C:\git\fellwork\fellwork-api\crates\fw-translate-hebrew`
- Decoder redesign architecture: `C:\git\fellwork\fellwork-api\docs\decoder-redesign-architecture.md`
- Atext exploration: `C:\git\fellwork\fellwork-api\docs\atext-exploration-report.md`
- Program guidance: `program.md`
- **Companion memory**: `C:\Users\srmcg\.claude\projects\C--git-fellwork-autoresearch-win-rtx\memory\feedback_agent_dispatch_discipline.md`
