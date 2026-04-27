"""End-to-end walking skeleton tests."""
from pathlib import Path


def test_prepare_translate_produces_outputs(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKING_SKELETON_CACHE", str(tmp_path / "cache"))
    import prepare_translate
    prepare_translate.main()
    cache = tmp_path / "cache"
    assert (cache / "tokenizer.pkl").exists()
    assert (cache / "train.bin").exists()
    assert (cache / "val.bin").exists()
    assert (cache / "train.bin").stat().st_size > 0
    assert (cache / "val.bin").stat().st_size > 0


def test_score_translate_returns_scalar(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKING_SKELETON_CACHE", str(tmp_path / "cache"))
    import prepare_translate
    prepare_translate.main()

    import score_translate
    s = score_translate.score(model=None, tokenizer=None, gold_subset_only=True)
    assert isinstance(s, float)
    assert 0.0 <= s <= 1.0


def test_expand_range_single_and_multi_verse():
    import score_translate
    assert score_translate._expand_range("Gen.1.1", "Gen.1.1") == ["Gen.1.1"]
    assert score_translate._expand_range("Gen.1.3", "Gen.1.5") == ["Gen.1.3", "Gen.1.4", "Gen.1.5"]


def test_load_gold_subset_expands_ranges():
    """Multi-verse catalog entries (ref_start != ref_end) must produce all verse refs."""
    import score_translate
    gold = score_translate.load_gold_subset()
    # The catalog has Gen.1.3 -> Gen.1.5 ('let there be light' block); confirm it's expanded.
    multi = [refs for refs, _ in gold if len(refs) > 1]
    assert multi, "expected at least one multi-verse entry in catalog"
    light_block = next((refs for refs, _ in gold if refs and refs[0] == "Gen.1.3"), None)
    assert light_block == ["Gen.1.3", "Gen.1.4", "Gen.1.5"]


def test_train_translate_smoke(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKING_SKELETON_CACHE", str(tmp_path / "cache"))
    import prepare_translate
    prepare_translate.main()

    import train_translate
    result = train_translate.main(smoke_test=True)
    assert result is not None
    assert "final_loss" in result
    assert "score" in result
    assert result["final_loss"] >= 0.0
    assert isinstance(result["score"], float)
