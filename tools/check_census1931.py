"""Check plsim/data/census1931_powiaty.csv: every row's languages add up to its total."""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

COLS = ["pl", "uk", "rue", "be", "ru", "cs", "lt", "de", "yi", "he", "oth", "pls", "unk"]


def rows(path="plsim/data/census1931_powiaty.csv"):
    with open(path, encoding="utf-8") as fh:
        yield from csv.DictReader(l for l in fh if not l.startswith("#"))


if __name__ == "__main__":
    bad = 0
    for r in rows(*sys.argv[1:]):
        rel = [r.get(c) for c in ("rc", "gc", "or", "ev", "jw", "orel")]
        if any(rel) and abs(sum(int(x or 0) for x in rel) - int(r["pop"])) > 0.005 * int(r["pop"]):
            print(f"{r['county']} ({r['source']}): religions {sum(int(x or 0) for x in rel)} vs total {r['pop']}")
        s = sum(int(r[c] or 0) for c in COLS)
        if s != int(r["pop"]):
            bad += 1
            print(f"{r['county']} ({r['source']}): languages {s} != total {r['pop']} (diff {s - int(r['pop'])})")
    print("all rows add up" if not bad else f"{bad} rows do not add up")
    import collections
    from plsim.data.regions import REGIONS
    tot = collections.Counter()
    for r in rows(*sys.argv[1:]):
        if not r["county"].endswith("*"):
            tot[r["county"].split(".")[0]] += int(r["pop"])
    for reg in REGIONS:
        if reg.code in tot:
            print(f"  {reg.code}: rows {tot[reg.code]:>9,}  voivodeship {reg.pop_1931:>9,}  missing {reg.pop_1931 - tot[reg.code]:>8,}")
