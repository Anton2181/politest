"""Language shift, bilingualism, extinction - and a census observation model.

Dynamics
--------
The model is a demographically explicit, multi-language generalisation of
Abrams & Strogatz (2003, Nature) with an intermediate bilingual state, in the
spirit of Mira & Paredes (2005), Minett & Wang (2008, Lingua) and Kandler,
Unger & Steele (2010, Phil. Trans. R. Soc. B):

* Speakers belong to groups (community c, home language L) and are either
  monolingual (b = 0) or also competent in the region's dominant/state
  language D (b = 1).
* **Vertical transmission** (Cavalli-Sforza & Feldman 1981): a child of an
  (c, L, b) mother is raised in L unless the family shifts.  The per-birth
  shift probability is

      p = sigma0(c,L) * Mod(r,u) * Pol(r,t) * (1 - omega(r,L))
          * sum_K A_K / (A_L + sum_K A_K) * (1 if b else m_mono)

  with Abrams-Strogatz attractiveness ``A_K = s_K(r,t) * x_K^a``: status
  ``s_K`` (policy-controlled prestige/utility of K) times the local share of
  people competent in K raised to the exponent a (~1.31 in Abrams & Strogatz's
  fits to Welsh, Gaelic, Quechua ...).  ``omega`` is institutional maintenance
  (own-language schooling, church, press); ``Mod`` rises with urbanity,
  modernisation and market access (roads, rails, schools and the army as the
  agents of national integration - Weber 1976, "Peasants into Frenchmen").
  The target language K is drawn in proportion to A_K among the targets
  admissible for community c (Catholic Belarusian speakers are pulled to
  Polish, Orthodox ones to Belarusian/Russian/Polish, Polesians to Ukrainian,
  Belarusian or Polish, Memellanders to German, etc.).
* **Horizontal processes** (annual hazards): school-age acquisition of D
  (depends on enrolment and on the share of minority children taught in their
  own language), adult acquisition through contact, conscription (young men),
  and a small rate of adult re-identification of bilinguals.
* Community transitions: Haredi -> acculturated Jewish (defection at birth)
  and a small reverse flow.

Because all of this sits inside the cohort-component engine, differential
fertility, mortality, urbanisation and emigration feed back on the
language balance exactly as in Kandler et al.'s "internal recruitment" term.

Observation model
-----------------
``CensusRegime`` maps the latent (community, home-language, competence)
state to the categories a given census would have printed, e.g. the 1931
Polish census ("tutejszy", "ruski", Catholic Belarusian speakers returned as
Polish), the 1897 imperial Russian census (vernacular "native language"),
the 1923 Lithuanian census (nationality) or a modern self-identification
census.  Latent and "as-recorded" series can therefore diverge, as they did
historically.
"""
from __future__ import annotations

import numpy as np

from .data.languages import COMMUNITIES, GROUP_INDEX, GROUPS, LANG_INDEX, LANGUAGES, NG, NL, SHIFT_TARGETS
from .economy import piecewise

CENSUS_CATEGORIES = ["pl", "uk", "ruth", "be", "tut", "yi", "he", "de", "ru", "lt", "cs", "lv",
                     "csb", "rue", "rom", "kdr", "wym", "other"]
CAT_INDEX = {c: i for i, c in enumerate(CENSUS_CATEGORIES)}


def _lang_sched_value(spec, year: float) -> float:
    if isinstance(spec, (int, float)):
        return float(spec)
    return piecewise(year, spec)


