"""Default parameters (the 'baseline' counterfactual) and scenario merging.

Every value is either (a) taken from a cited source, (b) calibrated to an
observed 1931-1939 aggregate (see ``plsim.validate``), or (c) a scenario
assumption documented in docs/SCENARIOS.md.  Items in ``UNCERTAINTY`` are
re-drawn in Monte-Carlo ensembles.
"""
from __future__ import annotations

import copy
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "meta": {"name": "baseline", "description": "No WW2; Polish-Lithuanian federation; moderate convergence"},
    "start_year": 1932,          # state at 1 Jan 1932 = census of 9 Dec 1931
    "end_year": 2032,
    "seed": 1931,
    "include_lithuania": True,
    "federation": True,          # Lithuania joined in a federal union (reopened Vilnius-Kaunas links etc.)
    "include_belarus": False,    # Soviet Belarus (BSSR of 1926) as part of Poland (data/bssr.py)
    "include_krai_east": False,  # Latgale, Nevel-Sebezh-Velizh, east Mogilev: the rest of the 1897 north-western
                                 # governorates (data/krai_east.py)
    "governorates": {},          # {group: [governorate, ...]}: members drawn on the 1897 borders (data/governorates.py)
    "governorates_keep_outside": ["PL"],   # 1932 states whose land outside every group stays in the run
    "separate_states": [],       # members that are sovereign states beside Poland: own economy (plsim/economy.py)
    "curzon_count": "language",  # who is a Pole for the equal-exchange line: "language" or "identity" (plsim/curzon.py)
    # 1931 starting point (see plsim/data/census1931.py and docs/DATA_SOURCES.md):
    # religion_corrected = Tomaszewski (1985), the mainstream scholarly correction
    # of the census; official = the census as printed; vernacular = upper bound
    # (Kubijovyč 1983, 1897-anchored Catholic Belarusian speech).
    "census_variant": "religion_corrected",
    # Lithuania: research = ~150 k Poles (historians' middle estimate);
    # census_1923 = the census (65.6 k Poles); polish_claim_1923 = ~202 k;
    # imperial_1897 = 1897 Kovno-governorate language shares.
    "lt_variant": "research",
    # Contact language of each region: the language bilinguals are competent
    # in, and the default target of shift. "auto:pl,be" picks, per region, the
    # listed language with the most speakers in 1931.
    "dominant_language": {"default": "pl", "LT_*": "lt"},
    # Official languages of each region (status floor, schooling, admissible
    # shift target); "all" makes every language official. Regions not listed
    # have the dominant language alone. Polish is co-official in every
    # autonomy, here the Lithuanian member of the federation.
    "official_languages": {"LT_*": ["lt", "pl"]},
    # Federal member state of each region (migration friction between members).
    "members": {"default": "PL", "LT_*": "LT"},
    # Spatial units: "counties" runs every voivodeship as its 1931 powiaty
    # (see plsim/data/counties.py); [] runs the 23 voivodeships; a list of
    # voivodeship codes uses the named splits of plsim/data/subregions.py.
    "partition": "counties",
    # Regions or counties left out of the state (codes, parent codes, wildcards
    # or region_groups names): their people, towns and land are foreign.
    "exclude": [],
    "snapshot_years": [1932, 1939, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2032],

    # ------------------------------------------------------------------ demography
    "fertility": {
        "tfr_scale": 1.07,
        "community_mult": {"RC": 1.0, "GC": 0.97, "OR": 1.05, "JW": 0.70, "JH": 1.15, "PR": 0.85, "OT": 0.90},
        "group_mult": {"RC:rom": 1.35, "OT:kdr": 0.8},
        "pretransition_U": 5.2,          # U: TFR level at which decline starts (Alkema); max(U, current + onset_offset)
        # Calibrated on the historical scenario (plsim/history_check.py): rural Poland kept about 3 children
        # per woman from 1970 to 1980 (2.99, 2.92) and 2.44 in 1990, the towns 1.7-1.9, and the Soviet-ruled
        # west of Ukraine and Belarus fell to about 2.6 by 1970. The decline is already under way in 1931 where
        # fertility is high (onset_offset), is slower in the countryside (pace_stratum: rural, urban) and ends
        # higher there (D4_rural_offset; phase3_mu_rural_offset for the long run).
        "onset_offset": 0.5, "pace_stratum": [0.7, 1.0], "D4_rural_offset": 0.8, "phase3_mu_rural_offset": 0.3,
        "d_max": 0.62,                   # max 5-year decrement (Alkema 2011 world medians ~0.5-1.0)
        "D1": 1.2, "D3": 1.2, "D4": 1.75, "phase3_entry_margin": 0.12,
        # pace_min 0.55 (was 0.40) and Orthodox pace 1.0 (was 0.85): the poorest eastern lands start
        # their decline sooner, matching rural eastern Poland of 1960-90 (2.9 children in 1970, 2.4-2.6
        # in 1990) and the Orthodox of Podlasie, who had fewer children than their Catholic neighbours
        "pace_M0": 0.20, "pace_M1": 0.75, "pace_min": 0.75, "pace_max": 1.00,
        "community_pace": {"RC": 1.0, "GC": 0.9, "OR": 1.0, "JW": 1.1, "JH": 0.12, "PR": 1.05, "OT": 1.0},
        "phase3_mu": {"default": 1.45, "JH": 2.8, "JW": 1.60, "PR": 1.50},
        "phase3_rho": 0.93,
        "phase3_sd": 0.025,
        "period": [[1931, 1.0], [1933, 0.965], [1938, 0.91], [1945, 0.95], [1950, 1.0]],
        "baby_boom": {"amplitude": 0.10, "centre": 1956, "width": 9.0},
        "period_sd": 0.012,
        "postponement": {"start": 1982, "rate": 0.13, "max": 4.0},
        "srb": 1.06,
        "struct_weight_current": 0.35,   # age structure built on 35% current + 65% pre-1914 fertility
        "struct_tfr_past": 5.5,
    },
    "mortality": {
        "community_e0_adj": {"JW": 4.0, "JH": 3.0, "PR": 2.0, "OR": -0.5},
        "urban_e0_adj": 1.0,
        "group_e0_adj": {"RC:rom": -8.0},
        "adj_halflife": 35.0,
        # gap_max: the gap to best practice at zero income, which antibiotics and mass vaccination halved
        # after the war (Poland's women were 3.6 years behind best practice in 1960 at a third of its income)
        "gap_min": 1.5, "gap_max": [[1931, 12.0], [1945, 12.0], [1955, 6.0], [2032, 6.0]], "gap_power": 1.5,
        "catchup_pre": 0.030, "catchup_post": 0.120,
        "sex_gap": [[1931, 3.2], [1960, 5.0], [1985, 6.6], [2010, 5.6], [2032, 4.8]],
        "frontier_slope": 0.243, "frontier_slope_post2000": 0.20,
        "shock_sd": 0.25,
    },

    # ------------------------------------------------------------------ economy
    "economy": {
        "y0_1931": 1800.0,                     # 1990 GK$ (Maddison-consistent; 1929 ~2,100)
        "lithuania_rel": 0.95,
        "frontier_1931": 4300.0,               # western European average, depressed 1931
        "frontier_growth": [[1931, 0.025], [1939, 0.018], [1950, 0.027], [1974, 0.019], [2008, 0.009]],
        "historical_growth": {"1932": -0.05, "1933": -0.01, "1934": 0.02, "1935": 0.03, "1936": 0.04,
                              "1937": 0.06, "1938": 0.05},
        "kappa": [[1931, 0.55], [1960, 0.64], [2032, 0.70]],
        "convergence_beta": 0.02,
        "shock_sd": 0.022, "crisis_prob": 0.04, "crisis_size": -0.05,
        "regional_beta": 0.015, "regional_persistence": 0.45, "ma_elasticity": 0.12,
        "regional_programmes": {   # extra log growth per year (COP 1936-, Gdynia/Pomerania)
            "LWO": [[1936, 0.0], [1937, 0.006], [1950, 0.004], [1960, 0.0]],
            "KIE": [[1936, 0.0], [1937, 0.004], [1950, 0.002], [1960, 0.0]],
            "LUB": [[1936, 0.0], [1937, 0.004], [1950, 0.002], [1960, 0.0]],
            "POM": [[1931, 0.006], [1945, 0.002], [1955, 0.0]],
        },
        "equalisation": [[1931, 0.0], [1939, 0.0], [1940, 0.006], [1954, 0.006], [1955, 0.002], [2032, 0.002]],
        "urban_rural_ratio": [[1931, 2.2], [1970, 1.5], [2000, 1.25], [2032, 1.2]],
        "literacy_rate": 0.045,
        "enrollment_rate": 0.06,
        "vehicles_1938_per_1000": 1.27,       # 44,200 motor vehicles on 1 Jan 1938
        "gompertz": {"gamma": 750.0, "alpha": -10.0, "beta": -0.239, "adjust": 0.15},
        "urbanisation": {"u_max": 0.75, "slope": 1.2, "y50": 3000.0},
        "infra_share_gdp": [[1931, 0.0040], [1938, 0.0055], [1939, 0.0080], [1954, 0.0100], [1970, 0.0110],
                            [1995, 0.0120], [2032, 0.0100]],
    },

    # ------------------------------------------------------------------ infrastructure
    "infrastructure": {
        "gravity_beta": 0.30, "ma_theta": 0.25, "border_factor": 0.12,
        "trip_rate": [[1931, 4.0], [1960, 12.0], [1990, 25.0], [2032, 35.0]],
        "vot_share": 0.35, "freight_uplift": 0.8, "discount": 0.05, "life": 40,
        "demand_growth_factor": 1.25,
        "bcr_threshold": 1.0, "account_cap_years": 6, "appraisal_interval": 2,
        # yearly operation and maintenance (incl. periodic renewal) as a share
        # of the capital cost, counted in the appraisal over the project life
        "om_share": {"express": 0.015, "motorway": 0.02},
        # share of the local (hinterland) traffic benefit earned by a
        # limited-access road; the rest stays on the old road. Calibrated so
        # that the baseline has about 19 km of expressway and motorway per
        # 1000 km2 by 2032 (Czechia, Hungary ~18-21; Spain, France ~35)
        "local_share_limited": {"express": 0.65, "motorway": 0.3},
        "equity_weight": [[1931, 0.3], [1939, 0.3], [1940, 1.0], [1954, 1.0], [1955, 0.4], [2032, 0.4]],
        "bus_access": [[1931, 0.25], [1950, 0.45], [1965, 0.70], [1980, 0.80]],
        "local_trip_rate": [[1931, 20.0], [1960, 40.0], [1990, 80.0], [2032, 100.0]],
        "rail_budget_share": [[1931, 0.55], [1950, 0.45], [1970, 0.35], [2000, 0.40], [2032, 0.40]],
        "hsr_min_town_k": 150,
        "closure_motorisation": 180.0, "closure_rate": 0.02,
        "enable_planned": True, "planned_delay": 0,
        "town_ma_elasticity": 1.0, "town_noise": 0.004,
        "town_bonus": {"Gdynia": [[1931, 0.16], [1939, 0.03], [1950, 0.01], [1960, 0.0]],
                       "Rozwadów": [[1931, 0.0], [1937, 0.25], [1945, 0.05], [1955, 0.0]],
                       "Klaipėda": [[1931, 0.02], [1960, 0.0]]},
    },

    # ------------------------------------------------------------------ migration
    "migration": {
        "rogers_castro": {"a1": 0.02, "alpha1": 0.10, "a2": 0.06, "mu2": 20.5, "alpha2": 0.10, "lambda2": 0.40, "c": 0.003},
        "rogers_castro_emig": {"a1": 0.012, "alpha1": 0.10, "a2": 0.08, "mu2": 22.0, "alpha2": 0.12, "lambda2": 0.45, "c": 0.002},
        "urban_kappa": 0.10, "urban_min": 0.002, "urban_fe_decay_years": 60.0,
        "out_rate_rural": 0.004, "out_rate_urban": 0.006,
        "internal_intensity": [[1931, 1.0], [1960, 1.3], [2000, 1.0]],
        "push_income": 1.5, "rural_weight": 0.2, "income_elasticity": 1.0, "mass_exponent": 0.75,
        "beta_time": 0.12,
        "cross_border_factor": 0.10, "affinity_floor": 0.02, "affinity_power": 0.40,
        "dest_urban_share": 0.78,
        "mobility": {"JW": 1.3, "JH": 0.9, "GC": 0.6, "OR": 0.7, "PR": 0.8, "RC": 1.0, "OT": 1.0,
                     "OR:pls": 0.4, "RC:rom": 1.5},
        "settlement": {
            "per_year": [[1931, 8000], [1939, 12000], [1955, 12000], [1965, 0]],
            "origins": {"KRA": 1.0, "KIE": 1.0, "LUB": 0.6, "WAR": 0.6, "LWO": 0.5},
            # the military settlers of 1921-39 by voivodeship (households): Wołyń 41.5 %,
            # Nowogródek 21.7, Wilno 13.3, Polesie 12.6, Białystok 10.9 (in its Grodno-
            # governorate east, on the Grodno and Wołkowysk estates)
            "destinations": {"WOL": 0.415, "NOW": 0.217, "WIL": 0.133, "POL": 0.126,
                             "BIA.grodno": 0.055, "BIA.wolkowysk": 0.054},
        },
        # international
        "emigration_base": {"default": 0.0025, "RC:pl": 0.0032, "RC:lt": 0.0035, "GC": 0.0028,
                            "OR": 0.0018, "OR:pls": 0.0008, "JW": 0.0028, "JH": 0.0014, "PR": 0.0021},
        "hump_peak": 0.35, "hump_shape": 2.5,
        "openness": [[1931, 0.12], [1939, 0.15], [1946, 0.8], [1955, 1.0], [1973, 1.0], [1977, 0.55],
                     [1990, 0.8], [2032, 0.8]],
        "emig_push_elasticity": 0.8,
        "jewish_channel": [[1931, 0.0035], [1939, 0.0035], [1948, 0.0030], [1960, 0.0015], [1980, 0.0008], [2032, 0.0005]],
        "haredi_channel_factor": 0.5,
        "german_channel": [[1931, 0.008], [1939, 0.004], [1950, 0.002], [1970, 0.001], [2032, 0.0005]],
        "lithuania_emig_factor": 1.0,
        "immigration_threshold": 0.74, "immigration_max": 0.004,
        "immigrant_composition": {"RC:DOM": 0.45, "OT:oth": 0.40, "OR:uk": 0.15},
    },

    # ------------------------------------------------------------------ language
    "language": {
        "a": 1.31,                      # Abrams & Strogatz (2003) fitted exponent
        "m_mono": 0.15,                 # shift propensity of monolingual vs bilingual mothers
        "max_shift": 0.90,
        "sigma_ref": 0.2,
        # history-matched classes (plsim/calibration.py, outputs/calibration):
        # same-faith vernaculars (RC:be, RC:pls, RC:csb), same-faith national
        # minorities (RC:lt, RC:uk, RC:de, RC:cs, RC:lv) and different-faith
        # ones (GC:uk, OR:uk, GC:rue, PR:de ...) each move by one factor
        "sigma0": {"default": 0.20,
                   "RC:pl": 0.05, "RC:be": 0.38, "RC:lt": 0.37, "RC:de": 0.46, "RC:csb": 0.138, "RC:cs": 0.77,
                   "RC:uk": 0.62, "RC:wym": 0.80, "RC:rom": 0.04, "RC:pls": 0.207, "RC:ru": 0.30, "RC:lv": 0.62,
                   "RC:oth": 0.30,
                   "GC:uk": 0.036, "GC:rue": 0.06, "GC:pl": 0.03,
                   "OR:uk": 0.036, "OR:be": 0.22, "OR:pls": 0.45, "OR:ru": 0.12, "OR:pl": 0.03, "OR:rue": 0.048,
                   "OR:cs": 0.15,
                   "JW:yi": 0.50, "JW:de": 0.30, "JW:ru": 0.30, "JW:lt": 0.20,
                   "JH:yi": 0.02,
                   "PR:de": 0.072, "PR:pl": 0.02, "PR:lt": 0.06, "PR:lv": 0.09, "PR:cs": 0.12,
                   "OT:kdr": 0.14, "OT:ru": 0.20, "OT:be": 0.30, "OT:oth": 0.30},
        "institutional": {"uk": 0.25, "GC:uk": 0.30, "be": 0.05, "JW:yi": 0.08, "JH:yi": 0.50, "de": 0.20,
                          "lt": 0.30, "csb": 0.05, "rue": 0.10, "pls": 0.0, "cs": 0.10, "ru": 0.10,
                          "kdr": 0.20, "wym": 0.0, "rom": 0.35, "lv": 0.10, "pl": 0.0},
        # spatial concentration of speakers relative to the regional cell
        # (enclaves are locally dominant even when regionally tiny)
        "concentration": {"wym": 300.0, "kdr": 60.0, "rue": 20.0, "cs": 15.0, "de": 5.0, "RC:de": 1.5,
                          "csb": 2.5, "lt": 4.0, "lv": 5.0, "rom": 4.0, "yi": 1.3, "pls": 1.1, "be": 1.4,
                          "uk": 1.25, "ru": 2.5, "pl": 3.0, "oth": 3.0},
        # clustering measured inside a county (replaces the factor above there): the Lithuanians of
        # Suwałki county live in Puńsk (75 % Lithuanian in 2002) and the villages round Sejny, a local
        # share of about 0.55 against 4.5 % of the county
        "concentration_regions": {"BIA.suwalki": {"lt": 10.0}},
        "official_status": 1.0,         # status floor of an official language (number or schedule)
        "official_schooling": 0.9,      # own-language schooling for speakers of an official language (number or schedule)
        "school_weight": 0.5,
        "completeness_share": 0.25,     # local own-language share at which institutions are complete
        # shift propensity approached by an institutionally incomplete group
        # (diaspora, migrants' children); groups listed keep their own sigma0
        "sigma_diaspora": 0.54,
        "diaspora_exempt": ["JH:yi", "RC:rom", "OT:kdr", "RC:wym"],
        "own_school_blocks": 0.7,
        "status": {"default": 0.1, "pl": 1.0, "lt": 0.35, "uk": 0.35, "be": 0.15, "pls": 0.05,
                   "yi": [[1931, 0.25], [1970, 0.18]], "de": [[1931, 0.55], [1960, 0.40]],
                   "ru": [[1931, 0.30], [1960, 0.20]], "csb": 0.10, "rue": 0.12, "cs": 0.20, "lv": 0.20,
                   "rom": 0.05, "kdr": 0.05, "wym": 0.05, "oth": 0.10},
        "status_regions": {"LT_*": {"lt": 1.0, "pl": 0.60, "de": 0.40},
                           "LT_KLA": {"lt": 1.0, "de": 0.90},
                           "WIL": {"lt": 0.40}},
        "own_schooling": {"uk": [[1931, 0.15], [1950, 0.25]], "GC:uk": [[1931, 0.20], [1950, 0.30]],
                          "be": 0.03, "lt": 0.50, "de": 0.50, "JW:yi": 0.20, "JH:yi": 0.70, "csb": 0.0,
                          "rue": 0.10, "cs": 0.50, "ru": 0.10, "lv": 0.50, "pls": 0.0, "kdr": 0.30, "pl": 0.0},
        "own_schooling_regions": {"LT_*": {"pl": 0.30, "RC:pl": 0.30, "de": 0.50, "ru": 0.20}},
        "pressure": {"default": [[1931, 1.0], [1950, 0.9], [1990, 0.8]], "LT_*": 0.8},
        "urban_mult": 0.6, "mod_base": 0.5, "mod_slope": 1.0, "access_mult": 0.15,
        "h0": 0.0025,
        # marriage across languages (language.horizontal): yearly rate for bilingual adults of 20-34, times
        # the chance of a partner from outside the group (homogamy odds H against the local own share) and
        # the pull of the other language; Jews hardly married out. Half the mixed households raise their
        # children in the partner's religion (the Galician rule: sons the father's rite, daughters the mother's)
        "exogamy": 0.20, "exogamy_homophily": 38.0, "exogamy_mult": {"JW": 0.1, "JH": 0.0},
        "exogamy_rite": 0.5,            # mixed households raising their children in the partner's religion
        "acq_school": 0.36, "acq_adult": 0.022, "acq_urban_bonus": 0.8, "acq_military": 0.35,
        "conscription": [[1931, 1.0], [1990, 0.8], [2008, 0.0]],
        "haredi_exit": [[1931, 0.20], [1970, 0.15], [2000, 0.12]],
        "haredi_entry": 0.01,
    },

    # ------------------------------------------------------------------ national identity
    "identity": {                      # plsim/identity.py
        "follow": 0.6,                 # language switchers taking the identity of the new language
        "nation_building": 0.02,       # yearly rate x modernisation: "local" -> national identity
        # yearly rate x pressure x modernisation: pull of the state nation. Calibrated on the historical
        # scenario against the 2002 census, on the Lithuanians and Kashubians, whose home language the model
        # gets about right (2002: 5.8 and 4.7 thousand, census 6 and 5; it was 0.008, giving 12 and 37)
        "assimilation": 0.05,
        "anchor": 0.85,                # reduction of that pull when identity matches home language...
        # ...in full only where that language has this status or this own-language schooling, in proportion
        # below (a stigmatised, unschooled language anchors identity less)
        "anchor_status": 0.35, "anchor_schooling": 0.3,
        "compat": {"RC": 1.0, "GC": 0.25, "OR": 0.3, "JW": 0.6, "JH": 0.0, "PR": 0.5, "OT": 0.5},
    },

    # ------------------------------------------------------------------ spatial downscaling (maps only)
    "spatial": {
        "anchor_sigma_km": 22.0,     # county-anchor interpolation kernel
        "sigma_km": 10.0,            # neighbourhood kernel (Prochazka & Vogl 2017)
        "cutoff_sigmas": 3.0,
        "town_sigma_km": 8.0,        # town influence radius at 20k inhabitants...
        "town_sigma_exp": 0.3,       # ...growing as (pop / 20k)^exp (Trudgill gravity)
        "town_weight": 1.0,          # extra weight of towns in the neighbourhood
        "a": 1.31,                   # exponent on neighbourhood share (Abrams-Strogatz)
        "kappa0": 0.15,              # neighbourhood-independent (institutional) part of shift
        "beta_access": 0.004,        # yearly rural growth elasticity w.r.t. town potential
        "pull_km": 25.0,             # decay length of the town potential
        "seed_floor": 0.01,          # share of arrivals placed independent of existing speakers
        "town_seed_floor": 0.05,     # initial town composition: (floor + rural share)^exp
        "town_seed_exp": 0.8,
        "urban_density": 4000.0,     # persons/km2 used to draw towns as areas on maps
    },
}

