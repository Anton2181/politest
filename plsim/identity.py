"""National identity, tracked separately from home language.

Home language and national identity were never the same thing in these
lands. Catholic Belarusian speakers mostly called themselves Poles; many
Orthodox villagers of Polesie answered "tutejszy" (local); Polish-speaking
Jews remained Jews; in Lithuania a large part of the Polish-speaking
Catholics were entered, and in time saw themselves, as Lithuanians. A
mother-tongue census (Poland 1931) records language, a nationality census
(Poland 1921, Lithuania 1923, modern self-identification) records identity,
and the two series diverge.

State
-----
``I[r, u, g, i]``: persons of region r, rural/urban cell u and community-
language group g who identify with nationality i (``IDENTITIES``). The
totals over i always equal the population of (r, u, g). Identity is not
tracked by age.

Initial identity (1931)
-----------------------
``INITIAL`` gives the identity mix of each group, with overrides for the
Lithuanian member and Soviet Belarus, chosen to agree with the nationality
censuses next to the 1931 language census: in Poland in 1921 about three
quarters of the Jews by religion declared Jewish nationality and a quarter
Polish; Catholic Belarusian and Ukrainian speakers ("Latinniks") mostly
declared Polish nationality; in Lithuania in 1923, 65.6 thousand Poles
against some 150 thousand Polish speakers (about 42 %); in the BSSR in 1926
the Belarusian nationality was declared by nearly all Belarusian speakers
(Soviet indigenisation), and Catholics were split between Belarusian and
Polish.

Dynamics
--------
* **Births.** A child raised in its mother's language takes her identity.
  A child raised in another language takes the identity that goes with the
  new language (``NATURAL``: Polish for a Catholic Polish speaker, Jewish
  for a Jew of any language ...) with probability ``follow``, otherwise its
  mother's identity. Adult language switchers follow the same rule.
* **Nation-building.** People who identify only as "local" adopt the
  national identity that goes with their language and faith at the yearly
  rate ``nation_building x M`` (modernisation: schools, press, army,
  elections; Weber 1976, Hroch 1985).
* **State-nation pull.** Everyone else may adopt the identity of the
  region's state (contact) language at the yearly rate
  ``assimilation x pressure x M x compat(community)``, reduced by the
  factor ``1 - anchor`` when the identity is the one that goes with the
  person's own home language (identity anchored in language). The policy
  ``pressure`` is that of the language module. "Lithuanisation" of the
  Polish speakers of the Lithuanian member runs through this process as
  well as through language shift; with Polish co-official (the baseline
  federation) the pull is weak and identity falls about as fast as speech.
* **Migration and exchange.** People leaving a cell take its identity mix;
  arrivals take the mix of the people of their group who left (first those
  of the same region, then the state pool).
"""
from __future__ import annotations

import numpy as np

from .data.languages import COMMUNITIES, GROUPS, LANG_INDEX, NG, NL

IDENTITIES = ["pl", "uk", "be", "lt", "ru", "de", "jw", "cs", "lv", "csb", "rue", "loc", "oth"]
ID_INDEX = {k: i for i, k in enumerate(IDENTITIES)}
NI = len(IDENTITIES)
ID_LABEL = {"pl": "Polish", "uk": "Ukrainian", "be": "Belarusian", "lt": "Lithuanian", "ru": "Russian",
            "de": "German", "jw": "Jewish", "cs": "Czech", "lv": "Latvian", "csb": "Kashubian",
            "rue": "Lemko/Rusyn", "loc": "Local ('tutejszy')", "oth": "Other"}


def natural(c: str, l: str) -> str:
    """The identity that goes with home language l for community c."""
    if c in ("JW", "JH"):
        return "jw"
    if l in ("pl", "csb", "wym"):
        return "pl"
    if l == "uk":
        return "pl" if c == "RC" else "uk"
    if l == "be":
        return "pl" if c == "RC" else "be"
    if l == "ru":
        return "pl" if c == "RC" else "ru"
    if l == "pls":
        return "loc"
    if l in ("lt", "de", "cs", "lv", "rue"):
        return l
    return "oth"


