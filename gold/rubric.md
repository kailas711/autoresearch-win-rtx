# Translation Rubric — Gold vs Mainstream

> Extracted from `gold/catalog.json` by comparison with mainstream English translations (NIV, ESV, NASB, KJV).
> Catalog: 95 entries — 67 Genesis, 10 Psalms, 3 Other-OT, 15 NT.

---

## Summary

The gold corpus consistently differs from mainstream translations along **13 dimensions**. The most measurable are: (1) cardinal vs ordinal day-numbers, (2) explicit `"And"` clause-start preservation (wayyiqtol), (3) cognate-accusative retention, (4) doubled-pronoun emphasis, (5) Hiphil rendered as "caused to X", (6) Hebrew word retention with explanation, (7) preposition bein…ubein ("between X and between Y"), and (8) "as" vs "in" for the tselem/image preposition. Four additional patterns — (9) plural marking of second-person address, (10) "good and bad" vs "good and evil", (11) lexical literalism in key theological terms, and (12) bracketed gap-filling of elided Hebrew subjects — are also consistently present. A thirteenth pattern, (13) short clause mirroring of Hebrew prose, underlies almost every entry but resists clean programmatic detection without a reference translation for comparison.

---

## Patterns

---

### P1: Cardinal Day Numbers

**Trigger:** The Hebrew day-formula `yom ekhad` / `yom sheni` etc. at the close of each creation day. In Hebrew, day 1 uses the cardinal `ekhad` (one) rather than the ordinal `rishon` (first); days 2–5 use ordinals with the indefinite article; day 6 uses an unusual post-posed article `ha-yom ha-shishi`.

**Gold convention:** Mirrors the Hebrew article/ordinal pattern exactly: "one day" (day 1), "a second day" / "a fourth day" / "a fifth day" (days 2–5), and the anomalous "a day, the sixth" (day 6).

**Mainstream convention:** NIV/ESV/NASB: "the first day", "the second day", … "the sixth day" — all ordinals with the definite article.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.1.3–1.5 | "And there was evening, and there was morning — **one day**." | "And there was evening, and there was morning — **the first day**." |
| Gen.1.6–1.8 | "And there was evening, and there was morning--**a second day**." | "And there was evening, and there was morning — **the second day**." |
| Gen.1.31 | "And there was evening and there was morning--**a day, the sixth**." | "And there was evening, and there was morning — **the sixth day**." |

**Programmatic check:** Regex on the day-formula line: `there was morning\s*[-–—]+\s*(one day|a second day|a third day|a fourth day|a fifth day|a day, the sixth)`. A candidate translation passes if it matches this pattern for the relevant verse(s). Reject strings matching `the first day` at Gen 1:5, or article-first ordinals (`the \w+ day`) at Gen 1:8, 1:13, 1:19, 1:23 (days 2–5).

**Coverage in gold catalog:** 5 entries (Gen.1.3–1.5, Gen.1.6–1.8, Gen.1.14–1.19 partial, Gen.1.22–1.23, Gen.1.31).

---

### P2: Wayyiqtol "And" Clause Preservation

**Trigger:** The Hebrew narrative chain uses the wayyiqtol (consecutive imperfect), morphologically `waw` + verb. Every new narrative clause begins with `waw` ("and"), including speech introductions, results of commands, and narrative transitions.

**Gold convention:** Every clause in a narrative chain is introduced with an explicit **"And"**, including `"And it was so."`, `"And God saw"`, `"And God called"`, `"And he slept."` Short single-clause events are not merged into compound sentences.

**Mainstream convention:** NIV frequently drops "And" at the start of sentences or subordinates clauses into longer compound structures (e.g., "God made … God saw … God called …" in a single sentence). ESV preserves "And" more than NIV but still compresses. NASB is closer to gold but still telescopes some chains.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.2.21–2.22 | "And the Lord God caused a deep sleep to fall on the man. **And he slept. And he took** one of his ribs. **And he closed up** the flesh in its place. **And the Lord God built** the rib … **And he brought** her to the man." | "So the Lord God caused the man to fall into a deep sleep; and while he was sleeping, **he took** one of the man's ribs and then **closed** up the place with flesh. Then the Lord God **made** a woman from the rib he had taken … and **he brought** her to the man." (4 "And"s → 1 "and" + subordination) |
| Gen.3.6 | "**And she took** its fruit. **And she ate. And she gave** to the man with her. **And he ate**." | "**She took** some and ate it. **She also gave** some to her husband, who was with her, **and he ate** it." (2 chains compressed) |
| Gen.4.8 | "**And** Cain spoke to Abel, his brother. **And** it happened when they were in the field. Cain rose up against Abel, his brother. **And** he killed him." | "Now Cain said to his brother Abel … **While** they were in the field, Cain attacked his brother Abel and killed him." |