# Parameters re-drawn in Monte-Carlo runs: path -> (distribution, a, b)
UNCERTAINTY: dict[str, tuple[str, float, float]] = {
    "fertility.d_max": ("uniform", 0.45, 0.80),
    "fertility.D4": ("uniform", 1.6, 1.95),
    "fertility.phase3_mu.JH": ("uniform", 2.2, 4.0),
    "fertility.phase3_mu.default": ("normal", 1.45, 0.15),
    "fertility.baby_boom.amplitude": ("uniform", 0.0, 0.20),
    "mortality.catchup_post": ("uniform", 0.08, 0.16),
    "mortality.gap_min": ("uniform", 1.0, 3.0),
    "economy.convergence_beta": ("uniform", 0.015, 0.03),
    "economy.shock_sd": ("uniform", 0.015, 0.03),
    "migration.emigration_base.RC:pl": ("uniform", 0.002, 0.0045),
    "migration.hump_peak": ("uniform", 0.28, 0.42),
    "migration.immigration_max": ("uniform", 0.002, 0.006),
    "language.a": ("uniform", 1.1, 1.5),
    "language.m_mono": ("uniform", 0.08, 0.25),
    "language.sigma0.JW:yi": ("uniform", 0.35, 0.65),
    "language.sigma0.OR:pls": ("uniform", 0.30, 0.60),
    "language.sigma0.OR:be": ("uniform", 0.12, 0.35),
    "language.sigma0.RC:be": ("uniform", 0.40, 0.70),
    "language.sigma0.GC:uk": ("uniform", 0.03, 0.10),
    "language.sigma0.RC:csb": ("uniform", 0.12, 0.30),
    "language.haredi_exit.0.1": ("uniform", 0.12, 0.25),
    "infrastructure.gravity_beta": ("uniform", 0.22, 0.38),
    "infrastructure.bcr_threshold": ("uniform", 0.9, 1.3),
}


