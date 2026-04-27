import json

data = json.load(open('data/fixtures/lex_bdb.json', encoding='utf-8'))

# --- Sub-defect 1: 227 verbs with binyanim=None ---
verbs = [e for e in data if e.get('grammar_normalized') == 'verb']
verbs_no_binyan = [e for e in verbs if not e.get('binyanim')]
print(f"Total verb entries (grammar_normalized='verb'): {len(verbs)}")
print(f"Verb entries with binyanim=None: {len(verbs_no_binyan)}")
print(f"Pass (<=30): {'PASS' if len(verbs_no_binyan) <= 30 else 'FAIL'}")

# --- Sub-defect 1 named sample: qara ---
qara = [e for e in data if e.get('headword_consonantal') == 'קרא']
qara_binyan = [e for e in qara if e.get('grammar_normalized') == 'verb' and e.get('binyanim')]
print(f"\nקרא entries: {len(qara)}")
print(f"קרא verb entries with binyanim: {len(qara_binyan)}")
print(f"Pass (>=1): {'PASS' if qara_binyan else 'FAIL'}")

# --- Sub-defect 2: halak grammar_normalized ---
halak = [e for e in data if e.get('headword_consonantal') == 'הלך']
halak_verb = [e for e in halak if e.get('grammar_normalized') == 'verb']
print(f"\nהלך entries: {len(halak)}")
print(f"  grammar_normalized values: {[e.get('grammar_normalized') for e in halak]}")
print(f"Pass (>=1 entry has grammar_normalized='verb'): {'PASS' if halak_verb else 'FAIL'}")

# --- Sub-defect 3: asah present ---
asah = [e for e in data if e.get('headword_consonantal') == 'עשה']
print(f"\nעשה entries: {len(asah)}")
print(f"(Builder: explicitly address in STATUS -- fixed/source-gap/alternate-spelling)")

# --- Over-extraction regression: non-verbs with binyanim must remain 0 ---
non_verb_with_binyan = [
    e for e in data
    if e.get('grammar_normalized') != 'verb' and e.get('binyanim')
]
print(f"\nNon-verb entries with binyanim: {len(non_verb_with_binyan)}")
print(f"Pass (==0): {'PASS' if len(non_verb_with_binyan) == 0 else 'FAIL'}")

# --- Summary ---
all_pass = (
    len(verbs_no_binyan) <= 30
    and bool(qara_binyan)
    and bool(halak_verb)
    and len(non_verb_with_binyan) == 0
)
print(f"\nOverall: {'PASS' if all_pass else 'FAIL (see above)'}")