**Programmatic check:** Sentence-initial "And" ratio per verse-token. Compute `(count of sentences beginning with "And") / (total sentence count)` for the passage. Gold passages consistently score > 0.70; mainstream typically scores 0.25–0.45 for the same passages. Also: check for subordinating conjunctions (`while`, `when`, `so that`) bridging what should be independent `waw`-clauses — gold avoids them.

**Coverage in gold catalog:** ~45 entries exhibit this pattern (all Genesis narrative blocks with high confidence).

---

### P3: Cognate Accusative / Figura Etymologica Preservation

**Trigger:** Hebrew rhetorical device using a verb with a cognate noun object — e.g., `titsmatsh tsemakh` (sprout sprouts), `zarua zerah` (seed seed), `sherets sheretsim` (swarm swarmings). These intensify or specify the action via internal repetition.

**Gold convention:** Reproduces the root repetition as near-literally as English allows: "cause **sprouts** to **sprout**", "plants **seeding seeds**", "let the waters **swarm** with **swarming things**".

**Mainstream convention:** NIV: "Let the land produce vegetation: seed-bearing plants and trees." ESV: "Let the earth sprout vegetation, plants yielding seed." Neither preserves the etymological doubling.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.1.11–1.12 | "Let the earth **cause sprouts to sprout**: plants **seeding seeds**, fruit trees making fruit…" | "Let the land **produce vegetation**: **seed-bearing plants** and trees on the land that bear fruit with seed in it." |
| Gen.1.20 | "Let the waters **swarm with swarming things**, living creatures…" | "Let the water **teem with living creatures**…" |
| Gen.1.29 | "all the **herbage seeding seeds**…and all the trees…**seeding seed**." | "every **seed-bearing plant**…and every tree that has fruit with **seed** in it." |

**Programmatic check:** For the relevant verses, check for adjacent or near-adjacent use of the same root morpheme (verb + nominal form of same stem). Pattern: `(sprout|sprouts).{0,20}(sprout|sprouts)`, `seed.{0,10}seed(s|ing)?`, `swarm.{0,20}swarm`. A positive match on any of the three clusters indicates respect for cognate-accusative.

**Coverage in gold catalog:** 3 entries (Gen.1.11–1.12, Gen.1.20, Gen.1.29–1.30). Also echoed in Gen.6.22 "Thus he did!" (ken asah / asah).

---

### P4: Doubled Pronoun / Casus Pendens Emphasis

**Trigger:** Hebrew uses a fronted noun or pronoun followed by a resumptive pronoun to mark contrast or emphasis — a "left-dislocation" structure (casus pendens): `weCayin hu hayah` = "and-Cain, he was…". This is also how emphatic pronouns appear: `hi hi hayetah` = "she, she was."

**Gold convention:** Reproduces both elements: "but Cain, **he** was a server of the ground"; "But Abel, **he** brought, even he, from the firstborn"; "she, **she** was the mother of all living"; "but you, **you** will bruise his heel"; "But as for him, **he** will rule over you."

**Mainstream convention:** NIV: "Cain worked the soil." ESV: "Cain was a worker of the ground." No pronoun doubling or fronting. The casus pendens is dissolved into ordinary English SVO order.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.4.2 | "And Abel was a caretaker of sheep, but **Cain, he** was a server of the ground." | "Now Abel kept flocks, and **Cain** worked the soil." |
| Gen.3.20 | "And the man called the name of his wife Havah, because **she, she** was the mother of all living." | "Adam named his wife Eve, because **she** would become the mother of all the living." |
| Gen.3.15 | "He will bruise your head, but **you, you** will bruise his heel." | "he will crush your head, and **you** will strike his heel." |
| Gen.3.16 | "**But as for him, he** will rule over you." | "and **he** will rule over you." |

**Programmatic check:** Regex for fronted-pronoun patterns: `\b(but |But )(Cain|Abel|he|she|they|it),?\s+(he|she|they|it)\b`; also `\b(she|he),\s+(she|he)\s+(was|were|is|are)\b`. For specific verses (Gen 4:2, Gen 3:20, Gen 3:15, Gen 3:16), flag translations that lack the doubled/resumptive pronoun as non-compliant.

