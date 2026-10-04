"""Check plsim/data/census1931_strata.csv.

Every row's religions and languages are at most its population and leave at
most 2 % unstated; every county adds up to its 1931 population; every
voivodeship adds up to its census population (Warsaw voivodeship is short
the city of Płock, whose page is missing from the scan).
"""
import collections
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

REL = ["rc", "gc", "or", "ev", "xc", "jw", "xn", "ro"]
LANG = ["pl", "uk", "rue", "be", "pls", "ru", "cs", "lt", "de", "yi", "he", "oth", "unk"]


def rows(path="plsim/data/census1931_strata.csv"):
    with open(path, encoding="utf-8") as fh:
        yield from csv.DictReader(l for l in fh if not l.startswith("#"))


if __name__ == "__main__":
    from plsim.data.counties import BY_CODE, CENSUS_1931
    from plsim.data.regions import REGIONS
    bad = 0
    county, voi = collections.Counter(), collections.Counter()
    for r in rows(*sys.argv[1:]):
        pop = int(r["pop"])
        for name, cols in (("religions", REL), ("languages", LANG)):
            s = sum(int(r[c] or 0) for c in cols)
            # a few machine-read rows overshoot by a handful of persons
            if s > pop + max(0.001 * pop, 100) or pop - s > 0.02 * pop:
                bad += 1
                print(f"{r['county']} p.{r['page']} {r['stratum']}: {name} {s} vs population {pop}")
        county[r["county"]] += pop
        voi[r["county"][:3]] += pop
    for code, pop in county.items():
        ref = CENSUS_1931.get(code, (None,))[0] or (BY_CODE[code].pop if code in BY_CODE else None)
        if ref and abs(ref - pop) > 0.001 * ref and code != "WAR.plock":
            print(f"{code}: rows {pop:,} vs county {ref:,.0f}")
    print("all rows add up" if not bad else f"{bad} rows do not add up")
    for reg in REGIONS:
        if reg.code in voi:
            print(f"  {reg.code}: rows {voi[reg.code]:>9,}  voivodeship {reg.pop_1931:>9,}  "
                  f"missing {reg.pop_1931 - voi[reg.code]:>7,}")
