"""Exogenous events: border changes, wartime deaths, population transfers.

The counterfactual scenarios have no war, so the model has no machinery for
one. The ``historical`` scenario (calibration) needs it: the Second World
War, the border change of 1945 and the population movements around it.
They are given as a list of events in the scenario (``history``), each
applied in the year it names:

* ``border``: regions change state (``member``), contact language
  (``dominant``) and official languages (``official``) at the start of the
  year. People keep their home language; competence in the new contact
  language is reset to the 1931 starting levels for it. With ``like``
  (regions), the regions also take those regions' vital rates, schooling
  and mean relative income: land about to be resettled from them.
* ``deaths``: a share (``rate``) or a number (``number``) of the selected
  people die (war, genocide, flight).
* ``emigrate``: they leave the territory (flight, expulsion, emigration).
* ``transfer``: they move to other regions (``to``: weights by region
  pattern, or ``"@vacated"``: in proportion to the people earlier events
  removed from each region and stratum by events marked ``vacate: true``:
  settlers taking the homes of the expelled).
* ``immigrate``: ``number`` people of group ``group`` (and identity
  ``identity``) arrive from outside (repatriation from the Soviet interior,
  return from the West).
* ``away``: the selected people leave for a time (forced labour in the
  Reich, prisoners of war) and come back to the region and stratum they
  left: ``back`` gives the share of the event's people returning in each
  later year, aged by the years away and thinned by ``survive`` (yearly
  survival abroad). Leaving counts as emigration, returning as immigration.
* ``identity``: a share of the selected people change national identity
  (``to``).

Selection (``who``): ``community``, ``language`` and ``group`` ("RC:pl")
lists select groups; ``identity`` selects people by national identity
(within each group, in proportion to that identity's share); ``sex`` ("m"
or "f") and ``ages`` ([first, last]) select cohorts. Regions (``where``,
``from``) are patterns as elsewhere ("WAW", "DE_*", "LWO.lwow"), or

* ``@outside_1946`` / ``@inside_1946``: units whose land lies mostly
  outside (inside) Poland's post-war border (``borders_1932.json`` key
  ``PL1946``);
* ``@member:XX``: units of state XX at the time of the event;

and ``within`` (same forms) restricts them further, e.g. the Lwów voivodeship
``within: "@member:PL"`` after 1945 is its part left in Poland.

Every event is recorded in the year's accounts: deaths, emigrants,
immigrants and the inter-regional flow matrix, so the population accounting
identity still holds.
"""
from __future__ import annotations

import numpy as np

from .data.languages import GROUP_INDEX, GROUPS, LANG_INDEX, NG
from .identity import ID_INDEX
from .params import region_match


def _as_list(x):
    if x is None:
        return []
    return list(x) if isinstance(x, (list, tuple)) else [x]


class History:
    def __init__(self, sim, events: list):
        self.sim = sim
        self.events = [dict(e) for e in (events or [])]
        self.R = sim.R
        self.vacated = np.zeros((sim.R, 2))                 # people removed by events, by region and stratum
        self.log: list[dict] = []
        self._inside = None
        self.away: list[dict] = []                          # people abroad for a time (``away`` events)

    # ------------------------------------------------------------------ selection
    def inside_1946(self) -> np.ndarray:
        """Share of each unit's land inside Poland's post-war border."""
        if self._inside is None:
            from .data.geography import MODEL_DLAT, MODEL_DLON, build_grid, inside_key
            g = build_grid(self.sim.codes, MODEL_DLAT, MODEL_DLON)
            ins = inside_key("PL1946", g.lat, g.lon)
            tot = np.bincount(g.region, weights=g.cell_km2, minlength=self.R)
            inn = np.bincount(g.region, weights=g.cell_km2 * ins, minlength=self.R)
            share = np.where(tot > 0, inn / np.maximum(tot, 1e-9), 0.0)
            # units without cells (none expected): by their seat
            for r in np.where(tot <= 0)[0]:
                reg = self.sim.regions[r]
                share[r] = float(inside_key("PL1946", reg.lat, reg.lon)[0])
            self._inside = share
        return self._inside

    def regions(self, spec) -> np.ndarray:
        out = np.zeros(self.R, dtype=bool)
        for pat in _as_list(spec):
            if pat == "*":
                out[:] = True
            elif pat == "@outside_1946":
                out |= self.inside_1946() < 0.5
            elif pat == "@inside_1946":
                out |= self.inside_1946() >= 0.5
            elif pat.startswith("@member:"):
                out |= np.array([m == pat.split(":", 1)[1] for m in self.sim.member])
            else:
                out |= np.array([region_match(c, pat) for c in self.sim.codes])
        return out

    @staticmethod
    def groups(who: dict) -> np.ndarray:
        who = who or {}
        m = np.ones(NG, dtype=bool)
        if "community" in who:
            m &= np.array([c in _as_list(who["community"]) for c, _ in GROUPS])
        if "language" in who:
            m &= np.array([l in _as_list(who["language"]) for _, l in GROUPS])
        if "group" in who:
            m &= np.array([f"{c}:{l}" in _as_list(who["group"]) for c, l in GROUPS])
        if "not_group" in who:
            m &= ~np.array([f"{c}:{l}" in _as_list(who["not_group"]) for c, l in GROUPS])
        return m

    @staticmethod
    def cohort(who: dict) -> np.ndarray:
        """(2, 101) weights over sex and age."""
        who = who or {}
        w = np.ones((2, 101))
        if who.get("sex") == "m":
            w[1] = 0.0
        elif who.get("sex") == "f":
            w[0] = 0.0
        if "ages" in who:
            a0, a1 = who["ages"]
            ages = np.arange(101)
            w[:, (ages < a0) | (ages > a1)] = 0.0
        return w

    def _share_selected(self, who: dict) -> np.ndarray:
        """(R,2,G) share of each (r,u,g) cell's people with a selected identity."""
        ident = self.sim.ident
        if not who or "identity" not in who:
            return np.ones((self.R, 2, NG))
        sel = [ID_INDEX[i] for i in _as_list(who["identity"])]
        tot = ident.I.sum(axis=3)
        return np.where(tot > 0, ident.I[..., sel].sum(axis=3) / np.maximum(tot, 1e-12), 0.0)

    # ------------------------------------------------------------------ core removal
    def _remove(self, where: np.ndarray, who: dict, rate=None, number=None):
        """Take people out: returns (moved (R,2,G,B,S,A), identity counts (R,2,G,NI))."""
        sim = self.sim
        P, I = sim.P, sim.ident.I
        gm = self.groups(who)
        coh = self.cohort(who)
        q = self._share_selected(who)                                         # (R,2,G)
        mask = (where[:, None, None] & gm[None, None, :]) * q                   # (R,2,G)
        base = P * coh[None, None, None, None]                                   # people in the cohorts
        avail = base * mask[..., None, None, None]
        n_avail = avail.sum()
        if n_avail <= 0:
            return np.zeros_like(P), np.zeros_like(I)
        f = float(rate) if rate is not None else min(float(number) / n_avail, 1.0)
        f = min(max(f, 0.0), 0.999)
        moved = avail * f
        sim.P = P - moved
        # identity: the movers are of the selected identities, in proportion to them
        n_rug = moved.sum(axis=(3, 4, 5))                                         # (R,2,G)
        if who and "identity" in who:
            sel = np.zeros(I.shape[-1], dtype=bool)
            sel[[ID_INDEX[i] for i in _as_list(who["identity"])]] = True
            Isel = np.where(sel, I, 0.0)
        else:
            Isel = I
        tot = Isel.sum(axis=3, keepdims=True)
        id_moved = np.where(tot > 0, Isel / np.maximum(tot, 1e-12), 0.0) * n_rug[..., None]
        sim.ident.I = np.maximum(I - id_moved, 0.0)
        u_rem = n_rug.sum(axis=2)                                                  # (R,2)
        return moved, id_moved, u_rem

    def _dest_weights(self, spec, U_from: np.ndarray) -> np.ndarray:
        """(R,2) destination weights."""
        w = np.zeros((self.R, 2))
        pop_ru = self.sim.P.sum(axis=(2, 3, 4, 5))
        if spec == "@vacated":
            w = self.vacated.copy()
        else:
            for pat, wt in (spec or {}).items():
                m = self.regions(pat)
                if not m.any():
                    continue
                share = pop_ru[m] / max(pop_ru[m].sum(), 1e-9)                    # within the pattern, by population
                w[m] += float(wt) * share
        s = w.sum()
        return w / s if s > 0 else w

    # ------------------------------------------------------------------ events
    def start_of_year(self, year: int) -> None:
        for e in self.events:
            if e.get("year") == year and e.get("kind") == "border":
                self._border(e, year)

    def apply(self, year: int, acc: dict) -> None:
        """Population events of ``year``; ``acc`` holds the year's accounts
        (deaths (R,), emigrants (R,G), immigrants (R,G), internal (R,R))."""
        for e in self.events:
            if e.get("year") != year or e.get("kind") == "border":
                continue
            kind = e["kind"]
            if kind in ("deaths", "emigrate", "transfer", "away"):
                src = self.regions(e.get("where", e.get("from", "*")))
                if e.get("within"):
                    src &= self.regions(e["within"])
                out = self._remove(src, e.get("who"), e.get("rate"), e.get("number"))
                if len(out) == 2:
                    continue
                moved, id_moved, u_rem = out
                n = moved.sum()
                if kind == "deaths":
                    acc["deaths"] += moved.sum(axis=(1, 2, 3, 4, 5))
                    if e.get("vacate", False):
                        self.vacated += u_rem
                elif kind in ("emigrate", "away"):
                    acc["emigrants"] += moved.sum(axis=(1, 3, 4, 5))
                    if e.get("vacate", False):
                        self.vacated += u_rem
                    if kind == "away":
                        self.away.append({"year": year, "P": moved, "I": id_moved, "label": e.get("label", ""),
                                          "back": {int(k): float(v) for k, v in (e.get("back") or {}).items()},
                                          "survive": float(e.get("survive", 1.0))})
                else:
                    w = self._dest_weights(e.get("to"), u_rem)
                    self._place(moved, id_moved, w, acc)
                    if e.get("vacate", False):
                        self.vacated += u_rem
                self.log.append({"year": year, "kind": kind, "label": e.get("label", ""), "people": float(n)})
            elif kind == "immigrate":
                self._immigrate(e, acc)
            elif kind == "identity":
                self._identity(e)
        for a in self.away:
            if year in a["back"]:
                self._return(a, year, acc)

    def _place(self, moved, id_moved, w: np.ndarray, acc: dict) -> None:
        """Put movers (by origin) into destinations with weights w (R,2)."""
        sim = self.sim
        by_g = moved.sum(axis=(0, 1))                                             # (G,B,S,A)
        id_g = id_moved.sum(axis=(0, 1))                                          # (G,NI)
        from_r = moved.sum(axis=(1, 2, 3, 4, 5))                                  # (R,)
        tot = from_r.sum()
        if tot <= 0 or w.sum() <= 0:
            return
        for r in range(self.R):
            for u in (0, 1):
                if w[r, u] <= 0:
                    continue
                sim.P[r, u] += by_g * w[r, u]
                sim.ident.I[r, u] += id_g * w[r, u]
        dest_r = w.sum(axis=1)
        acc["internal"] += np.outer(from_r, dest_r)
        # destination quotas (``@vacated``) are used up by the people placed
        self.vacated = np.maximum(self.vacated - w * tot, 0.0)
        sim.mig.reset_competence(sim.P)

    def _immigrate(self, e: dict, acc: dict) -> None:
        sim = self.sim
        c, l = e["group"].split(":")
        g = GROUP_INDEX[(c, l)]
        n = float(e["number"])
        w = self._dest_weights(e.get("to"), None)
        if w.sum() <= 0:
            return
        # age and sex structure: that of the group in the whole run (or everyone)
        prof = sim.P[:, :, g].sum(axis=(0, 1, 2))
        if prof.sum() <= 0:
            prof = sim.P.sum(axis=(0, 1, 2, 3))
        prof = prof / prof.sum()                                                  # (S,A)
        ident = ID_INDEX[e.get("identity", "pl")]
        for r in range(self.R):
            for u in (0, 1):
                if w[r, u] <= 0:
                    continue
                add = n * w[r, u] * prof
                sim.P[r, u, g, 1] += add
                sim.ident.I[r, u, g, ident] += add.sum()
                acc["immigrants"][r, g] += add.sum()
        self.vacated = np.maximum(self.vacated - w * n, 0.0) if e.get("to") == "@vacated" else self.vacated
        sim.mig.reset_competence(sim.P)
        self.log.append({"year": e["year"], "kind": "immigrate", "label": e.get("label", ""), "people": n})

    def _return(self, a: dict, year: int, acc: dict) -> None:
        """People of an ``away`` event come back to where they left."""
        sim = self.sim
        k = year - a["year"]
        f = a["back"][year] * a["survive"] ** k
        back = a["P"] * f
        if k > 0:                                                               # aged by the years away
            aged = np.zeros_like(back)
            aged[..., k:] = back[..., :-k]
            aged[..., -1] += back[..., -k:].sum(axis=-1)                       # past 100: kept at 100
            back = aged
        sim.P = sim.P + back
        sim.ident.I = sim.ident.I + a["I"] * f
        acc["immigrants"] += back.sum(axis=(1, 3, 4, 5))
        sim.mig.reset_competence(sim.P)
        self.log.append({"year": year, "kind": "return", "label": a["label"], "people": float(back.sum())})

    def _identity(self, e: dict) -> None:
        sim = self.sim
        where = self.regions(e.get("where", "*"))
        if e.get("within"):
            where &= self.regions(e["within"])
        gm = self.groups(e.get("who"))
        frm = [ID_INDEX[i] for i in _as_list((e.get("who") or {}).get("identity", []))]
        to = ID_INDEX[e["to"]]
        rate = float(e["rate"])
        I = sim.ident.I
        m = where[:, None, None] & gm[None, None, :]
        moved = I[..., frm] * rate * m[..., None]
        I[..., frm] -= moved
        I[..., to] += moved.sum(axis=3)
        self.log.append({"year": e["year"], "kind": "identity", "label": e.get("label", ""), "people": float(moved.sum())})

    # ------------------------------------------------------------------ border change
    def _border(self, e: dict, year: int) -> None:
        sim = self.sim
        idx = np.where(self.regions(e["where"]))[0]
        if not len(idx):
            return
        sim.change_regime(idx, member=e.get("member"), dominant=e.get("dominant"), official=e.get("official"))
        if e.get("like"):
            like = np.where(self.regions(e["like"]) & ~np.isin(np.arange(self.R), idx))[0]
            sim.adopt_profile(idx, like)
        sim.res.border_changes.append({"year": year, "codes": [sim.codes[i] for i in idx],
                                       "member": e.get("member"), "dominant": e.get("dominant"),
                                       "label": e.get("label", "")})
        self.log.append({"year": year, "kind": "border", "label": e.get("label", ""), "units": int(len(idx))})


def members_at(res, year: int) -> list:
    """State (member) of each region of a run at 1 January of ``year``."""
    mem = list(res.members)
    idx = {c: i for i, c in enumerate(res.region_codes)}
    for ch in getattr(res, "border_changes", []) or []:
        if ch["year"] < year and ch.get("member"):
            for c in ch["codes"]:
                mem[idx[c]] = ch["member"]
    return mem


__all__ = ["History", "members_at", "LANG_INDEX"]