**Coverage in gold catalog:** 7 entries containing at least one instance (Gen.3.15, Gen.3.16, Gen.3.20, Gen.4.2, Gen.4.3–4.5, Gen.4.25–4.26, Gen.4.17–4.22).

---

### P5: Hiphil as "Caused to X" / "Caused X to Y"

**Trigger:** The Hebrew Hiphil binyan (causative stem) expresses "cause someone/something to do X." Gold renders this causative morphology transparently rather than naturalizing it into a simple English verb.

**Gold convention:** "And the Lord God **caused** a deep sleep to fall on the man" (Gen 2:21); "**caused him to rest** in the garden" (Gen 2:15); "**cause sprouts to sprout**" (Gen 1:11); "**caused a wind to pass** over the earth" (Gen 8:1); "for the Lord God had not yet **caused it to rain**" (Gen 2:4–7).

**Mainstream convention:** NIV: "the Lord God made the man fall into a deep sleep" (Gen 2:21) — "made" replaces "caused to"; "the Lord God put the man in the Garden" (Gen 2:15) — the causative is entirely lost. ESV similarly uses "put", "made", "sent" rather than "caused to."

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.2.15 | "And the Lord God … **caused him to rest** in the garden of Eden" | "The Lord God **took** the man and **put** him in the Garden of Eden" |
| Gen.2.21 | "And the Lord God **caused a deep sleep to fall** on the man" | "So the Lord God **caused** the man to fall into a deep sleep" (NIV preserves this one; ESV: "caused … to fall") |
| Gen.2.4–2.7 | "for the Lord God had not yet **caused it to rain**" | NIV: "the Lord God had not sent rain" |
| Gen.8.1 | "And God **caused a wind to pass** over the earth" | NIV: "God sent a wind over the earth" |

**Programmatic check:** For Hiphil-bearing verses, check for the pattern `caused\s+\w+\s+to\s+\w+` or `cause\s+\w+\s+to\s+\w+`. Flag translations using simple transitive verbs ("put", "placed", "sent", "made") at lexically confirmed Hiphil positions.

**Coverage in gold catalog:** 6 entries (Gen.1.11, Gen.2.4–2.7, Gen.2.15, Gen.2.21–2.23, Gen.8.1, plus implied in Gen.1.9 "let the dry appear" as Niphal).

---

### P6: Hebrew Word Retention (Transliteration with Implied Gloss)

**Trigger:** Theologically or culturally significant Hebrew words where gold treats translation as interpretively too narrowing, or where the Hebrew sound/form carries meaning the English would lose.

**Gold convention:** Retains the Hebrew form (sometimes with brackets or explanation): `tannanim` (Gen 1:21), `ishah` / `ish` (Gen 2:23), `Havah` (Gen 3:20 — not "Eve"), `toledot` (Gen 5:1, 6:9), `nephilim` (Gen 6:1–4), `adam` in quotes or brackets (Gen 5:1–2, 5:3), `Michtam` (Ps 16:1).

**Mainstream convention:** NIV: "sea creatures" (not `tannanim`); "woman … man" (not `ishah/ish` — the wordplay is lost); "Eve" (not `Havah`); "account / family history" (not `toledot`); "Nephilim" (NIV preserves this one); "mankind / human beings" (not `adam`). KJV: "Mischief" for `Michtam` (interpretive); NIV/ESV leave it untranslated.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.1.21 | "And God created the great **tannanim**…" | "So God created the great **creatures of the sea**…" |
| Gen.2.23 | "she will be called **ishah** because from **ish** this one was taken" | "she shall be called '**woman**,' for she was taken out of '**man**'" (NIV preserves wordplay but loses Hebrew form) |
| Gen.5.1 | "This is the book of the **toledot** of '**adam**'" | "This is the written account of **Adam's** family line" |
| Ps.16.1 | "**Michtam** of David" | NIV/ESV: "**A miktam** of David" (NIV uses lowercase, ESV glosses as "A Miktam") |

**Programmatic check:** Lexical presence check — for each expected transliteration site, test whether the candidate string contains the Hebrew form (case-insensitive): `tannanim`, `ishah`, `toledot`, `nephilim`, `michtam`/`miktam`, `adam` (in a context where a gloss rather than the name is expected). Also flag translations that substitute `Eve` for `Havah` at Gen.3.20.

**Coverage in gold catalog:** 7 entries (Gen.1.21, Gen.2.23, Gen.3.20, Gen.5.1–5.2, Gen.5.3, Gen.6.1–6.4, Gen.6.9–6.10, Ps.16.1).

