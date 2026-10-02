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
  Where the group's own-language institutions are incomplete (local share
  below ``completeness_share``) its propensity sigma0 is raised towards a
  diaspora floor ``sigma_diaspora``: scattered speakers and migrants in
  cities shift within two or three generations whatever their nationality
  (Veltman 1983; Alba et al. 2002).
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
``census_mapping`` maps the latent (community, home-language, competence)
state to the categories a language census would have printed: the 1931
Polish census ("tutejszy", "ruski", Catholic Belarusian speakers returned as
Polish) or the 1897 imperial Russian census (vernacular "native language").
Nationality censuses (Poland 1921, Lithuania 1923, modern
self-identification) record national identity instead, which
``plsim.identity`` tracks separately from home language.  Latent and
"as-recorded" series can therefore diverge, as they did historically.
"""
from __future__ import annotations

import numpy as np

from .data.languages import COMMUNITIES, GROUP_INDEX, GROUPS, LANG_INDEX, LANGUAGES, NG, NL, SHIFT_TARGETS
from .economy import piecewise
from .params import matching_patterns, region_lookup

CENSUS_CATEGORIES = ["pl", "uk", "ruth", "be", "tut", "yi", "he", "de", "ru", "lt", "cs", "lv",
                     "csb", "rue", "rom", "kdr", "wym", "other", "jw"]     # jw: Jewish nationality
CAT_INDEX = {c: i for i, c in enumerate(CENSUS_CATEGORIES)}


def _lang_sched_value(spec, year: float) -> float:
    if isinstance(spec, (int, float)):
        return float(spec)
    return piecewise(year, spec)


class LanguageModel:
    def __init__(self, params: dict, regions, dominant: list[str], official: list[list[str]] | None = None):
        self.p = params
        self.regions = regions
        self.codes = [r.code for r in regions]
        self.R = len(regions)
        self.dom = np.array([LANG_INDEX[d] for d in dominant])
        # official languages (R, NL): status floor, schooling, admissible shift targets
        self.official = np.zeros((self.R, NL), dtype=bool)
        for r, langs in enumerate(official or [[d] for d in dominant]):
            self.official[r, [LANG_INDEX[l] for l in langs]] = True
        self.official[np.arange(self.R), self.dom] = True
        self.group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
        self.group_comm = np.array([[c.code for c in COMMUNITIES].index(c) for c, _ in GROUPS])
        # Target matrix: for every group g and every region r, which child groups
        # are admissible targets (boolean (R, G, G)).
        tgt = np.zeros((self.R, NG, NG), dtype=bool)
        for g, (c, l) in enumerate(GROUPS):
            base = set(SHIFT_TARGETS.get((c, l), ()))
            for r in range(self.R):
                ts = set(base)
                ts.update(LANGUAGES[k].code for k in np.where(self.official[r])[0])
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
        # Diaspora floor (second-generation assimilation): where a group lacks
        # local institutions its shift propensity rises towards sigma_diaspora.
        exempt = set(params.get("diaspora_exempt", ()))
        self.dia_floor = np.array([0.0 if (f"{c}:{l}" in exempt or l in exempt) else
                                   max(params.get("sigma_diaspora", 0.0) - s, 0.0)
                                   for (c, l), s in zip(GROUPS, self.sigma0)])
        self.last_sigma = None
        conc = params.get("concentration", {})
        k = np.array([conc.get(f"{c}:{l}", conc.get(l, 1.0)) for c, l in GROUPS], dtype=float)
        self.conc = np.tile(k, (self.R, 1))                                  # (R, G)

    def nest_concentration(self, P: np.ndarray, codes: list[str]) -> None:
        """County runs.  The concentration factors are set for voivodeships;
        part of that concentration is already resolved by the counties.  For
        each voivodeship split into several regions, divide k_L by the
        speakers' clustering across its counties at the start: the mean
        county share of L experienced by L speakers over the voivodeship
        share of L (an isolation index ratio, >= 1).  k never falls below 1."""
        parent = np.array([c.split(".")[0] for c in codes])
        home = np.zeros((self.R, NL))
        np.add.at(home, (slice(None), self.group_lang), P.sum(axis=(1, 3, 4, 5)))
        ratio = np.ones((self.R, NL))
        for q in dict.fromkeys(parent):
            m = parent == q
            if m.sum() < 2:
                continue
            H = home[m]
            n_l = H.sum(axis=0)
            x = n_l / H.sum()
            e = (H * H / np.clip(H.sum(axis=1, keepdims=True), 1e-9, None)).sum(axis=0) / np.clip(n_l, 1e-9, None)
            ratio[m] = np.where(n_l > 0, np.clip(e / np.clip(x, 1e-12, None), 1.0, None), 1.0)
        k = self.conc
        self.conc = np.maximum(k / ratio[:, self.group_lang], np.minimum(k, 1.0))
        self.clustering = ratio

    # ---------------------------------------------------------------- policy
    def status(self, year: float) -> np.ndarray:
        """(R, NL) status/prestige of each language in each region."""
        p = self.p
        s = np.zeros((self.R, NL))
        for l in LANGUAGES:
            s[:, LANG_INDEX[l.code]] = _lang_sched_value(p["status"].get(l.code, p["status"]["default"]), year)
        sr = p.get("status_regions", {})
        for r, code in enumerate(self.codes):
            for pattern in matching_patterns(sr, code):
                for lc, spec in sr[pattern].items():
                    s[r, LANG_INDEX[lc]] = _lang_sched_value(spec, year)
        # The dominant language of a region always has at least the reference
        # status; co-official languages at least the official status.
        s[np.arange(self.R), self.dom] = np.maximum(s[np.arange(self.R), self.dom], 1.0)
        s = np.where(self.official, np.maximum(s, _lang_sched_value(p.get("official_status", 1.0), year)), s)
        return s

    def own_schooling(self, year: float) -> np.ndarray:
        p = self.p
        o = np.zeros((self.R, NG))
        for g, (c, l) in enumerate(GROUPS):
            spec = p["own_schooling"].get(f"{c}:{l}", p["own_schooling"].get(l, 0.0))
            o[:, g] = _lang_sched_value(spec, year)
        osr = p.get("own_schooling_regions", {})
        for r, code in enumerate(self.codes):
            for pattern in matching_patterns(osr, code):
                for key, spec in osr[pattern].items():
                    for g, (c, l) in enumerate(GROUPS):
                        if key == l or key == f"{c}:{l}":
                            o[r, g] = _lang_sched_value(spec, year)
        # speakers of a co-official language are schooled in it
        off_g = self.official[:, self.group_lang]                          # (R,G)
        o = np.where(off_g, np.maximum(o, _lang_sched_value(p.get("official_schooling", 0.9), year)), o)
        # own-language schooling is meaningless for the dominant language
        o[self.group_lang[None, :] == self.dom[:, None]] = 0.0
        return np.clip(o, 0, 1)

    def pressure(self, year: float) -> np.ndarray:
        p = self.p
        return np.array([_lang_sched_value(region_lookup(p["pressure"], code), year) for code in self.codes])

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
        sL = np.clip(self.conc[:, None, :] * xL, 0, 0.95)
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
        # A diaspora (institutionally incomplete) shifts at least at about the
        # rate of second-generation immigrants (Alba et al. 2002): the group's
        # propensity is raised towards sigma_diaspora by (1 - completeness).
        sig = self.sigma0[None, None, :] + self.dia_floor[None, None, :] * (1 - complete)    # (R,2,G)
        self.last_sigma = sig
        base = sig * mod[:, :, None] * pol[:, None, None] * (1 - omega) * frac
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
        rate = p["h0"] * (self.last_sigma / p["sigma_ref"]) * mod[:, :, None] * \
            pol[:, None, None] * (1 - omega) * frac
        hz = 1 - np.exp(-np.clip(rate, 0, 0.5))                         # (R,2,G)
        switch = P[:, :, :, 1, :, 15:65] * hz[..., None, None]          # (R,2,G,S,50)
        P[:, :, :, 1, :, 15:65] -= switch
        inflow = np.einsum("rugk,rugsa->ruksa", dist, switch)
        # switchers into the dominant language are b=1; into another minority
        # language they keep D competence too (they were bilingual)
        P[:, :, :, 1, :, 15:65] += inflow
        flows = dist * switch.sum(axis=(3, 4))[..., None]                 # (R,2,G_from,G_to)
        return {"acquired": moved.sum(), "switched": switch.sum(), "flows": flows}

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
    if regime == "latent":
        return {("tut" if l == "pls" else ("other" if l == "oth" else l)): 1.0}
    if regime == "polish_1931":
        if l == "pl":
            return {"pl": 1.0}
        if l == "be":
            if c == "RC":
                return _dist(pl=.90, be=.10) if b else _dist(pl=.70, be=.30)
            return _dist(be=.63, pl=.32, ru=.05) if b else _dist(be=.86, pl=.12, ru=.02)
        if l == "pls":
            return _dist(tut=.97, be=.01, pl=.02)
        if l == "uk":
            if c == "RC":
                return _dist(pl=.90, uk=.10)
            if c == "GC":
                return _dist(uk=.50, ruth=.34, pl=.16) if b else _dist(uk=.56, ruth=.38, pl=.06)
            return _dist(uk=.89, ruth=.01, pl=.10)
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
    raise ValueError(regime)


# Language censuses (home language / mother tongue) read the latent language
# state; nationality censuses read national identity (plsim.identity).
LANGUAGE_REGIMES = ["latent", "polish_1931", "imperial_1897"]
REGIMES = LANGUAGE_REGIMES + ["polish_1921", "lithuanian_1923", "modern_selfid"]


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