def _specificity(code: str, pattern: str) -> int:
    """0 = no match; 1 = wildcard; 2 = parent region; 3 = the county a piece
    was cut from (``data.governorates``); 4 = exact.

    Sub-regions are named ``PARENT.CHILD`` (e.g. ``WIL.E``) and inherit any
    setting given for their parent unless a more specific key overrides it."""
    if pattern == code:
        return 4
    if "~" in code and pattern == code.split("~")[0].rstrip("."):
        return 3
    if pattern == code.split(".")[0]:
        return 2
    if pattern.endswith("*") and code.startswith(pattern[:-1]):
        return 1
    return 0


def region_match(code: str, pattern: str) -> bool:
    return _specificity(code, pattern) > 0


def matching_patterns(spec: dict, code: str) -> list:
    """Keys of ``spec`` that apply to ``code``, least specific first, so that
    applying them in order lets the most specific one win."""
    keys = [(k, _specificity(code, k)) for k in spec if k != "default"]
    return [k for k, s in sorted((x for x in keys if x[1] > 0), key=lambda x: x[1])]


def region_lookup(spec: dict, code: str, default=None):
    """Most specific value of a region-keyed mapping (falls back to 'default')."""
    keys = matching_patterns(spec, code)
    if keys:
        return spec[keys[-1]]
    return spec.get("default", default)