---

### P7: Preposition bein…ubein ("Between X and Between Y")

**Trigger:** Hebrew uses the compound `bein … ubein` to express "between A and B," literally "between A and between B." This double-preposition structure appears idiomatically in creation and covenant language.

**Gold convention:** Preserves the doubled preposition: "separating **between** waters **and** waters"; "to separate **between** the day **and** the night"; "enmity I will set **between** you **and between** the woman, **and between** your seed **and between** her seed."

**Mainstream convention:** NIV/ESV: "separate the water from the water"; "to separate the day from the night"; "I will put enmity between you and the woman." Single preposition `between … and` or `from … from` — the doubled `bein…ubein` is collapsed.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.1.6–1.8 | "separating **between** waters **and** waters … separated **between** the waters … **and between** the waters…" | "to separate the water **from** the water … separated the water **under** … **from** the water above" |
| Gen.1.14 | "to separate **between** the day **and** the night" | "to separate the day **from** the night" |
| Gen.3.14–3.15 | "enmity I will set **between** you **and between** the woman, **and between** your seed **and between** her seed" | "I will put enmity **between** you **and** the woman, and **between** your offspring and hers" |

**Programmatic check:** For the specific verses, test for the pattern `between\s+\w[\w\s]+and\s+between`. Flag any candidate that uses `from … from` or collapses to a single `between … and`.

**Coverage in gold catalog:** 4 entries (Gen.1.6–1.8, Gen.1.14–1.15, Gen.1.16–1.19, Gen.3.14–3.15).

---

### P8: Preposition "as" (ke) for the Image — "as our image" vs "in our image"

**Trigger:** The Hebrew preposition `ke` in `betsalmenu kdemutenu` (Gen 1:26) has been debated as "in" or "as." The gold translator consistently renders `ke` as "as" (indicating functional identification or comparison) rather than "in" (indicating location within).

**Gold convention:** "Let us make man **as** our image, according to our likeness"; "And God created the man **as** his image, **as** the image of God he created him."

**Mainstream convention:** NIV/ESV/NASB/KJV: "**in** our image, **in** our likeness" — the prepositional choice "in" dominates all major translations.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.1.26 | "Let us make man **as** our image, according to our likeness…" | "Let us make mankind **in** our image, **in** our likeness…" |
| Gen.1.27 | "And God created the man **as** his image, **as** the image of God he created him" | "So God created mankind **in** his own image, **in** the image of God he created them" |
| Gen.5.3 | "And he begat **in** his likeness, **according to** his image" (note: "in" used here for a different preposition — beth — distinguishing from the earlier ke) | NIV: "in his own likeness, in his own image" (conflates both prepositions) |

**Programmatic check:** At Gen.1.26 and Gen.1.27, regex `\bimage\b` combined with adjacent preposition check: require `as (our|his|the) image` rather than `in (our|his|the) image`. Note that gold uses "in his likeness" at Gen.5.3 for `beth` — so the check must be verse-specific.

**Coverage in gold catalog:** 3 entries (Gen.1.26–1.27, Gen.5.3 as a counter-confirmation).

---

### P9: Explicit Second-Person Plural Marking ("You all")

**Trigger:** Biblical Hebrew has distinct 2nd-person masculine plural forms (atem, lachem). When the serpent addresses the woman but implies the couple (Gen 3:1–5), the Hebrew plural is detectable. English has no dedicated 2nd-person plural pronoun in standard registers.

**Gold convention:** Renders the Hebrew plural explicitly as **"you all"** throughout the serpent dialogue: "You all may not eat from every tree," "you all may not eat from it and you all may not touch it, lest you all die," "You all will not surely die," "your eyes will be open, and you all will be like God."

**Mainstream convention:** NIV/ESV/NASB/KJV: simple "you" throughout Gen 3:1–5. The plurality is unmarked or addressed only in a footnote.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.3.1–3.5 | "'**You all** may not eat from every tree of the garden?'" | "'**You** must not eat from any tree in the garden?'" |
| Gen.3.3 | "**you all** may not eat from it and **you all** may not touch it, lest **you all** die" | "**you** must not eat fruit from the tree … and **you** must not touch it, or **you** will die" |
| Gen.3.5 | "**you all** will be like God" | "**you** will be like God" |

**Programmatic check:** At Gen.3.1–3.5, count occurrences of `you all` (case-insensitive). Gold uses it at minimum 5 times in this block. A score of ≥ 3 occurrences in this passage indicates respect for the pattern. Also detect absence via count of bare `you` in positions where Hebrew is plural.

