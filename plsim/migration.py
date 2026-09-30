"""Internal and international migration.

Internal
--------
* **Rural -> urban within a region.**  Each region moves towards an income-
  dependent urbanisation target (Davis & Henderson 2003); the flow closes a
  fraction of the gap each year.  This is the reduced form of the Lewis (1954)
  surplus-labour / Harris & Todaro (1970) expected-income mechanism: rural
  "agrarian overpopulation" (estimated at 5-8 million in the 1930s) drains
  towards urban jobs as those jobs appear.
* **Inter-regional.**  A production-constrained spatial-interaction model
  (Wilson 1971; Stouffer 1940 intervening opportunities as an option via
  the radiation model of Simini et al. 2012):

      T_rj = O_r * W_j exp(-beta t_rj) Aff_gj / sum_k W_k exp(-beta t_rk) Aff_gk

  where O_r rises with the income gap to the national mean, W_j is urban
  mass x relative income, t_rj comes from the *current* transport network
  (so new railways and roads re-route migration), and Aff is an ethnic-
  network / language-barrier affinity term.
* **Age.**  All flows use Rogers & Castro (1981) model migration schedules.
* **Planned settlement.**  Optional flows of Polish Catholic smallholders to
  the eastern voivodeships (military and civilian "osadnictwo", Polesie
  drainage schemes).

International
-------------
Net emigration follows the "migration hump" (Zelinsky 1971; Hatton &
Williamson 1998, 2005; de Haas 2010): propensity rises with income from very
low levels (people can afford to leave), peaks at roughly a third of the
destination income and falls as the gap closes, turning into net
immigration at about three quarters of the frontier.  A time-varying
"openness" factor captures destination policies (US quotas from 1924, the
Depression, European guest-worker demand 1955-73, later free movement).
Group-specific channels carry the Jewish emigration (Palestine/Americas; ~400 k
recorded Jewish emigrants from interwar Poland) and German emigration to
the Reich.
"""
from __future__ import annotations

import numpy as np

from .data.languages import COMMUNITIES, GROUPS, LANG_INDEX, NG
from .economy import piecewise

AGES = np.arange(101)


def rogers_castro(a1=0.02, alpha1=0.10, a2=0.06, mu2=20.5, alpha2=0.10, lambda2=0.40, c=0.003,
                  ages=AGES) -> np.ndarray:
    x = ages.astype(float)
    return a1 * np.exp(-alpha1 * x) + a2 * np.exp(-alpha2 * (x - mu2) - np.exp(-lambda2 * (x - mu2))) + c


def normalised_schedule(**kw) -> np.ndarray:
    s = rogers_castro(**kw)
    return s / s[:65].mean()


def hump(z: float, z_star: float, shape: float) -> float:
    """Migration hump, 1 at z = z_star."""
    z = max(z, 1e-3)
    return (z / z_star) ** shape * np.exp(shape * (1 - z / z_star))


