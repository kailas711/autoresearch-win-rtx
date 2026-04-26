"""
Walking-skeleton scoring: chrF against gold subset.

Returns a single scalar (lower-is-better, i.e., 1 - chrF) so it slots
cleanly into the autoresearch loop's metric contract.

For the walking skeleton, the gold subset is whatever entries from
gold/catalog.json fall inside Genesis 1-3 (the fixture range).
"""
import json
import os
from pathlib import Path

import sacrebleu

CACHE_DIR_DEFAULT = Path("data/cache/walking_skeleton")
GOLD_CATALOG = Path("gold/catalog.json")


def load_gold_subset() -> dict[str, str]:
    """Return dict ref -> gold English for entries in Gen 1-3."""
    if not GOLD_CATALOG.exists():
        return {}
    catalog = json.loads(GOLD_CATALOG.read_text(encoding="utf-8"))
    out = {}
    for entry in catalog["entries"]:
        ref_start = entry.get("ref_start", "")
        if not (ref_start.startswith("Gen.1") or ref_start.startswith("Gen.2") or ref_start.startswith("Gen.3")):
            continue
        out[ref_start] = entry["translation"]
    return out


def stub_translate(hebrew: str) -> str:
    """Identity stub. Replaced when train_translate wires a real model."""
    return hebrew


def score(model=None, tokenizer=None, *, gold_subset_only: bool = False, cache_dir: Path | None = None) -> float:
    """
    Run translation on the scoring set and return 1 - chrF (lower-better).

    If model/tokenizer are None, uses the stub identity translator -- useful for
    smoke-testing the harness itself.
    """
    cache = cache_dir or Path(os.environ.get("WALKING_SKELETON_CACHE", str(CACHE_DIR_DEFAULT)))
    _ = cache  # cache is reserved for future use; not currently consumed here

    fixtures = Path("data/fixtures/gen_1_3_hebrew.json")
    hebrew_by_ref = json.loads(fixtures.read_text(encoding="utf-8"))

    gold = load_gold_subset()
    if gold_subset_only and not gold:
        # Walking skeleton fallback: use Berean as gold if no real gold found.
        berean = json.loads(Path("data/fixtures/gen_1_3_berean.json").read_text(encoding="utf-8"))
        gold = berean

    refs_to_score = sorted(set(hebrew_by_ref.keys()) & set(gold.keys()))
    if not refs_to_score:
        return 1.0  # worst score; no scoring points

    hypotheses = []
    references = []
    for ref in refs_to_score:
        hebrew = hebrew_by_ref[ref]
        if model is None:
            hyp = stub_translate(hebrew)
        else:
            hyp = generate(model, tokenizer, hebrew)
        hypotheses.append(hyp)
        references.append(gold[ref])

    chrf = sacrebleu.corpus_chrf(hypotheses, [references])
    chrf_normalized = chrf.score / 100.0  # sacrebleu chrF returns 0-100; normalize to 0-1
    return 1.0 - chrf_normalized


def generate(model, tokenizer, hebrew: str, max_new: int = 128) -> str:
    """Greedy decode the english half from the hebrew prefix. Implemented in train_translate."""
    from train_translate import generate_for_scoring
    return generate_for_scoring(model, tokenizer, hebrew, max_new=max_new)


if __name__ == "__main__":
    s = score(gold_subset_only=False)
    print(f"score (1 - chrF): {s:.6f}")