def deep_merge(base: dict, over: dict) -> dict:
    """Recursive merge; a mapping containing ``_replace: true`` replaces the
    base mapping instead of being merged into it."""
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and v.get("_replace"):
            out[k] = {kk: copy.deepcopy(vv) for kk, vv in v.items() if kk != "_replace"}
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


REGION_KEYED = [("dominant_language",), ("official_languages",), ("members",), ("language", "status_regions"),
                ("language", "own_schooling_regions"), ("language", "pressure"),
                ("economy", "regional_programmes"), ("migration", "settlement", "origins"),
                ("migration", "settlement", "destinations")]


def expand_region_groups(params: dict) -> dict:
    """``region_groups`` names sets of regions (e.g. a canton made of counties);
    a setting keyed by a group name applies to each member as if keyed by
    its own code."""
    groups = params.get("region_groups") or {}
    if not groups:
        return params
    for path in REGION_KEYED:
        d = params
        for k in path:
            d = d.get(k) if isinstance(d, dict) else None
            if d is None:
                break
        if not isinstance(d, dict):
            continue
        for g, members in groups.items():
            if g in d:
                val = d.pop(g)
                for m in members:
                    d.setdefault(m, copy.deepcopy(val))
    excl = params.get("exclude") or []
    params["exclude"] = [m for e in excl for m in (groups.get(e, [e]))]
    return params