class MigrationModel:
    def __init__(self, params: dict, regions, dominant: list[str]):
        self.p = params
        self.regions = regions
        self.R = len(regions)
        self.codes = [r.code for r in regions]
        self.dom = np.array([LANG_INDEX[d] for d in dominant])
        self.sched_internal = normalised_schedule(**params["rogers_castro"])
        self.sched_emig = normalised_schedule(**params["rogers_castro_emig"])
        comm_codes = [c.code for c in COMMUNITIES]
        mob = params["mobility"]
        self.mobility = np.array([mob.get(f"{c}:{l}", mob.get(c, 1.0)) for c, l in GROUPS])
        emig = params["emigration_base"]
        self.emig_base = np.array([emig.get(f"{c}:{l}", emig.get(c, emig["default"])) for c, l in GROUPS])
        self.group_lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
        self.group_comm = np.array([comm_codes.index(c) for c, _ in GROUPS])
        self.is_jewish = np.isin(self.group_comm, [comm_codes.index("JW"), comm_codes.index("JH")])
        self.is_haredi = self.group_comm == comm_codes.index("JH")
        self.is_german = self.group_lang == LANG_INDEX["de"]
        self.country = np.array([r.country for r in regions])
        self.logit_fe = None

    # ---------------------------------------------------------------- rural-urban
    def urbanisation(self, P: np.ndarray, u_target: np.ndarray, year: int) -> dict:
        p = self.p
        tot = P.sum(axis=(2, 3, 4, 5))            # (R,2)
        U = tot[:, 1] / tot.sum(axis=1)
        # regional fixed effects (industrial Silesia, agrarian Polesie) decay slowly
        if self.logit_fe is None:
            lu = np.log(np.clip(U, 1e-3, 0.999) / (1 - np.clip(U, 1e-3, 0.999)))
            lt = np.log(u_target / (1 - u_target))
            self.logit_fe = lu - lt
            self.fe_year0 = year
        decay = np.exp(-(year - self.fe_year0) / p["urban_fe_decay_years"])
        lt = np.log(u_target / (1 - u_target)) + self.logit_fe * decay
        target = 1 / (1 + np.exp(-lt))
        gap = np.clip(target - U, 0, None) / np.clip(1 - U, 1e-6, None)
        rate = p["urban_kappa"] * gap + p["urban_min"]
        rate = np.where(U > 0.995, 0.0, rate)
        flow = P[:, 0] * (rate[:, None, None, None, None] * self.sched_internal[None, None, None, None, :])
        flow = np.minimum(flow, P[:, 0] * 0.5)
        P[:, 0] -= flow
        P[:, 1] += flow
        return {"rural_urban": flow.sum(axis=(1, 2, 3, 4))}

    # ---------------------------------------------------------------- inter-regional
    def interregional(self, P: np.ndarray, t_reg: np.ndarray, y_reg: np.ndarray, x_lang: np.ndarray,
                      year: int, settlement: dict | None = None, y_dest: np.ndarray | None = None) -> np.ndarray:
        """y_reg: regional mean income (origin push); y_dest: urban income at the
        destination (most movers go to towns), defaults to y_reg."""
        p = self.p
        ybar = (y_reg * P.sum(axis=(1, 2, 3, 4, 5))).sum() / P.sum()
        push = 1 + p["push_income"] * np.clip(np.log(ybar / y_reg), 0, None)
        base = np.array([p["out_rate_rural"], p["out_rate_urban"]])
        O_rate = base[None, :] * push[:, None] * piecewise(year, p["internal_intensity"])  # (R,2)
        out = P * (O_rate[:, :, None, None, None, None] * self.mobility[None, None, :, None, None, None]
                   * self.sched_internal[None, None, None, None, None, :])
        out = np.minimum(out, P * 0.3)
        # destination attractiveness
        pop_r = P.sum(axis=(2, 3, 4, 5))            # (R,2)
        yd = y_reg if y_dest is None else y_dest
        W = (pop_r[:, 1] + p["rural_weight"] * pop_r[:, 0]) ** p["mass_exponent"] * \
            (yd / yd.mean()) ** p["income_elasticity"]
        det = np.exp(-p["beta_time"] * t_reg)       # (R,R)
        np.fill_diagonal(det, 0.0)
        # cross-border (PL <-> LT) friction
        cross = self.country[:, None] != self.country[None, :]
        det = det * np.where(cross, p["cross_border_factor"], 1.0)
        # affinity: share of own-language speakers at destination (ethnic networks)
        xl = x_lang.mean(axis=1)                     # (R, NL)
        aff = (xl[:, self.group_lang] + p["affinity_floor"]) ** p["affinity_power"]   # (R_dest, G)
        prob = det[:, :, None] * W[None, :, None] * aff[None, :, :]    # (R_from, R_to, G)
        prob /= np.clip(prob.sum(axis=1, keepdims=True), 1e-300, None)
        out_fg = out.sum(axis=1)                     # (R,G,B,S,A)
        same_dom = (self.dom[:, None] == self.dom[None, :])[:, :, None]
        inflow = np.einsum("fgbsa,ftg->tgbsa", out_fg, prob * same_dom)
        cross_in = np.einsum("fgbsa,ftg->tgbsa", out_fg, prob * ~same_dom)
        # Competence refers to the destination's dominant language: migrants
        # crossing a language border arrive monolingual (unless native in it).
        inflow[:, :, 0] += cross_in.sum(axis=2)
        P -= out
        us = p["dest_urban_share"]
        P[:, 1] += inflow * us
        P[:, 0] += inflow * (1 - us)
        # settlement programme (rural RC:pl families east)
        if settlement:
            self._settle(P, settlement, year)
        flows = np.einsum("fgbsa,ftg->ft", out_fg, prob)
        return flows

    def _settle(self, P, s: dict, year: int):
        n = piecewise(year, s["per_year"])
        if n <= 0:
            return
        from .data.languages import GROUP_INDEX
        g = GROUP_INDEX[("RC", "pl")]
        orig = np.array([s["origins"].get(c, 0.0) for c in self.codes])
        dest = np.array([s["destinations"].get(c, 0.0) for c in self.codes])
        if orig.sum() <= 0 or dest.sum() <= 0:
            return
        orig /= orig.sum()
        dest /= dest.sum()
        fam = np.zeros(101)
        fam[0:15] = 0.7
        fam[20:40] = 1.0
        fam[40:50] = 0.5
        for r in range(self.R):
            if orig[r] == 0:
                continue
            avail = P[r, 0, g, 1] * fam[None, :]
            k = min(n * orig[r] / max(avail.sum(), 1.0), 0.05)
            moved = avail * k
            P[r, 0, g, 1] -= moved
            for d in range(self.R):
                if dest[d] > 0:
                    P[d, 0, g, 1] += moved * dest[d]

    # ---------------------------------------------------------------- international
    def international(self, P: np.ndarray, year: int, y_nat: float, y_frontier: float,
                      y_reg: np.ndarray) -> dict:
        p = self.p
        z = y_nat / y_frontier
        openness = piecewise(year, p["openness"])
        h = hump(z, p["hump_peak"], p["hump_shape"])
        # net emigration fades to zero near the immigration threshold
        fade = 1 / (1 + np.exp((z - p["immigration_threshold"]) / 0.04))
        ybar = (y_reg * P.sum(axis=(1, 2, 3, 4, 5))).sum() / P.sum()
        push = (ybar / y_reg) ** p["emig_push_elasticity"]           # (R,)
        rate_g = self.emig_base * h * openness * fade                # (G,)
        jew = piecewise(year, p["jewish_channel"])
        ger = piecewise(year, p["german_channel"])
        extra = np.where(self.is_jewish, jew * np.where(self.is_haredi, p["haredi_channel_factor"], 1.0), 0.0)
        extra = extra + np.where(self.is_german, ger, 0.0)
        rate = (rate_g[None, :] * push[:, None] + extra[None, :])    # (R,G)
        # Lithuania's own openness (e.g. emigration to Latin America in the 1920s)
        lt_mask = self.country == "LT"
        rate[lt_mask] *= p["lithuania_emig_factor"]
        E = P * (rate[:, None, :, None, None, None] * self.sched_emig[None, None, None, None, None, :])
        E = np.minimum(E, P * 0.2)
        P -= E
        emigrants = E.sum(axis=(1, 3, 4, 5))                          # (R,G)
        # net immigration once income is high
        imm_rate = p["immigration_max"] / (1 + np.exp(-(z - p["immigration_threshold"]) / 0.04))
        total = P.sum()
        imm = imm_rate * total
        immigrants = np.zeros((self.R, NG))
        if imm > 0:
            from .data.languages import GROUP_INDEX
            urb = P[:, 1].sum(axis=(1, 2, 3, 4))
            w = urb * (y_reg / ybar) ** 2
            w = w / w.sum()
            age = self.sched_emig / self.sched_emig.sum()
            comp = p["immigrant_composition"]
            for key, share in comp.items():
                c, l = key.split(":")
                dom_g = None
                if l == "DOM":
                    for r in range(self.R):
                        lang = "lt" if self.country[r] == "LT" else "pl"
                        g = GROUP_INDEX[("RC", lang)]
                        add = imm * share * w[r] * age
                        P[r, 1, g, 1, 0] += add * 0.5
                        P[r, 1, g, 1, 1] += add * 0.5
                        immigrants[r, g] += add.sum()
                    continue
                g = GROUP_INDEX[(c, l)] if dom_g is None else dom_g
                for r in range(self.R):
                    add = imm * share * w[r] * age
                    P[r, 1, g, 0, 0] += add * 0.55
                    P[r, 1, g, 0, 1] += add * 0.45
                    immigrants[r, g] += add.sum()
        return {"emigrants": emigrants, "immigrants": immigrants, "z": z}

    # ---------------------------------------------------------------- bookkeeping
    def reset_competence(self, P: np.ndarray) -> None:
        """Groups whose home language is the region's dominant language are
        competent by definition."""
        for r in range(self.R):
            gm = self.group_lang == self.dom[r]
            P[r, :, gm, 1] += P[r, :, gm, 0]
            P[r, :, gm, 0] = 0.0
