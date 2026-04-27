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


def _expand_range(ref_start: str, ref_end: str) -> list[str]:
    """Expand a verse range into individual verse refs (intra-chapter only)."""
    s_book, s_chap, s_verse = ref_start.split(".")
    e_book, e_chap, e_verse = ref_end.split(".")
    if (s_book, s_chap) != (e_book, e_chap):
        raise ValueError(f"Cross-chapter ranges not supported: {ref_start}-{ref_end}")
    return [f"{s_book}.{s_chap}.{v}" for v in range(int(s_verse), int(e_verse) + 1)]


def load_gold_subset() -> list[tuple[list[str], str]]:
    """Return [(refs, gold English)] for all Genesis entries in the catalog.

    Each entry's `refs` is the full list of verse references covered by the
    translation -- single-verse entries return a 1-element list; range entries
    (e.g. ref_start=Gen.1.3, ref_end=Gen.1.5) return [Gen.1.3, Gen.1.4, Gen.1.5].
    """
    if not GOLD_CATALOG.exists():
        return []
    catalog = json.loads(GOLD_CATALOG.read_text(encoding="utf-8"))
    out = []
    for entry in catalog["entries"]:
        ref_start = entry.get("ref_start", "")
        if not ref_start.startswith("Gen."):
            continue
        ref_end = entry.get("ref_end") or ref_start
        refs = _expand_range(ref_start, ref_end)
        out.append((refs, entry["translation"]))
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

    gold_pairs = load_gold_subset()
    if gold_subset_only and not gold_pairs:
        # Fallback: use Berean as gold if no real gold found. Berean is single-verse.
        berean = json.loads(Path(f"data/fixtures/{name}_berean.json").read_text(encoding="utf-8"))
        gold_pairs = [([ref], translation) for ref, translation in berean.items()]

    hypotheses = []
    references = []
    for refs, gold_translation in gold_pairs:
        # Skip if any verse in the range is missing from the Hebrew fixture --
        # partial-range scoring would distort chrF since the gold covers all verses.
        if not all(r in hebrew_by_ref for r in refs):
            continue
        hebrew = " ".join(hebrew_by_ref[r] for r in refs)
        if model is None:
            hyp = stub_translate(hebrew)
        else:
            hyp = generate_for_scoring(model, tokenizer, hebrew)
        hypotheses.append(hyp)
        references.append(gold_translation)

    if not hypotheses:
        return 1.0  # worst score; no scoring points

    chrf = sacrebleu.corpus_chrf(hypotheses, [references])
    chrf_normalized = chrf.score / 100.0  # sacrebleu chrF returns 0-100; normalize to 0-1
    return 1.0 - chrf_normalized


def generate_for_scoring(model, tokenizer, hebrew: str, max_new: int = 128) -> str:
    """Greedy decode the english half from the hebrew prefix.

    Lives here (not in train_translate) so train_translate -> score_translate is
    a one-way dependency; otherwise score's generation path imported back into
    train and produced a circular import.
    """
    import torch

    bos = tokenizer.encode_single_token("<|bos|>")
    sep = tokenizer.encode_single_token("<|sep|>")
    eos = tokenizer.encode_single_token("<|eos|>")
    he_ids = tokenizer.encode_ordinary(hebrew)
    ids = [bos] + he_ids + [sep]
    device = next(model.parameters()).device
    cur = torch.tensor(ids, dtype=torch.long, device=device).unsqueeze(0)
    model.train(False)  # inference mode
    with torch.no_grad():
        for _ in range(max_new):
            if cur.size(1) >= model.cfg.block_size:
                break
            logits = model(cur)[:, -1, :]
            next_id = int(logits.argmax(dim=-1).item())
            cur = torch.cat([cur, torch.tensor([[next_id]], device=device)], dim=1)
            if next_id == eos:
                break
    out_ids = cur.squeeze(0).tolist()
    after_sep = out_ids[out_ids.index(sep) + 1:] if sep in out_ids else out_ids
    if eos in after_sep:
        after_sep = after_sep[: after_sep.index(eos)]
    return tokenizer.decode(after_sep)


if __name__ == "__main__":
    s = score(gold_subset_only=False)
    print(f"score (1 - chrF): {s:.6f}")