def resolve_governorates(params: dict, labels: dict) -> dict:
    """Turn the groups of ``governorates`` into the units they hold, once the
    partition has cut the units (``labels``: unit -> group, or None).

    * A setting keyed by a group name applies to each of its units, as for
      ``region_groups`` (a key for the unit, its county or its voivodeship
      still wins).
    * Units in no group are left out of the state (``exclude``), unless their
      1932 state is in ``governorates_keep_outside`` (Poland by default):
      the Klaipėda region, Palanga, the BSSR's slivers of other governorates.
    * ``exclude`` may name a group."""
    from .data.regions import state_of_code
    groups = params.get("governorates") or {}
    members = {g: [c for c, lab in labels.items() if lab == g] for g in groups}
    for path in REGION_KEYED:
        d = params
        for k in path:
            d = d.get(k) if isinstance(d, dict) else None
            if d is None:
                break
        if not isinstance(d, dict):
            continue
        for g, units in members.items():
            if g in d:
                val = d.pop(g)
                own = [k for k in d if k != "default" and k not in groups]
                for u in units:
                    # a key naming the unit, its county or its voivodeship wins over the group
                    if not any(_specificity(u, k) >= 2 for k in own):
                        d[u] = copy.deepcopy(val)
    keep = set(params.get("governorates_keep_outside", ["PL"]))
    excl = []
    for e in params.get("exclude") or []:
        excl += members.get(e, [e])
    excl += [c for c, lab in labels.items() if lab is None and state_of_code(c) not in keep and c not in excl]
    params["exclude"] = excl
    params["governorate_units"] = {g: sorted(u) for g, u in members.items()}
    return params


def load_scenario(path_or_name: str | None) -> dict:
    """Load a scenario YAML (path, or a name in scenarios/) merged over DEFAULTS.
    A scenario may name a parent via ``extends:``."""
    import os
    if path_or_name is None:
        return copy.deepcopy(DEFAULTS)
    path = path_or_name
    if not os.path.exists(path):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(here, "scenarios", f"{path_or_name}.yaml")
    with open(path, encoding="utf-8") as fh:
        over = yaml.safe_load(fh) or {}
    parent = over.pop("extends", None)
    base = load_scenario(parent) if parent else copy.deepcopy(DEFAULTS)
    return expand_region_groups(deep_merge(base, over))


def set_path(d: dict, path: str, value) -> None:
    keys = path.split(".")
    cur = d
    for k in keys[:-1]:
        if isinstance(cur, list):
            cur = cur[int(k)]
        else:
            cur = cur[k]
    last = keys[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


def get_path(d: dict, path: str):
    cur = d
    for k in path.split("."):
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur
