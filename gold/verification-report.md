# Verification Report

## Sample size: 20 of 53 entries spot-checked

Entries selected to cover every chapter (Gen 1–9), with emphasis on multi-verse spans. All 53 entries were read; 20 were verified in depth.

---

## Strong matches

| Entry | Ref | Notes |
|-------|-----|-------|
| 1 | Gen.1.1 | "In the beginning" — unambiguous. |
| 2 | Gen.1.3–1.5 | Full Day 1 text; all three verses present; "one day" (cardinal) is the distinctive phrasing noted. |
| 3 | Gen.1.6–1.8 | Day 2 expanse block; v6 command, v7 execution, v8 naming + "second day" — all correct. |
| 4 | Gen.1.9–1.10 | Gathering of waters; both verses present; stops correctly before v11. |
| 5 | Gen.1.11–1.12 | Vegetation speech + execution; v13 (day-close formula) correctly excluded. |
| 6 | Gen.1.14–1.15 | Lights speech only; v16 narrative correctly starts the next entry. |
| 7 | Gen.1.16–1.19 | Two lights through "fourth day"; all four verses accounted for despite ellipsis. |
| 8 | Gen.1.26–1.27 | "Let us make man" (v26) + image/creation (v27); range and content exact. |
| 9 | Gen.2.15 | "Caused him to rest…to serve it and keep it" — single verse, exact. |
| 10 | Gen.3.1–3.5 | Full serpent-woman dialogue; all five verses (v1b–v5) present and correct. |
| 11 | Gen.4.5–4.7 | Cain's anger + God's warning about sin "lying at the opening"; all content of v5b–v7 present. |
| 12 | Gen.4.9–4.12 | Divine confrontation through Cain's curse; four verses complete. |
| 13 | Gen.4.13–4.16 | Cain's lament, the mark, and exile to "land of wandering" (Nod); four verses complete. |
| 14 | Gen.4.17–4.22 | Six-verse Cainite genealogy (city, Lamech's wives, Jabal/Jubal/Tubal Cain/Naamah); all present. |
| 15 | Gen.5.21–5.24 | Enoch's entry; all four verses present; "was not, for God took him" is the hallmark phrase. |
| 16 | Gen.6.1–6.4 | Sons of God, nephilim block; all four verses present; distinctive 120-year limit and "renown men." |

---

## Weak / unclear matches

| Entry | Ref | Concern |
|-------|-----|---------|
| Gen.2.4–2.7 | Gen.2.4 start | Technically correct but Gen 2:4 is a split verse in critical scholarship. The translation represents v4b ("In the day the Lord God made…"), omitting v4a ("These are the generations…"). The extraction is defensible — the teaching evidently treats v4b as the start of the new unit — but a reader should know v4a is not rendered here. Low severity. |
| Gen.4.3–4.5 | v5 boundary | Verse 5 is split across two consecutive entries: the first entry (4.3–4.5) captures "But to Cain and his gift he did not pay attention" (v5a), while the next entry (4.5–4.7) opens with "And Cain was very angry. And his face fell" (v5b). This is an intentional pedagogical split at a verse boundary, but the overlap on `Gen.4.5` could cause confusion in automated lookups. Low severity. |

---

## Mismatches

| Entry | Cited ref | Likely correct ref | Evidence |
|-------|-----------|-------------------|---------|
| Gen.4.23 | Gen.4.23–Gen.4.23 | Gen.4.23–Gen.4.24 | The translation includes both the poem (v23: "a man I killed for my wound, and a youth for my hurt") **and** the vengeance boast (v24: "If sevenfold will be avenged for Cain, to Lamech seventy and seven"). Genesis 4:24 is a separate verse in all standard versifications. The `ref_end` should be `Gen.4.24`, not `Gen.4.23`. |

---

## Off-by-one range starts

| Entry | Cited ref | Likely correct start | Evidence |
|-------|-----------|---------------------|---------|
| Gen.2.8–2.14 | Gen.2.8 | Gen.2.9 | Gen 2:8 reads "And the Lord God planted a garden in Eden, to the east, and there he placed the man whom he had formed." This planting/placing action is entirely absent from the translation. The text opens with "The Lord God caused to sprout from the ground all trees…" which is Gen 2:9. The `ref_start` appears to be one verse early. |

---

## Patterns observed

- **Translation style is internally consistent**: This is a highly literal, Hebrew-order-preserving translation (doubled pronouns "she, she"; inverted word order; untranslated Hebrew terms like *tannanim*, *ishah/ish*, *adam*, *toledot*, *nephilim*, *Havah*). This style is distinctive and easily verified against any standard text — there are no cases where the translation could be mistaken for a different passage.
- **All 53 entries span Genesis 1–9 continuously** with no chapter gaps, consistent with a sequential lecture series; no entries from Gen 10–11 despite the metadata stating "Gen 1-11." This is likely because teaching stopped before Gen 10, not an extraction error.
- **Ranges are generally accurate and complete**: Of 20 entries checked, 16 are strong matches, 2 have minor boundary ambiguity (defensible pedagogical splits), 1 has an off-by-one start (Gen 2:8 vs 2:9), and 1 has an incorrect `ref_end` (Gen 4:23 should be 4:23–4:24).
- **Confidence ratings in the JSON are uniformly "high"**: This is accurate for the content matches, but the two structural issues (Gen 2:8 start and Gen 4:23 end) were not flagged by the extractor.
- **No entry maps to the wrong passage entirely**: Zero cases of content belonging to a completely different verse or chapter.

---

## Recommendation

**Trust the extraction with minor corrections.** The content-to-reference matching is reliable across all 20 sampled entries. Two specific fixes are recommended before using this data in any reference system:

1. **Fix `Gen.4.23` entry**: Change `ref_end` from `Gen.4.23` to `Gen.4.24`. The translation demonstrably includes verse 24.
2. **Investigate `Gen.2.8–2.14` entry**: Change `ref_start` from `Gen.2.8` to `Gen.2.9`, or confirm whether the teaching PDF includes a rendering of v8 that was not captured. The current text clearly begins at v9 content.
3. **Document the Gen 2:4 split-verse convention**: No change needed, but add a note that `Gen.2.4` here represents v4b only.
4. **Clarify Gen 4:5 overlap**: The split of verse 5 across two entries is a pedagogical choice, not an error — but downstream tools doing verse-range lookups should be aware of the overlap.

Overall severity: **low**. One confirmed ref_end error (Gen 4:23), one likely ref_start error (Gen 2:8), both in known passages with unambiguous content.
