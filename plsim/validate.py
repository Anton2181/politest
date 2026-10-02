"""Back-validation (1932-1939) and long-run plausibility checks.

Historical targets are the *registered* aggregates of the Polish and
Lithuanian statistical offices.  Registration of deaths (especially infant
deaths) in the eastern voivodeships was incomplete, so modelled "true" crude
death rates are expected to sit slightly above the registered ones; the
tolerances reflect that.  Targets:

* Poland, population 1 Jan 1939: official GUS estimate 35.1 M (probably
  somewhat inflated by under-registered deaths); we accept 34.3-35.3 M.
* Poland, crude birth rate: 1932 ~28.8, 1938 ~24.3 per 1000.
* Poland, crude death rate: 1932 ~15.0, 1938 ~13.8 per 1000.
* Poland, life expectancy 1931-32: males 48.2, females 51.4.
* Poland, motor vehicles 1 Jan 1938: 44,200 (~1.27 per 1000).
* Lithuania 1938: ~2.56 M; CBR 22.6, CDR 12.6 (1933: 25.5 / 13.4).

Long-run plausibility bands come from comparator countries without Soviet-
type regimes (Spain, Portugal, Italy, Greece, Ireland, Finland) and from
Poland's own post-war record; they are *not* forecasts, just guard rails.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import Results


@dataclass
class Check:
    name: str
    value: float
    lo: float
    hi: float
    kind: str  # 'historical' | 'plausibility'

    @property
    def ok(self) -> bool:
        return self.lo <= self.value <= self.hi

    def row(self) -> str:
        flag = "PASS" if self.ok else "FAIL"
        return f"{flag:4}  {self.kind:12}  {self.name:52}  {self.value:10.3f}   [{self.lo}, {self.hi}]"


def _idx(res: Results, year: int) -> int:
    """Index of the record whose flows are those of calendar year ``year``
    (records are stamped with the following 1 January)."""
    return res.years.index(year + 1)


def _pl_mask(res: Results):
    return np.array([not c.startswith("LT") for c in res.region_codes])


def rates(res: Results, year: int, mask) -> tuple[float, float, float]:
    A = res.arrays()
    i = _idx(res, year)
    p_end = A["pop"][i][mask].sum()
    p_start = A["pop"][i - 1][mask].sum() if i > 0 else p_end
    mid = 0.5 * (p_start + p_end)
    return A["births"][i][mask].sum() / mid * 1000, A["deaths"][i][mask].sum() / mid * 1000, mid


def historical_checks(res: Results) -> list[Check]:
    A = res.arrays()
    pl = _pl_mask(res)
    out = []
    y1939 = res.years.index(1939)
    out.append(Check("Poland population 1 Jan 1939 (M)", A["pop"][y1939][pl].sum() / 1e6, 34.3, 35.3, "historical"))
    cbr32, cdr32, _ = rates(res, 1932, pl)
    cbr38, cdr38, mid38 = rates(res, 1938, pl)
    out.append(Check("Poland CBR 1932 (per 1000)", cbr32, 27.3, 30.3, "historical"))
    out.append(Check("Poland CBR 1938 (per 1000)", cbr38, 22.8, 25.8, "historical"))
    out.append(Check("Poland CDR 1932 (per 1000; registered 15.0)", cdr32, 14.0, 17.0, "historical"))
    out.append(Check("Poland CDR 1938 (per 1000; registered 13.8)", cdr38, 12.8, 15.3, "historical"))
    i32 = _idx(res, 1932)
    w = A["pop"][i32].sum(axis=(1, 2))
    e0 = (A["e0"][i32][pl] * w[pl, None]).sum(0) / w[pl].sum()
    out.append(Check("Poland e0 males 1932 (1931-32 table: 48.2)", e0[0], 46.7, 50.2, "historical"))
    out.append(Check("Poland e0 females 1932 (1931-32 table: 51.4)", e0[1], 49.9, 53.4, "historical"))
    i38 = _idx(res, 1937)
    out.append(Check("Motor vehicles per 1000, 1 Jan 1938", res.econ[i38]["vehicles_per_1000"], 0.8, 1.8, "historical"))
    urb = A["pop"][y1939][pl][:, 1].sum() / A["pop"][y1939][pl].sum()
    out.append(Check("Poland urban share 1939", urb, 0.27, 0.33, "historical"))
    if (~pl).any():
        lt = ~pl
        out.append(Check("Lithuania population 1938 (M)", A["pop"][_idx(res, 1938)][lt].sum() / 1e6, 2.45, 2.65, "historical"))
        cbr, cdr, _ = rates(res, 1938, lt)
        out.append(Check("Lithuania CBR 1938 (22.6)", cbr, 20.6, 24.6, "historical"))
        out.append(Check("Lithuania CDR 1938 (12.6)", cdr, 11.1, 14.1, "historical"))
    return out


def plausibility_checks(res: Results) -> list[Check]:
    A = res.arrays()
    pl = _pl_mask(res)
    out = []

    def nat(year, key):
        i = _idx(res, year)
        w = A["pop"][i].sum(axis=(1, 2))
        if key == "tfr":
            return (A["tfr"][i] * w).sum() / w.sum()
        if key == "e0":
            return float(((A["e0"][i] * w[:, None]).sum(0) / w.sum()).mean())
        raise KeyError(key)

    if 1960 in res.years:
        out.append(Check("TFR 1960 (S. Europe 2.3-3.8)", nat(1960, "tfr"), 2.3, 3.8, "plausibility"))
        out.append(Check("e0 both sexes 1960 (58-72)", nat(1960, "e0"), 58, 72, "plausibility"))
    if 2000 in res.years:
        out.append(Check("TFR 2000 (1.2-2.2)", nat(2000, "tfr"), 1.2, 2.2, "plausibility"))
        out.append(Check("e0 both sexes 2000 (70-81)", nat(2000, "e0"), 70, 81, "plausibility"))
        i = _idx(res, 2000)
        urb = A["pop"][i][:, 1].sum() / A["pop"][i].sum()
        out.append(Check("Urban share 2000 (0.50-0.80)", urb, 0.5, 0.8, "plausibility"))
        out.append(Check("Polish-unit population 2000 (M)", A["pop"][i][pl].sum() / 1e6, 40, 65, "plausibility"))
    if res.years[-1] >= 2030:
        # dual carriageways per 1000 km2 of the state (Czechia, Hungary, Poland's
        # 2033 plan ~18-26; Spain, France, Portugal ~35; Germany ~45)
        from .data.regions import REGIONS
        area = sum(r.area_km2 for r in REGIONS if r.code in {c.split(".")[0] for c in res.region_codes})
        km = res.km[-1]
        out.append(Check("Expressways + motorways, last year (km per 1000 km2)",
                         (km["road_express"] + km["road_motorway"]) / area * 1000, 15, 35, "plausibility"))
    return out


def report(res: Results) -> str:
    checks = historical_checks(res) + plausibility_checks(res)
    lines = [c.row() for c in checks]
    n_ok = sum(c.ok for c in checks)
    lines.append(f"{n_ok}/{len(checks)} checks passed")
    return "\n".join(lines)