# Identity mix of each group in 1931 (missing groups: their natural identity).
INITIAL = {
    "RC:pl": {"pl": .998, "lt": .002},
    "RC:uk": {"pl": .85, "uk": .15},
    "RC:be": {"pl": .78, "be": .12, "loc": .10},
    "RC:pls": {"loc": .70, "pl": .30},
    "RC:de": {"de": .70, "pl": .30},
    "RC:ru": {"pl": .50, "ru": .50},
    "RC:lt": {"lt": .85, "pl": .15},
    "RC:csb": {"pl": .80, "csb": .20},
    "RC:cs": {"cs": .90, "pl": .10},
    "RC:lv": {"lv": .85, "pl": .10, "lt": .05},
    "RC:rom": {"oth": .70, "pl": .30},
    "RC:wym": {"pl": .60, "de": .40},
    "RC:oth": {"oth": .80, "pl": .20},
    "GC:pl": {"pl": .70, "uk": .30},
    "GC:uk": {"uk": .88, "ru": .01, "pl": .06, "loc": .05},
    "GC:rue": {"rue": .60, "uk": .30, "pl": .10},
    "OR:pl": {"pl": .85, "ru": .05, "be": .05, "uk": .05},
    "OR:uk": {"uk": .78, "loc": .13, "ru": .02, "pl": .07},
    "OR:be": {"be": .52, "loc": .35, "ru": .03, "pl": .10},
    "OR:pls": {"loc": .75, "uk": .12, "be": .08, "pl": .05},
    "OR:ru": {"ru": .85, "be": .10, "pl": .05},
    "OR:lt": {"lt": .70, "ru": .30},
    "OR:rue": {"rue": .60, "uk": .30, "ru": .10},
    "OR:cs": {"cs": .90, "uk": .10},
    "JW:pl": {"jw": .35, "pl": .65},
    "JW:yi": {"jw": .88, "pl": .12},
    "JW:de": {"jw": .60, "de": .30, "pl": .10},
    "JW:ru": {"jw": .70, "ru": .30},
    "JW:lt": {"jw": .70, "lt": .30},
    "PR:pl": {"pl": .80, "de": .20},
    "PR:de": {"de": .97, "pl": .03},
    "PR:lt": {"de": .50, "lt": .30, "oth": .20},       # Memellanders
    "OT:be": {"be": .70, "loc": .30},
}
# Overrides by region prefix: the Lithuanian member, Soviet Belarus
INITIAL_REGIONS = {
    "LT_": {"RC:pl": {"pl": .42, "lt": .58}, "RC:lt": {"lt": .998, "pl": .002},
            "RC:be": {"pl": .50, "be": .20, "lt": .30}, "JW:yi": {"jw": .97, "lt": .03}},
    "BY_": {"RC:pl": {"pl": .97, "be": .03}, "RC:be": {"be": .55, "pl": .45},
            "OR:be": {"be": .92, "ru": .05, "loc": .03}, "OR:ru": {"ru": .75, "be": .25},
            "JW:yi": {"jw": .99, "be": .01}},
}
# state identity of a region: the identity of its contact language
STATE_IDENTITY = {"pl": "pl", "lt": "lt", "uk": "uk", "be": "be", "de": "de", "ru": "ru", "cs": "cs", "lv": "lv"}


def initial_mix(c: str, l: str, code: str) -> dict:
    key = f"{c}:{l}"
    for prefix, table in INITIAL_REGIONS.items():
        if code.startswith(prefix) and key in table:
            return table[key]
    return INITIAL.get(key, {natural(c, l): 1.0})


class IdentityModel:
    def __init__(self, params: dict, codes: list[str], dominant: list[str], pop_rug: np.ndarray):
        self.p = params
        self.codes = codes
        self.R = len(codes)
        self.group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
        self.nat = np.zeros((NG, NI))
        for g, (c, l) in enumerate(GROUPS):
            self.nat[g, ID_INDEX[natural(c, l)]] = 1.0
        self.nat_idx = self.nat.argmax(axis=1)
        mix = np.zeros((self.R, NG, NI))
        for r, code in enumerate(codes):
            for g, (c, l) in enumerate(GROUPS):
                m = initial_mix(c, l, code)
                s = sum(m.values())
                for k, v in m.items():
                    mix[r, g, ID_INDEX[k]] = v / s
        self.mix0 = mix
        self.I = pop_rug[..., None] * mix[:, None]                         # (R,2,G,NI)
        self.state = np.array([ID_INDEX[STATE_IDENTITY.get(d, "pl")] for d in dominant])
        compat = params.get("compat", {})
        comms = [c.code for c in COMMUNITIES]
        self.compat = np.array([compat.get(f"{c}:{l}", compat.get(c, 1.0)) for c, l in GROUPS])
        assert all(c in comms for c, _ in GROUPS)

    # ------------------------------------------------------------------ helpers
    def shares(self) -> np.ndarray:
        tot = self.I.sum(axis=3, keepdims=True)
        return np.where(tot > 1e-9, self.I / np.maximum(tot, 1e-12), self.mix0[:, None])

    def birth_counts(self, child: np.ndarray, shifted: np.ndarray, dist: np.ndarray) -> np.ndarray:
        """Identity of newborns (R,2,G,NI) from children raised in the
        mother's language ``child`` (R,2,G), children raised in another
        language ``shifted`` (R,2,G, by mother's group) and their target
        distribution ``dist`` (R,2,G,G)."""
        m = self.shares()
        f = self.p["follow"]
        into = np.einsum("rug,rugk->ruk", shifted, dist)
        out = child[..., None] * m + f * into[..., None] * self.nat[None, None]
        out += (1 - f) * np.einsum("rug,rugk,rugi->ruki", shifted, dist, m)
        return out

    def vital(self, survived: np.ndarray, before: np.ndarray, births: np.ndarray, newborn_surv: np.ndarray):
        """Deaths (``survived`` of ``before`` persons of each (r,u,g) alive a
        year later) and births (identity counts ``births`` of which
        ``newborn_surv`` persons survive to the year's end)."""
        frac = np.where(before > 0, survived / np.maximum(before, 1e-12), 0.0)
        nb = births.sum(axis=3)
        bmix = np.where(nb[..., None] > 0, births / np.maximum(nb, 1e-12)[..., None], self.nat[None, None])
        self.I = self.I * frac[..., None] + bmix * newborn_surv[..., None]

    def switch(self, flows: np.ndarray) -> None:
        """Adult home-language switches ``flows`` (R,2,G_from,G_to)."""
        m = self.shares()
        f = self.p["follow"]
        out = flows.sum(axis=3)
        into = flows.sum(axis=2)
        self.I -= out[..., None] * m
        self.I += f * into[..., None] * self.nat[None, None]
        self.I += (1 - f) * np.einsum("rugk,rugi->ruki", flows, m)
        np.maximum(self.I, 0.0, out=self.I)

    def reconcile(self, before: np.ndarray, after: np.ndarray) -> None:
        """Migration (or an exchange) changed the totals of (r,u,g) from
        ``before`` to ``after``: leavers take their cell's mix, arrivals take
        the mix of their group's leavers (same region first, then the state)."""
        m = self.shares()
        dec = np.maximum(before - after, 0.0)
        inc = np.maximum(after - before, 0.0)
        keep = np.where(before > 0, np.minimum(after, before) / np.maximum(before, 1e-12), 0.0)
        I = self.I * keep[..., None]
        out = dec[..., None] * m                                          # (R,2,G,NI) leavers
        # arrivals within the region (rural <-> urban)
        out_r = out.sum(axis=1)                                           # (R,G,NI)
        dec_r, inc_r = dec.sum(axis=1), inc.sum(axis=1)                   # (R,G)
        local = np.minimum(dec_r, inc_r)
        mix_r = np.where(dec_r[..., None] > 0, out_r / np.maximum(dec_r, 1e-12)[..., None], 0.0)
        w_loc = np.where(inc_r > 0, local / np.maximum(inc_r, 1e-12), 0.0)              # (R,G)
        I += inc[..., None] * (w_loc[:, None, :, None] * mix_r[:, None])
        # the rest from the state pool of leavers of the group (or its present mix)
        rest_out = out_r - local[..., None] * mix_r                                    # (R,G,NI)
        pool = rest_out.sum(axis=0)                                                     # (G,NI)
        cur = (self.I).sum(axis=(0, 1))
        pool = np.where(pool.sum(axis=1, keepdims=True) > 1e-9, pool, cur)
        pool = np.where(pool.sum(axis=1, keepdims=True) > 1e-9, pool, self.nat)
        pool = pool / pool.sum(axis=1, keepdims=True)
        I += (inc * (1 - w_loc[:, None, :]))[..., None] * pool[None, None]
        self.I = np.maximum(I, 0.0)

    def drift(self, M: np.ndarray, pressure: np.ndarray) -> None:
        """Nation-building of "local" identities; pull of the state nation."""
        p = self.p
        I = self.I
        loc = ID_INDEX["loc"]
        # nation-building: local -> the identity that goes with language and faith
        nb = 1 - np.exp(-p["nation_building"] * M)                                       # (R,2)
        target = self.nat_idx                                                            # (G,)
        movable = target != loc
        mv = I[:, :, movable, loc] * nb[..., None]
        I[:, :, movable, loc] -= mv
        np.add.at(I, (slice(None), slice(None), np.where(movable)[0], target[movable]), mv)
        # state-nation pull
        rate = p["assimilation"] * pressure[:, None, None] * M[..., None] * self.compat[None, None, :]   # (R,2,G)
        st = self.state                                                                   # (R,)
        anchor = np.zeros((self.R, NG, NI))
        anchor[:, np.arange(NG), self.nat_idx] = p["anchor"]
        h = 1 - np.exp(-rate[..., None] * (1 - anchor[:, None]))                          # (R,2,G,NI)
        h[np.arange(self.R), :, :, st] = 0.0
        moved = I * h
        I -= moved
        I[np.arange(self.R), :, :, st] += moved.sum(axis=3)
        self.I = I

    # ------------------------------------------------------------------ outputs
    def by_region(self) -> np.ndarray:
        return self.I.sum(axis=(1, 2))                                                    # (R,NI)

    def by_language(self) -> np.ndarray:
        out = np.zeros((self.R, NL, NI))
        np.add.at(out, (slice(None), self.group_lang), self.I.sum(axis=1))
        return out                                                                        # (R,NL,NI)


# ---------------------------------------------------------------------------------
# Nationality censuses (identity-based observation)
# ---------------------------------------------------------------------------------
def _d(**kw) -> dict:
    s = sum(kw.values())
    return {k: v / s for k, v in kw.items()}


def identity_mapping(regime: str, ident: str, region_code: str) -> dict:
    """Probability that a person of identity ``ident`` is recorded as each
    census category by a nationality census."""
    direct = {"pl": "pl", "uk": "uk", "be": "be", "lt": "lt", "ru": "ru", "de": "de", "jw": "jw", "cs": "cs",
              "lv": "lv", "oth": "other"}
    if regime == "polish_1921":
        # no Kashubian or Lemko category; "local" people were mostly entered
        # by the enumerators under a nationality
        if ident == "csb":
            return {"pl": 1.0}
        if ident == "rue":
            return _d(ruth=.7, uk=.2, pl=.1)
        if ident == "loc":
            return _d(tut=.25, pl=.35, be=.2, uk=.2)
        return {direct[ident]: 1.0}
    if regime == "lithuanian_1923":
        if ident == "csb":
            return {"pl": 1.0}
        if ident == "rue":
            return {"ru": 1.0}
        if ident == "loc":
            return _d(tut=.2, lt=.4, pl=.2, be=.2) if region_code.startswith("LT") else _d(tut=.4, pl=.3, be=.3)
        if ident == "pl" and region_code.startswith("LT"):
            return _d(pl=.9, lt=.1)            # some Poles still entered as Lithuanians
        return {direct[ident]: 1.0}
    if regime == "modern_selfid":
        if ident == "loc":
            return {"tut": 1.0}
        if ident == "csb":
            return {"csb": 1.0}
        if ident == "rue":
            return {"rue": 1.0}
        return {direct[ident]: 1.0}
    raise ValueError(regime)


IDENTITY_REGIMES = ["polish_1921", "lithuanian_1923", "modern_selfid"]


def identity_census(I_rugi: np.ndarray, regime: str, region_codes: list[str], categories: list[str]) -> np.ndarray:
    """(R, n_categories) recorded counts from identity counts (R,2,G,NI)."""
    by_ri = I_rugi.sum(axis=(1, 2))                                               # (R,NI)
    cat = {c: i for i, c in enumerate(categories)}
    out = np.zeros((len(region_codes), len(categories)))
    for r, code in enumerate(region_codes):
        for i, ident in enumerate(IDENTITIES):
            for c, pr in identity_mapping(regime, ident, code).items():
                out[r, cat[c]] += by_ri[r, i] * pr
    return out
