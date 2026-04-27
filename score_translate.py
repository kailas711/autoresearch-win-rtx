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

GOLD_CATALOG = Path("gold/catalog.json")
CORPUS_CHOICES = ("gen_1_3", "genesis_full")


def corpus_name() -> str:
    name = os.environ.get("WALKING_SKELETON_CORPUS", "gen_1_3")
    if name not in CORPUS_CHOICES:
        raise ValueError(f"Unknown corpus {name!r}; expected one of {CORPUS_CHOICES}")
    return name


def load_gold_subset() -> dict[str, str]:
    """Return dict ref -> gold English for all Genesis entries in the catalog."""
    if not GOLD_CATALOG.exists():
        return {}
    catalog = json.loads(GOLD_CATALOG.read_text(encoding="utf-8"))
    out = {}
    for entry in catalog["entries"]:
        ref_start = entry.get("ref_start", "")
        if not ref_start.startswith("Gen."):
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
    _ = cache_dir  # reserved; not currently consumed

    name = corpus_name()
    fixtures = Path(f"data/fixtures/{name}_hebrew.json")
    hebrew_by_ref = json.loads(fixtures.read_text(encoding="utf-8"))

    gold = load_gold_subset()
    if gold_subset_only and not gold:
        # Fallback: use Berean as gold if no real gold found.
        berean = json.loads(Path(f"data/fixtures/{name}_berean.json").read_text(encoding="utf-8"))
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