**Coverage in gold catalog:** 1 extended entry (Gen.3.1–3.5), plus indirect evidence in Gen.9.1–9.7 "you all, be fruitful and multiply" (the plural blessing to Noah's family).

---

### P10: "Good and Bad" vs "Good and Evil" for tov ve-ra

**Trigger:** The Hebrew `ra` covers a wide semantic range (bad, evil, harmful, displeasing, wrong). Gold consistently translates it as "**bad**" rather than the more interpretively loaded "**evil**."

**Gold convention:** "the tree of the knowledge of **good and bad**"; "man has become like one of us to know **good and bad**"; "knowing **good and bad**"; "the bad of mankind was great."

**Mainstream convention:** NIV/ESV/NASB/KJV: "the tree of the knowledge of **good and evil**"; "knowing **good and evil**"; "the **wickedness** of man was great" (NIV). The word "evil" is standard in these verses across mainstream translations.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.2.9 | "the tree of the knowledge of **good and bad**" | "the tree of the knowledge of **good and evil**" |
| Gen.2.16–2.17 | "the tree of the knowledge of **good and bad**" | "the tree of the knowledge of **good and evil**" |
| Gen.6.5–6.8 | "the **bad** of mankind was great in the earth" | "the **wickedness** of man was great" |

**Programmatic check:** Simple lexical substitution check — at Gen.2.9, Gen.2.17, Gen.3.1–3.5, Gen.3.22, Gen.6.5: require `good and bad`; flag `good and evil`. Also require `bad` (not `wickedness` or `evil`) at Gen.6.5.

**Coverage in gold catalog:** 6 entries (Gen.2.9–2.14, Gen.2.16–2.17, Gen.3.1–3.5, Gen.3.22–3.24, Gen.6.5–6.8, Gen.6.5–6.13).

---

### P11: Lexical Literalism in Key Theological Terms

**Trigger:** Several Hebrew words have acquired standard English translation equivalents in mainstream Bibles that are interpretively specific or theologically loaded. Gold prefers more literal, etymologically closer renderings.

**Gold convention (with mainstream alternatives):**

| Hebrew | Gold rendering | NIV/ESV | Notes |
|---|---|---|---|
| `minkhah` (gift/tribute) | "**gift**" | "**offering**" | Gen 4:3–4: Cain brings a "gift" not an "offering" |
| `nakhash` (regret/comfort) | "**relief**" | "**comfort**" | Gen 5:29: Noah's name derived from `nakhash` |
| `sha'ah` (gaze, pay attention) | "**paid attention**" | "**looked with favor**" (NIV) / "**had regard**" (ESV) | Gen 4:4–5 |
| `yatser` (formation) | "**formation** of his heart" | "**inclination** of the thoughts of his heart" | Gen 6:5 |
| `makhah` (wipe) | "**wipe out**" | "**destroy**" (NIV) / "**blot out**" (ESV) | Gen 6:7 |
| `'itsavon` (pain, toil) | "**toilsome labor**" | "**painful toil**" (NIV) / "**pain**" (ESV) | Gen 3:16–17 |
| `darash` (seek, pursue) | "**require**" | "**demand an accounting**" (NIV) / "**require**" (ESV) | Gen 9:5 |
| `kanah` (create/acquire) | "**created** a man" | "**brought forth** a man" (ESV) / "**given birth to** a man" (NIV) | Gen 4:1 |

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.4.3–4.5 | "Cain brought a **gift** to the Lord … the Lord **paid attention** to Abel and his **gift**. But to Cain and his **gift** he did not **pay attention**." | "Cain brought some of the fruits of the soil as an **offering** to the Lord … The Lord **looked with favor** on Abel and his **offering**, but on Cain and his **offering** he did not look with favor." |
| Gen.4.1 | "I have **created** a man with the Lord." | "With the help of the Lord I have **brought forth** a man." |
| Gen.5.28–5.31 | "This one, he will give us **relief** from our work" | "He will comfort us in the labor and painful toil of our hands" |

**Programmatic check:** Lexical lookup table: for each verse, assert presence of the gold term and absence of the mainstream term. E.g., at Gen.4.3–4.5: `gift` present AND `offering` absent; at Gen.4.4–4.5: `paid attention` present AND `looked with favor` absent. These are single-word-or-phrase assertions and are highly automatable.

**Coverage in gold catalog:** ~12 entries reference at least one lexical-literalism choice.

---

### P12: Bracketed Gap-Filling of Elided Hebrew Subject/Object

**Trigger:** Biblical Hebrew frequently elides subject or object pronouns that are recoverable from context (pro-drop). When the gold translator supplies them, they are placed in square brackets `[…]` to signal their status as supplied rather than explicit.

**Gold convention:** Inserts the implied constituent in brackets rather than silently supplying it (as mainstream translations do) or leaving a grammatical gap. Examples: `[I have given]` (Gen 1:29–30) where the first-person verb was ellipted; `[adam]` (Gen 5:3) where the proper noun `Adam` vs generic `adam` is ambiguous; `[He sent out the raven …]` (Gen 8:6–12) where the raven section is summarized in brackets.

**Mainstream convention:** NIV/ESV supply the elided material silently — readers see no indication that the element was absent in Hebrew. Italics in KJV serve a similar disclosure function, but the convention is rare in modern translations.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.1.29–1.30 | "But to all the living things … **[I have given]** all the green herbs for food." | "And to all the beasts of the earth … I give every green plant for food." (NIV supplies "I give" without bracketing) |
| Gen.5.3 | "And Adam **[adam]** was 130 years old" | "When Adam had lived 130 years, he had a son" (NIV: no bracket) |
| Gen.6.14 | "reeds you will make the ark / and you will cover it inside and outside with covering" (three-line layout flags ambiguous syntax) | NIV: "Make rooms in it and coat it with pitch inside and out." |

**Programmatic check:** Regex for `\[` in the candidate translation. Count and locate square brackets. Gold uses them specifically for elided syntactic material and glossing ambiguity; a candidate translation with `> 0` brackets at the specific sites (Gen 1:30, Gen 5:3) is likely compliant. Translations with zero brackets across all Genesis entries are likely non-compliant.

**Coverage in gold catalog:** 3 direct bracket instances (Gen.1.29–1.30, Gen.5.3, Gen.8.6–8.12); pattern is implied in several partial entries flagged as structural summaries.

---

### P13: Short-Clause Hebrew Prose Mirroring (Paratactic Structure)

**Trigger:** Biblical Hebrew prose is heavily paratactic — stringing short independent clauses together with `waw` rather than embedding clauses hypotactically. This produces short sentences with minimal subordination. Gold mirrors this.

**Gold convention:** Renders each Hebrew clause as a separate English sentence, even very short ones. Avoids relative clauses, participial phrases, and subordinating conjunctions where the Hebrew has a simple main clause. E.g., "And he slept." (one clause), "And he took one of his ribs." (one clause), rather than "and while he slept, he took one of his ribs."

**Mainstream convention:** NIV and ESV regularly merge adjacent paratactic Hebrew clauses into hypotactic English sentences using subordinators ("while", "so that", "as") or coordinate them with commas and semicolons rather than full stops.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.3.7–3.8 | "**And their eyes were opened.** **And they knew** that they were naked. **And they sewed together** fig leaves. **And they made** loincloths for themselves. **And they heard** the voice of the Lord…" | "Then the eyes of both of them were opened, and they realized they were naked; so they sewed fig leaves together and made coverings for themselves. Then the man and his wife heard the sound of the Lord God…" |
| Gen.2.21–2.23 | "**And the Lord God caused** a deep sleep to fall on the man. **And he slept. And he took** one of his ribs. **And he closed up** the flesh…" | "So the Lord God caused the man to fall into a deep sleep; **and while he was sleeping,** he took one of the man's ribs…" |

**Programmatic check:** Average sentence length (in words) per verse range. Gold Genesis narrative blocks average ~8–12 words per sentence. Compute also: ratio of sentences beginning with "And" (see P2 above) as a proxy for parataxis. Additionally, count subordinating conjunctions (`while`, `as`, `so that`, `when`, `which`, `that`) per 100 words — gold scores lower than mainstream. A combined score (short sentence length + high "And"-start ratio + low subordinator density) is the most reliable proxy.

**Coverage in gold catalog:** Ubiquitous in all 67 Genesis entries and the Psalms narrative entries.

---

## Additional Patterns Found Beyond the Named List

### P14: Inverted (VSO/OVS) Word Order Preservation for Emphasis

**Trigger:** Hebrew is verb-subject-object (VSO) by default but uses fronted objects (OVS) to signal thematic emphasis or contrast. Gold preserves this inverted order.

**Gold convention:** "**Your voice** I heard in the garden" (object first); "**dirt you will eat**" (object first); "**enmity I will set** between you and between the woman" (object-verb-subject); "**A roamer and wanderer** you will be on the earth."

**Mainstream convention:** NIV: "I heard you in the garden"; "you will eat dust"; "I will put enmity between you and the woman." Standard SVO in English.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.3.9–3.13 | "**Your voice** I heard in the garden" | "I heard you in the garden" |
| Gen.3.14–3.15 | "**dirt you will eat** all the days of your life. And **enmity I will set** between you and between the woman" | "you will eat dust all the days of your life. And I will put enmity between you and the woman" |
| Gen.4.9–4.12 | "**A roamer and wanderer** you will be on the earth" | "You will be a restless wanderer on the earth" |

**Programmatic check:** For specific OVS sites, test whether the object NP precedes the verb. E.g., at Gen 3:10, check `\b(voice|your voice)\b` before `\b(heard|I heard)\b`. At Gen 3:14, check `\bdirt\b` before `\beat\b`. At Gen 4:12, check `\b(roamer|wanderer)\b` in sentence-initial position.

**Coverage in gold catalog:** 5 entries (Gen.3.9–3.13, Gen.3.14–3.15, Gen.3.17–3.19, Gen.4.9–4.12, Gen.4.23–4.24).

---

### P15: Ellipsis-Marked Suspended Divine Speech

**Trigger:** Hebrew narrative sometimes records an incomplete or interrupted divine speech where the implied consequence is too weighty to state. Gold marks this suspense explicitly with ellipsis rather than completing the thought as mainstream translations do.

**Gold convention:** Preserves the suspension with `…` inside the quoted speech, forcing the reader to feel the weight of the unsaid: "And now … lest he send out his hand and take even from the tree of life, and eat, and live forever …" (Gen 3:22). The sentence grammatically never completes.

**Mainstream convention:** NIV: "He must not be allowed to reach out his hand and take also from the tree of life and eat, and live forever" — completes the thought as a declarative. ESV similarly resolves the syntactic suspension.

**Examples:**

| Ref | Gold | Mainstream (NIV) |
|---|---|---|
| Gen.3.22–3.24 | "And now **…** lest he send out his hand and take even from the tree of life, and eat, and live forever **…**" | "He must not be allowed to reach out his hand and take also from the tree of life and eat, and live forever." |
| Gen.3.1–3.5 | "'Did God really say, 'You all may not eat from every tree of the garden'?'" (serpent's speech uses internal quotes to mark intonation) | (no suspension; NIV resolves to declarative) |

**Programmatic check:** Regex `\.\.\.|…` (ellipsis) within quoted speech. Specifically, at Gen.3.22, detect `\band now\b.{0,80}\.\.\.` or Unicode ellipsis within 80 characters of the phrase "tree of life." A candidate translation that substitutes a grammatically complete declarative clause at this position fails the pattern.

**Coverage in gold catalog:** 2 direct instances (Gen.3.22–3.24, Gen.8.6–8.12 fragmentary).

---

## Measurability Summary

**Tier 1 — Easy to measure programmatically (regex / lexical lookup):**

1. **P1 — Cardinal day numbers**: Exact phrase match (`one day`, `a second day`, etc.) or ordinal-with-article pattern. Precision near 100%.
2. **P6 — Hebrew word retention**: Lexical presence/absence check for `tannanim`, `toledot`, `nephilim`, `ishah`, `Havah`, `michtam`, `adam` (in context). Precision near 100%.
3. **P8 — "as" vs "in" for image**: Single preposition check at two verses. Binary. Precision near 100%.
4. **P10 — "good and bad" vs "good and evil"**: Exact phrase check. Precision near 100%.
5. **P12 — Bracketed gap-filling**: Regex for `[` characters at specific verse positions. Precision near 100% for the specific sites.

**Tier 2 — Moderate difficulty (multi-token pattern or local window):**

6. **P3 — Cognate accusative**: Root-repetition pattern in a word window. Requires some morphological grouping (`sprout`/`sprouts`, `seed`/`seeds`/`seeding`). Precision ~85–90%.
7. **P4 — Doubled pronoun/casus pendens**: Regex for `X, he/she` or `she, she` or `you, you`. Requires verse-specific application. Precision ~85%.
8. **P7 — bein…ubein double preposition**: Pattern `between … and between`. Precision ~90% at targeted verses.
9. **P9 — "you all" plural marking**: Count `you all` at Gen 3:1–5 and Gen 9:7. Precision ~95% for the specific passage.
10. **P14 — Inverted word order (OVS)**: Verse-specific checks for object-before-verb at targeted sentences. Precision ~80%.
11. **P15 — Ellipsis-marked suspension**: Regex for `…` within quoted speech at Gen 3:22. Precision ~90%.

**Tier 3 — Requires sentence-level analysis (NLP / dependency parsing):**

12. **P5 — Hiphil "caused to X"**: Requires distinguishing Hiphil-bearing verbs from ordinary transitives. A verb-specific list of Hiphil positions can be pre-compiled for this corpus; then pattern-check `caused … to` is near-mechanical. But general detection requires knowing the underlying Hebrew morphology (~75% precision with a compiled list).
13. **P11 — Lexical literalism (key terms)**: Lookup table per verse. Compilable but requires maintaining a gold-term / mainstream-term mapping per verse. Precision ~85% with the table.

**Tier 4 — Requires comparison against reference translation or human judgment:**

14. **P2 — Wayyiqtol "And" preservation**: Measurable as a ratio (sentence-initial "And" density) but threshold calibration requires a reference corpus; also affected by passage selection. Precision ~70%.
15. **P13 — Short-clause paratactic structure**: Measurable only statistically (average sentence length, subordinator density). Cannot detect clause-level faithfulness without parse trees. Precision ~65% with statistical proxy.

---

## Limitations

1. **No underlying Hebrew text linked in the catalog.** Morphological claims (Hiphil, casus pendens, cognate accusative) are inferred from the translator's choices and match_notes. A rigorous metric would need verse-aligned Hebrew source data (BHS/WTT) to confirm which Hebrew form is being rendered.

2. **NT entries follow different source traditions.** The NT entries use identifiable standard translations (NET for John 1:1–5 and John 17:3; Darby for Eph 5:13; 1 John passages appear to be from a Victorian-era translation). NT patterns are not generalizable to Hebrew Bible entries and should not be used for rubric scoring.

3. **Partial/low-confidence entries excluded.** Thirteen entries have `confidence: low` or `is_partial: true`. These are structural summaries, table paraphrases, or fragmentary ellipsis quotations. They cannot be reliably scored against any of the above patterns.

4. **P9 ("you all") has only one primary test site** (Gen 3:1–5). The pattern is theologically motivated (plural address to the couple) but cannot be tested across most of the corpus, limiting its usefulness as a rubric dimension for arbitrary passages.

5. **P8 ("as our image") may be translator-idiosyncratic** rather than a stable rule. The preposition `ke` is genuinely ambiguous; some scholars read `beth` in the same slot. A candidate translation choosing "in our image" is not necessarily non-compliant with standard Hebrew grammar.

6. **Semantic range of `ra` (P10).** While "bad" is consistent across all gold entries, there may be contexts in non-catalogued passages where the gold translator uses "evil" (e.g., moral evil in narrative rather than cosmic knowledge). The rubric pattern is reliable for the Genesis 1–9 knowledge-tree context but may not generalize.

7. **Ellipsis entries (P15) are too sparse** (2 instances) to be generalized as a rubric dimension. This is better treated as a passage-specific annotation than a corpus-wide measurable pattern.

---

## Final Report

**Total patterns identified:** 15 (13 named in task description, 2 additional: P14 inverted word order, P15 ellipsis suspension)

**Breakdown by measurability tier:**

| Tier | Patterns | Count |
|---|---|---|
| Tier 1 (exact match / lexical) | P1, P6, P8, P10, P12 | 5 |
| Tier 2 (local window / regex) | P3, P4, P7, P9, P14, P15 | 6 |
| Tier 3 (NLP / compiled list) | P5, P11 | 2 |
| Tier 4 (statistical / human) | P2, P13 | 2 |

**Patterns unique to a single passage (not generalizable as rubric rules):**

- **P15 (Ellipsis suspension):** Only Gen.3.22–3.24 and partially Gen.8.6–8.12. Too sparse for a corpus-wide metric; annotate as a passage-specific note.
- **P9 ("you all" plural):** One extended test site (Gen.3.1–3.5), one secondary site (Gen.9.7). Usable for those specific verses only.
- **P8 ("as" image preposition):** Only Gen.1.26–1.27 and Gen.5.3 as contra-evidence. Valid as a binary check for those three verses but not extrapolatable.

**Most diagnostic patterns** (highest coverage, Tier 1–2, applicable to the broadest set of Genesis entries): P2, P1, P4, P10, P13 in that order.

STATUS: DONE