class LanguageModel:
    def __init__(self, params: dict, regions, dominant: list[str]):
        self.p = params
        self.regions = regions
        self.codes = [r.code for r in regions]
        self.R = len(regions)
        self.dom = np.array([LANG_INDEX[d] for d in dominant])
        self.group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
        self.group_comm = np.array([[c.code for c in COMMUNITIES].index(c) for c, _ in GROUPS])
        # Target matrix: for every group g and every region r, which child groups
        # are admissible targets (boolean (R, G, G)).
        tgt = np.zeros((self.R, NG, NG), dtype=bool)
        for g, (c, l) in enumerate(GROUPS):
            base = set(SHIFT_TARGETS.get((c, l), ()))
            for r in range(self.R):
                ts = set(base)
                d = LANGUAGES[self.dom[r]].code
                if d != l:
                    ts.add(d)
                for t in ts:
                    if t == l:
                        continue
                    k = GROUP_INDEX.get((c, t))
                    if k is not None:
                        tgt[r, g, k] = True
        self.targets = tgt
        # sigma0 per group
        s0 = params["sigma0"]
        self.sigma0 = np.array([s0.get(f"{c}:{l}", s0.get(l, s0["default"])) for c, l in GROUPS])
        inst = params["institutional"]
        self.inst = np.array([inst.get(f"{c}:{l}", inst.get(l, 0.0)) for c, l in GROUPS])
        self.a = params["a"]
        conc = params.get("concentration", {})
        self.conc = np.array([conc.get(f"{c}:{l}", conc.get(l, 1.0)) for c, l in GROUPS], dtype=float)

    # ---------------------------------------------------------------- policy
    def status(self, year: float) -> np.ndarray:
        """(R, NL) status/prestige of each language in each region."""
        p = self.p
        s = np.zeros((self.R, NL))
        for l in LANGUAGES:
            s[:, LANG_INDEX[l.code]] = _lang_sched_value(p["status"].get(l.code, p["status"]["default"]), year)
        for pattern, over in p.get("status_regions", {}).items():
            for r, code in enumerate(self.codes):
                if code == pattern or (pattern.endswith("*") and code.startswith(pattern[:-1])):
                    for lc, spec in over.items():
                        s[r, LANG_INDEX[lc]] = _lang_sched_value(spec, year)
        # The dominant language of a region always has at least the reference status.
        s[np.arange(self.R), self.dom] = np.maximum(s[np.arange(self.R), self.dom], 1.0)
        return s

    def own_schooling(self, year: float) -> np.ndarray:
        p = self.p
        o = np.zeros((self.R, NG))
        for g, (c, l) in enumerate(GROUPS):
            spec = p["own_schooling"].get(f"{c}:{l}", p["own_schooling"].get(l, 0.0))
            o[:, g] = _lang_sched_value(spec, year)
        for pattern, over in p.get("own_schooling_regions", {}).items():
            for r, code in enumerate(self.codes):
                if code == pattern or (pattern.endswith("*") and code.startswith(pattern[:-1])):
                    for key, spec in over.items():
                        for g, (c, l) in enumerate(GROUPS):
                            if key == l or key == f"{c}:{l}":
                                o[r, g] = _lang_sched_value(spec, year)
        # own-language schooling is meaningless for the dominant language
        o[self.group_lang[None, :] == self.dom[:, None]] = 0.0
        return np.clip(o, 0, 1)

    def pressure(self, year: float) -> np.ndarray:
        p = self.p
        base = _lang_sched_value(p["pressure"]["default"], year)
        out = np.full(self.R, base)
        for pattern, spec in p["pressure"].items():
            if pattern == "default":
                continue
            for r, code in enumerate(self.codes):
                if code == pattern or (pattern.endswith("*") and code.startswith(pattern[:-1])):
                    out[r] = _lang_sched_value(spec, year)
        return out

    # ---------------------------------------------------------------- shares
    def competence_shares(self, P: np.ndarray) -> np.ndarray:
        """x[r,u,K]: share of people able to speak K (home speakers of K plus,
        for the dominant language, bilinguals)."""
        tot_g = P.sum(axis=(4, 5))            # (R,2,G,B)
        home = np.zeros(P.shape[:2] + (NL,))
        np.add.at(home, (slice(None), slice(None), self.group_lang), tot_g.sum(axis=3))
        bil = tot_g[..., 1]                    # (R,2,G)
        total = tot_g.sum(axis=(2, 3))         # (R,2)
        comp = home.copy()
        not_dom = self.group_lang[None, :] != self.dom[:, None]   # (R,G)
        extra = (bil * not_dom[:, None, :]).sum(axis=2)            # (R,2)
        comp[np.arange(self.R), :, self.dom] += extra
        with np.errstate(invalid="ignore", divide="ignore"):
            x = np.where(total[..., None] > 0, comp / total[..., None], 0.0)
        return np.clip(x, 0, 1)

    def modifier(self, M: np.ndarray, ma_norm: np.ndarray) -> np.ndarray:
        p = self.p
        urb = np.array([0.0, 1.0])[None, :]
        return (1 + p["urban_mult"] * urb) * (p["mod_base"] + p["mod_slope"] * M) * \
            (1 + p["access_mult"] * ma_norm[:, None])

    def local_environment(self, P: np.ndarray):
        """Competence shares *as experienced by the speakers of each group*.

        Minority speakers are spatially concentrated (enclave villages,
        shtetls, colonies, the Wilamowice or Trakai enclaves), so the share of
        own-language speakers around them is higher than the regional-cell
        share.  With concentration factor k_L the local own share is
        ``s_L = min(0.95, k_L * x_L)`` and the remaining neighbours have the
        cell's non-L language mix.  Returns (own local share (R,2,G),
        local competence in every language (R,2,G,NL))."""
        tot_gb = P.sum(axis=(4, 5))                        # (R,2,G,B)
        pop_g = tot_gb.sum(axis=3)                         # (R,2,G)
        bil_g = tot_gb[..., 1]
        total = pop_g.sum(axis=2)                          # (R,2)
        home = np.zeros(P.shape[:2] + (NL,))
        bil_l = np.zeros(P.shape[:2] + (NL,))
        np.add.at(home, (slice(None), slice(None), self.group_lang), pop_g)
        np.add.at(bil_l, (slice(None), slice(None), self.group_lang), bil_g)
        comp = home.copy()
        not_dom = self.group_lang[None, :] != self.dom[:, None]
        comp[np.arange(self.R), :, self.dom] += (bil_g * not_dom[:, None, :]).sum(axis=2)
        safe = np.clip(total, 1e-9, None)
        homeL = home[:, :, self.group_lang]                # (R,2,G)
        bilL = bil_l[:, :, self.group_lang]
        xL = homeL / safe[..., None]
        sL = np.clip(self.conc[None, None, :] * xL, 0, 0.95)
        sL = np.maximum(sL, xL)
        is_dom_k = (np.arange(NL)[None, :] == self.dom[:, None])            # (R,NL)
        # competence in K among the non-L neighbours
        compK_nonL = comp[:, :, None, :] - is_dom_k[:, None, None, :] * bilL[..., None]
        own_k = (np.arange(NL)[None, :] == self.group_lang[:, None])        # (G,NL)
        compK_nonL = np.where(own_k[None, None], 0.0, compK_nonL)
        nonL = np.clip(total[..., None] - homeL, 1e-9, None)
        xK = (1 - sL[..., None]) * np.clip(compK_nonL / nonL[..., None], 0, 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            bil_rate = np.where(homeL > 0, bilL / np.clip(homeL, 1e-9, None), 0.0)
        xK = xK + is_dom_k[:, None, None, :] * (sL * bil_rate)[..., None]
        xK = np.where(own_k[None, None], sL[..., None], xK)
        return sL, np.clip(xK, 0, 1)

    def transmission(self, year: float, P: np.ndarray, M: np.ndarray, ma_norm: np.ndarray):
        """Return (probability of shift per birth) array (R,2,G,2) and target
        distribution (R,2,G,G) for children of mothers in each state."""
        sL, xK = self.local_environment(P)                 # (R,2,G), (R,2,G,NL)
        s = self.status(year)                              # (R,NL)
        A = s[:, None, None, :] * np.power(xK, self.a)     # (R,2,G,NL) attraction as seen by group g
        Ag = np.take_along_axis(A, self.group_lang[None, None, :, None].repeat(A.shape[0], 0).repeat(2, 1),
                                axis=3)[..., 0]            # (R,2,G) own language
        # attraction of each target group k (language of k) as seen by group g
        tgt = self.targets[:, None, :, :]                 # (R,1,G,G)
        At = np.where(tgt, A[:, :, :, self.group_lang], 0.0)   # (R,2,G,G)
        sumT = At.sum(axis=3)
        with np.errstate(invalid="ignore", divide="ignore"):
            frac = np.where(sumT + Ag > 0, sumT / (sumT + Ag), 0.0)
            dist = np.where(sumT[..., None] > 0, At / sumT[..., None], 0.0)
        own = self.own_schooling(year)                     # (R,G)
        # Institutional completeness (Breton 1964): churches, schools, press and
        # associations sustain a language where its community is locally
        # substantial, not in a scattered diaspora.
        complete = np.clip(sL / self.p["completeness_share"], 0, 1)                 # (R,2,G)
        omega = np.clip((self.p["school_weight"] * own[:, None, :] + self.inst[None, None, :]) * complete, 0, 0.95)
        mod = self.modifier(M, ma_norm)                     # (R,2)
        pol = self.pressure(year)                           # (R,)
        base = self.sigma0[None, None, :] * mod[:, :, None] * pol[:, None, None] * (1 - omega) * frac
        p_shift = np.stack([base * self.p["m_mono"], base], axis=3)   # (R,2,G,2)
        p_shift = np.clip(p_shift, 0, self.p["max_shift"])
        return p_shift, dist, frac, mod, pol, omega

    # ---------------------------------------------------------------- horizontal
    def horizontal(self, year: float, P: np.ndarray, enrollment: np.ndarray, M: np.ndarray,
                   ma_norm: np.ndarray, x_cache=None) -> dict:
        """Apply annual acquisition of the dominant language and adult
        re-identification in place.  Returns flow diagnostics."""
        p = self.p
        _sL, xK = self.local_environment(P)
        own = self.own_schooling(year)
        not_dom = (self.group_lang[None, :] != self.dom[:, None])      # (R,G)
        # --- acquisition b: 0 -> 1 (contact with D speakers in the local environment)
        xd = np.take_along_axis(xK, self.dom[:, None, None, None].repeat(2, 1).repeat(NG, 2), axis=3)[..., 0]
        school = p["acq_school"] * enrollment[:, None, None] * (1 - own[:, None, :] * p["own_school_blocks"])
        adult = p["acq_adult"] * xd * (1 + p["acq_urban_bonus"] * np.array([0, 1])[None, :, None])
        mil = p["acq_military"] * piecewise(year, p["conscription"])
        h_school = 1 - np.exp(-school)                                   # (R,2,G)
        h_adult = 1 - np.exp(-adult)
        h_mil = 1 - np.exp(-mil)
        acq = np.zeros(P.shape[:3] + (2, 101))                           # (R,2,G,S,A)
        acq[..., 7:15] = h_school[..., None, None]
        acq[..., 15:65] = h_adult[..., None, None]
        acq[:, :, :, 0, 20:22] = 1 - (1 - acq[:, :, :, 0, 20:22]) * (1 - h_mil)
        acq *= not_dom[:, None, :, None, None]
        moved = P[:, :, :, 0] * acq
        P[:, :, :, 0] -= moved
        P[:, :, :, 1] += moved
        # --- adult re-identification of bilinguals (switch home language)
        p_shift, dist, frac, mod, pol, omega = self.transmission(year, P, M, ma_norm)
        rate = p["h0"] * (self.sigma0 / p["sigma_ref"])[None, None, :] * mod[:, :, None] * \
            pol[:, None, None] * (1 - omega) * frac
        hz = 1 - np.exp(-np.clip(rate, 0, 0.5))                         # (R,2,G)
        switch = P[:, :, :, 1, :, 15:65] * hz[..., None, None]          # (R,2,G,S,50)
        P[:, :, :, 1, :, 15:65] -= switch
        inflow = np.einsum("rugk,rugsa->ruksa", dist, switch)
        # switchers into the dominant language are b=1; into another minority
        # language they keep D competence too (they were bilingual)
        P[:, :, :, 1, :, 15:65] += inflow
        return {"acquired": moved.sum(), "switched": switch.sum()}

    # ---------------------------------------------------------------- community flows
    def haredi_exit(self, year: float) -> tuple[float, float]:
        return (_lang_sched_value(self.p["haredi_exit"], year), _lang_sched_value(self.p["haredi_entry"], year))


# ---------------------------------------------------------------------------------
# Census observation model
# ---------------------------------------------------------------------------------
def _dist(**kw) -> dict:
    s = sum(kw.values())
    return {k: v / s for k, v in kw.items()}


def census_mapping(regime: str, c: str, l: str, b: int, u: int, region_code: str) -> dict:
    """Probability that a person in latent state (c, l, b, u) is recorded as
    each census category under the given regime."""
    lt_region = region_code.startswith("LT")
    if regime == "latent":
        return {("tut" if l == "pls" else ("other" if l == "oth" else l)): 1.0}
    if regime == "polish_1931":
        if l == "pl":
            return {"pl": 1.0}
        if l == "be":
            if c == "RC":
                return _dist(pl=.90, be=.10) if b else _dist(pl=.70, be=.30)
            return _dist(be=.68, pl=.27, ru=.05) if b else _dist(be=.88, pl=.10, ru=.02)
        if l == "pls":
            return _dist(tut=.86, be=.04, uk=.04, pl=.06)
        if l == "uk":
            if c == "RC":
                return _dist(pl=.90, uk=.10)
            if c == "GC":
                return _dist(uk=.54, ruth=.36, pl=.10) if b else _dist(uk=.58, ruth=.39, pl=.03)
            return _dist(uk=.92, ruth=.01, pl=.07)
        if l == "rue":
            return _dist(ruth=.85, uk=.10, pl=.05)
        if l == "yi":
            return _dist(yi=.97, he=.03) if c == "JH" else _dist(yi=.88, he=.12)
        if l == "csb":
            return {"pl": 1.0}
        if l == "wym":
            return _dist(pl=.8, de=.2)
        if l == "rom":
            return _dist(pl=.85, other=.15)
        if l == "kdr":
            return {"other": 1.0}
        if l == "lt":
            return _dist(lt=.75, pl=.25) if b else _dist(lt=.92, pl=.08)
        if l == "de":
            return _dist(de=.6, pl=.4) if (c == "RC" and b) else _dist(de=.95, pl=.05)
        if l == "ru":
            return _dist(ru=.9, pl=.1)
        if l == "oth":
            return {"other": 1.0}
        return {l: 1.0} if l in CAT_INDEX else {"other": 1.0}
    if regime == "imperial_1897":
        # Native-language question of the 1897 census; no Kashubian/Rusyn
        # categories (lumped with Polish / "Little Russian").
        if l == "pls":
            return _dist(uk=.55, be=.45)
        if l == "rue":
            return {"uk": 1.0}
        if l == "csb":
            return {"pl": 1.0}
        if l == "yi":
            return {"yi": 1.0}
        if l == "pl" and c in ("JW", "JH"):
            return _dist(yi=.6, pl=.4)
        if l == "pl" and c == "OR":
            return _dist(pl=.5, be=.25, uk=.15, ru=.1)
        if l == "pl" and c == "GC":
            return _dist(uk=.6, pl=.4)
        if l == "be" and c == "RC":
            return _dist(be=.88, pl=.12)
        if l == "oth":
            return {"other": 1.0}
        if l in ("wym", "kdr", "rom"):
            return {"other": 1.0}
        return {l: 1.0} if l in CAT_INDEX else {"other": 1.0}
    if regime == "lithuanian_1923":
        # Nationality census; Catholic Polish-speakers in Lithuania frequently
        # entered as Lithuanians.
        if lt_region and l == "pl" and c == "RC":
            return _dist(pl=.40, lt=.60)
        if l == "pls":
            return {"tut": 1.0}
        if l == "oth":
            return {"other": 1.0}
        return {l: 1.0} if l in CAT_INDEX else {"other": 1.0}
    if regime == "modern_selfid":
        if l == "pls":
            return _dist(pl=.25, be=.25, uk=.25, tut=.25)
        if l == "oth":
            return {"other": 1.0}
        if b and l not in ("pl", "lt"):
            dom = "lt" if lt_region else "pl"
            p_dom = .30 if l in ("csb", "rue", "be", "rom", "wym", "kdr") else .15
            d = {l if l in CAT_INDEX else "other": 1 - p_dom, dom: p_dom}
            return d
        return {l: 1.0} if l in CAT_INDEX else {"other": 1.0}
    raise ValueError(regime)


REGIMES = ["latent", "polish_1931", "imperial_1897", "lithuanian_1923", "modern_selfid"]


def census_matrix(regime: str, region_codes: list[str]) -> np.ndarray:
    """(R, 2, G, 2, n_categories) mapping."""
    R = len(region_codes)
    M = np.zeros((R, 2, NG, 2, len(CENSUS_CATEGORIES)))
    for r, code in enumerate(region_codes):
        for u in (0, 1):
            for g, (c, l) in enumerate(GROUPS):
                for b in (0, 1):
                    for cat, pr in census_mapping(regime, c, l, b, u, code).items():
                        M[r, u, g, b, CAT_INDEX[cat]] += pr
    return M


def census_view(P_rugb: np.ndarray, regime: str, region_codes: list[str], _cache: dict = {}) -> np.ndarray:
    """P_rugb: population (R,2,G,2).  Returns recorded counts (R, n_cat)."""
    key = (regime, tuple(region_codes))
    if key not in _cache:
        _cache[key] = census_matrix(regime, region_codes)
    M = _cache[key]
    return np.einsum("rugb,rugbk->rk", P_rugb, M)
