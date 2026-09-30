"""Figures, tables and the HTML report.

Charts follow a fixed, colour-blind-validated categorical order (colour
follows the entity, never its rank), thin marks, hairline grids, one y-axis
per panel (different scales -> small multiples), and a table twin for every
chart in the HTML report.
"""
from __future__ import annotations

import base64
import html
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .data.languages import GROUPS, LANG_INDEX, LANGUAGES, NL  # noqa: E402
from .data.network import NODES  # noqa: E402
from .data.regions import REGIONS  # noqa: E402
from .ensemble import QUANTILES  # noqa: E402
from .language import CENSUS_CATEGORIES  # noqa: E402

# ---------------------------------------------------------------------------------
# Palette (validated reference instance; light surface)
# ---------------------------------------------------------------------------------
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASE = "#c3c2b7"
OTHER = "#b9b8b1"
BLUE_RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
ORANGE_RAMP = ["#f6c8b3", "#f2a07f", "#eb6834", "#b94a1f", "#7a2e10"]

# Colour follows the language (fixed slot per entity).
LANG_SLOT = {"pl": 0, "uk": 1, "yi": 2, "be": 3, "lt": 4, "de": 5, "pls": 6}
LANG_LABEL = {l.code: l.name for l in LANGUAGES}
LANG_LABEL["pls"] = "West Polesian"
MAIN_LANGS = ["pl", "uk", "yi", "be", "lt", "de", "pls"]


def lang_color(code: str) -> str:
    return SLOTS[LANG_SLOT[code]] if code in LANG_SLOT else OTHER


def _style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": BASE, "axes.linewidth": 0.8, "axes.labelcolor": INK2,
        "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": INK,
        "axes.titlelocation": "left", "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "grid.linestyle": "-", "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5, "font.family": ["DejaVu Sans"], "font.size": 9, "legend.frameon": False,
        "legend.fontsize": 8.5, "lines.linewidth": 2.0, "lines.solid_capstyle": "round",
        "axes.spines.top": False, "axes.spines.right": False,
    })


_style()


def _save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _fan(ax, years, q, color, label=None, scale=1.0):
    q = np.asarray(q) / scale
    ax.fill_between(years, q[0], q[4], color=color, alpha=0.10, linewidth=0)
    ax.fill_between(years, q[1], q[3], color=color, alpha=0.20, linewidth=0)
    ax.plot(years, q[2], color=color, lw=2, label=label)


def _q(ens, key):
    return np.percentile(ens[key], QUANTILES, axis=0)


# ---------------------------------------------------------------------------------
# Single-run helpers
# ---------------------------------------------------------------------------------
def lang_totals(res) -> np.ndarray:
    A = res.arrays()
    gl = np.array([LANG_INDEX[l] for _, l in GROUPS])
    out = np.zeros((len(res.years), NL))
    for g in range(len(GROUPS)):
        out[:, gl[g]] += A["pop"][:, :, :, g].sum(axis=(1, 2))
    return out


def region_lang(res, i: int) -> np.ndarray:
    A = res.arrays()
    gl = np.array([LANG_INDEX[l] for _, l in GROUPS])
    out = np.zeros((len(res.region_codes), NL))
    for g in range(len(GROUPS)):
        out[:, gl[g]] += A["pop"][i][:, :, g].sum(axis=1)
    return out


def _fold(vec_by_lang: np.ndarray) -> tuple[list[str], np.ndarray]:
    labels = MAIN_LANGS + ["other"]
    vals = [vec_by_lang[..., LANG_INDEX[c]] for c in MAIN_LANGS]
    other = vec_by_lang.sum(axis=-1) - sum(vals)
    return labels, np.stack(vals + [other], axis=-1)


# ---------------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------------
def fig_population(ens: dict, path: str, title_suffix: str = ""):
    yrs = ens["years"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
    _fan(axes[0], yrs, _q(ens, "pop_total"), SLOTS[0], scale=1e6)
    axes[0].set_title("Whole union (millions)")
    _fan(axes[1], yrs, _q(ens, "pop_pl"), SLOTS[0], scale=1e6)
    axes[1].set_title("Polish voivodeships (millions)")
    if ens["pop_lt"].max() > 0:
        _fan(axes[2], yrs, _q(ens, "pop_lt"), SLOTS[4], scale=1e6)
        axes[2].set_title("Lithuanian units (millions)")
    else:
        axes[2].axis("off")
    for ax in axes:
        ax.set_xlim(yrs[0], yrs[-1])
        med = ax.lines[0].get_ydata() if ax.lines else None
        if med is not None:
            ax.annotate(f"{med[-1]:.1f}", (yrs[-1], med[-1]), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=8.5, color=INK2)
    fig.suptitle(f"Population, median with 50 % and 90 % bands{title_suffix}", x=0.01, ha="left",
                 fontsize=12, fontweight="bold", color=INK)
    fig.tight_layout()
    _save(fig, path)


def fig_vitals(ens: dict, path: str):
    yrs = ens["years"]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.2))
    _fan(axes[0, 0], yrs, _q(ens, "tfr"), SLOTS[0])
    axes[0, 0].set_title("Total fertility rate")
    e0 = ens["e0"]
    _fan(axes[0, 1], yrs, np.percentile(e0[:, :, 1], QUANTILES, axis=0), SLOTS[1], label="Women")
    _fan(axes[0, 1], yrs, np.percentile(e0[:, :, 0], QUANTILES, axis=0), SLOTS[0], label="Men")
    axes[0, 1].set_title("Life expectancy at birth (years)")
    axes[0, 1].legend(loc="lower right")
    _fan(axes[0, 2], yrs, _q(ens, "urban_share") * 100, SLOTS[2])
    axes[0, 2].set_title("Urban population (%)")
    tot = ens["pop_total"]
    net = (ens["immig"] - ens["emig"]) / tot * 1000
    _fan(axes[1, 0], yrs, np.percentile(net, QUANTILES, axis=0), SLOTS[7])
    axes[1, 0].axhline(0, color=BASE, lw=0.8)
    axes[1, 0].set_title("Net international migration (per 1000)")
    z = ens["y_nat"] / ens["y_frontier"]
    _fan(axes[1, 1], yrs, np.percentile(z, QUANTILES, axis=0) * 100, SLOTS[6])
    axes[1, 1].set_title("GDP per head, % of western frontier")
    _fan(axes[1, 2], yrs, _q(ens, "vehicles"), SLOTS[5])
    axes[1, 2].set_title("Motor vehicles per 1000")
    for ax in axes.flat:
        ax.set_xlim(yrs[0], yrs[-1])
    fig.tight_layout()
    _save(fig, path)


def fig_language_area(res, path: str, title: str = "Home language of the population (latent vernacular)"):
    lt = lang_totals(res)
    labels, vals = _fold(lt)
    yrs = np.array(res.years)
    share = vals / vals.sum(axis=1, keepdims=True) * 100
    fig, ax = plt.subplots(figsize=(10, 4.6))
    colors = [lang_color(c) for c in labels]
    ax.stackplot(yrs, share.T, colors=colors, edgecolor=SURFACE, linewidth=0.6)
    ax.set_xlim(yrs[0], yrs[-1])
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of population")
    ax.set_title(title)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
    ax.legend(handles, [LANG_LABEL.get(l, "Other") for l in labels], ncol=8, loc="upper center",
              bbox_to_anchor=(0.5, -0.1))
    ax.grid(False)
    fig.tight_layout()
    _save(fig, path)
    return labels, share


def fig_language_scenarios(results: dict, path: str, year: int = 2032):
    """Small multiples: share of each main language in `year` by scenario."""
    names = list(results)
    langs = ["pl", "uk", "yi", "be", "lt", "pls"]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.2), sharey=True)
    ypos = np.arange(len(names))
    for ax, code in zip(axes.flat, langs):
        vals = []
        for n in names:
            res = results[n]
            i = res.years.index(year)
            lt = lang_totals(res)[i]
            vals.append(lt[LANG_INDEX[code]] / lt.sum() * 100)
        colors = [lang_color(code) if n == "baseline" else OTHER for n in names]
        ax.barh(ypos, vals, height=0.6, color=colors)
        for y, v in zip(ypos, vals):
            ax.text(v, y, f" {v:.1f}", va="center", fontsize=7.5, color=INK2)
        ax.set_title(f"{LANG_LABEL[code]} (% in {year})")
        ax.set_yticks(ypos, names)
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
        ax.set_xlim(0, max(vals) * 1.25 + 0.5)
    fig.tight_layout()
    _save(fig, path)


def fig_endangered(ens: dict, path: str):
    yrs = ens["years"]
    codes = ["csb", "rue", "pls", "be", "yi", "rom", "kdr", "wym"]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6))
    for ax, code in zip(axes.flat, codes):
        q = np.percentile(ens["pop_lang"][:, :, LANG_INDEX[code]], QUANTILES, axis=0)
        _fan(ax, yrs, np.maximum(q, 1), SLOTS[0])
        ax.set_yscale("log")
        ax.set_title(LANG_LABEL[code])
        ax.set_xlim(yrs[0], yrs[-1])
        ax.annotate(f"{q[2][-1]:,.0f}", (yrs[-1], max(q[2][-1], 1)), xytext=(3, 0),
                    textcoords="offset points", fontsize=8, color=INK2, va="center")
    fig.suptitle("Home speakers of minority and endangered languages (log scale; median, 50 %, 90 %)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    _save(fig, path)


def fig_pyramids(res, path: str, years=(1932, 1970, 2000, 2032)):
    fig, axes = plt.subplots(1, len(years), figsize=(13, 4.4), sharey=True)
    ages = np.arange(101)
    for ax, y in zip(axes, years):
        if y not in res.pyramids:
            ax.axis("off")
            continue
        pyr = res.pyramids[y]                        # (NL, 2, 101)
        labels, vals = _fold(np.moveaxis(pyr, 0, -1))  # (2, 101, 8)
        tot = pyr.sum()
        left_m = np.zeros(101)
        left_f = np.zeros(101)
        for k, lab in enumerate(labels):
            m = vals[0, :, k] / tot * 100
            f = vals[1, :, k] / tot * 100
            ax.barh(ages, -m, left=-left_m, height=1.0, color=lang_color(lab), linewidth=0)
            ax.barh(ages, f, left=left_f, height=1.0, color=lang_color(lab), linewidth=0)
            left_m += m
            left_f += f
        lim = max(left_m.max(), left_f.max()) * 1.05
        ax.set_xlim(-lim, lim)
        ax.set_title(f"{y}  ({tot / 1e6:.1f} M)")
        ax.axvline(0, color=SURFACE, lw=1)
        ax.set_xlabel("men  % |  % women")
        ax.grid(axis="y", visible=False)
    axes[0].set_ylabel("age")
    handles = [plt.Rectangle((0, 0), 1, 1, color=lang_color(c)) for c in MAIN_LANGS + ["other"]]
    fig.legend(handles, [LANG_LABEL.get(c, "Other") for c in MAIN_LANGS + ["other"]], ncol=8,
               loc="lower center", bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save(fig, path)


def fig_census_regimes(res, path: str, year: int):
    """Dot plot: the same population as four census regimes would record it."""
    regs = ["latent", "polish_1931", "modern_selfid", "imperial_1897"]
    names = {"latent": "Latent home language", "polish_1931": "As a 1931-type Polish census",
             "modern_selfid": "Modern self-identification", "imperial_1897": "As the 1897 imperial census"}
    cats = ["uk", "ruth", "yi", "he", "be", "tut", "lt", "de", "ru", "other"]
    cat_label = {"pl": "Polish", "uk": "Ukrainian", "ruth": "'Ruthenian'", "yi": "Yiddish", "he": "Hebrew",
                 "be": "Belarusian", "tut": "'Local' / Polesian", "lt": "Lithuanian", "de": "German",
                 "ru": "Russian", "other": "Other"}
    vals = {}
    for rg in regs:
        tab = res.census[(rg, year)].sum(axis=0)
        tot = tab.sum()
        d = {c: tab[CENSUS_CATEGORIES.index(c)] / tot * 100 for c in ["pl"] + cats if c != "other"}
        d["other"] = 100 - sum(d.values())
        vals[rg] = d
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 3.2]})
    for ax, cs in ((ax0, ["pl"]), (ax1, cats)):
        y = np.arange(len(cs))
        for i, c in enumerate(cs):
            xs = [vals[rg][c] for rg in regs]
            ax.hlines(i, min(xs), max(xs), color=BASE, lw=1.5, zorder=1)
        for k, rg in enumerate(regs):
            ax.scatter([vals[rg][c] for c in cs], y, s=46, color=SLOTS[k], edgecolor=SURFACE, linewidth=1.5,
                       zorder=3, label=names[rg])
        ax.set_yticks(y, [cat_label[c] for c in cs])
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("% of population")
    lo = min(vals[rg]["pl"] for rg in regs)
    hi = max(vals[rg]["pl"] for rg in regs)
    ax0.set_xlim(lo - 3, hi + 3)
    ax0.set_title("Polish")
    ax1.set_title("Other categories")
    ax1.set_xlim(0, None)
    ax1.legend(loc="lower right")
    fig.suptitle(f"The same {year} population as four different censuses would record it", x=0.01, ha="left",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    _save(fig, path)


def _draw_network(ax, snap, mode: int, ramp, classes, lat, lon, town_pop=None, title=""):
    for u, v, m, cls in snap:
        if m != mode:
            continue
        k = classes.index(cls)
        ax.plot([lon[u], lon[v]], [lat[u], lat[v]], color=ramp[k], lw=0.6 + 0.6 * k, solid_capstyle="round",
                zorder=1 + k)
    if town_pop is not None:
        dom = np.array([n.region != "EXT" for n in NODES])
        s = np.sqrt(np.maximum(town_pop, 1)) * 1.6
        ax.scatter(np.array(lon)[dom], np.array(lat)[dom], s=s[dom], color=INK2, alpha=0.55, lw=0, zorder=10)
    ax.set_title(title)
    ax.set_aspect(1 / np.cos(np.radians(52)))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


LABEL_TOWNS = ["Warszawa", "Łódź", "Kraków", "Lwów", "Poznań", "Wilno", "Gdynia", "Katowice", "Lublin", "Brześć",
               "Kaunas", "Klaipėda", "Białystok", "Równe", "Stanisławów"]


def _label_towns(ax, lat, lon):
    idx = {n.name: i for i, n in enumerate(NODES)}
    for name in LABEL_TOWNS:
        i = idx[name]
        ax.annotate(name, (lon[i], lat[i]), xytext=(3, 3), textcoords="offset points", fontsize=7, color=INK,
                    zorder=20)


def fig_networks(res, path: str, years=(1932, 1970, 2032)):
    rail_cls = ["nar", "sec", "main", "main_el", "hsr"]
    road_cls = ["dirt", "gravel", "paved", "express", "motorway"]
    lat, lon = res.node_lat, res.node_lon
    fig, axes = plt.subplots(2, len(years), figsize=(14, 9.5))
    for j, y in enumerate(years):
        snap = res.network_snapshots.get(y)
        if snap is None:
            continue
        ti = res.years.index(y) - 1 if y in res.years else 0
        tp = np.array(res.town_pop[max(ti, 0)]) if res.town_pop else None
        _draw_network(axes[0, j], snap, 0, BLUE_RAMP, rail_cls, lat, lon, tp, f"Railways {y}")
        _draw_network(axes[1, j], snap, 1, ORANGE_RAMP, road_cls, lat, lon, tp, f"Roads {y}")
        if j == 0:
            _label_towns(axes[0, j], lat, lon)
            _label_towns(axes[1, j], lat, lon)
    h1 = [plt.Line2D([0], [0], color=BLUE_RAMP[k], lw=0.6 + 0.6 * k) for k in range(5)]
    h2 = [plt.Line2D([0], [0], color=ORANGE_RAMP[k], lw=0.6 + 0.6 * k) for k in range(5)]
    fig.legend(h1 + h2, ["narrow gauge", "secondary", "main line", "electrified main", "high speed",
                         "dirt", "gravel/macadam", "paved", "expressway", "motorway"],
               ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save(fig, path)


def fig_network_km(ens: dict, path: str):
    yrs = ens["years"]
    km = np.median(ens["km"], axis=0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    rail = km[:, :5]
    road = km[:, 5:]
    axes[0].stackplot(yrs, rail.T / 1000, colors=BLUE_RAMP, edgecolor=SURFACE, linewidth=0.5,
                      labels=["narrow", "secondary", "main", "electrified", "high speed"])
    axes[0].set_title("Modelled rail route-km (thousands, median run)")
    axes[1].stackplot(yrs, road.T / 1000, colors=ORANGE_RAMP, edgecolor=SURFACE, linewidth=0.5,
                      labels=["dirt", "gravel", "paved", "expressway", "motorway"])
    axes[1].set_title("Modelled inter-town road-km (thousands, median run)")
    for ax in axes:
        ax.set_xlim(yrs[0], yrs[-1])
        ax.legend(loc="upper left", ncol=2)
        ax.grid(axis="x", visible=False)
    fig.tight_layout()
    _save(fig, path)


def fig_regional(res, path: str):
    A = res.arrays()
    codes = res.region_codes
    i0, i1 = 0, len(res.years) - 1
    p0 = A["pop"][i0].sum(axis=(1, 2)) / 1e6
    p1 = A["pop"][i1].sum(axis=(1, 2)) / 1e6
    u0 = A["pop"][i0][:, 1].sum(axis=1) / A["pop"][i0].sum(axis=(1, 2)) * 100
    u1 = A["pop"][i1][:, 1].sum(axis=1) / A["pop"][i1].sum(axis=(1, 2)) * 100
    rel0 = np.array(res.rel_income[0])
    rel1 = np.array(res.rel_income[-1])
    names = [next(r.name for r in REGIONS if r.code == c) for c in codes]
    y = np.arange(len(codes))
    fig, axes = plt.subplots(1, 3, figsize=(13, 6.8), sharey=True)
    for ax, a, b, t in [(axes[0], p0, p1, "Population (millions)"), (axes[1], u0, u1, "Urban share (%)"),
                        (axes[2], rel0 * 100, rel1 * 100, "Income per head (% of average)")]:
        ax.hlines(y, np.minimum(a, b), np.maximum(a, b), color=BASE, lw=1.5)
        ax.scatter(a, y, color=SLOTS[1], s=28, zorder=3, label=str(res.years[0] - 1) if False else "1932",
                   edgecolor=SURFACE, linewidth=1.5)
        ax.scatter(b, y, color=SLOTS[0], s=28, zorder=3, label=str(res.years[-1]), edgecolor=SURFACE, linewidth=1.5)
        ax.set_title(t)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(y, names)
    axes[0].invert_yaxis()
    axes[0].legend(loc="lower right")
    fig.tight_layout()
    _save(fig, path)


def fig_region_languages(res, path: str, years=(1932, 2032)):
    codes = res.region_codes
    names = [next(r.name for r in REGIONS if r.code == c) for c in codes]
    fig, axes = plt.subplots(1, len(years), figsize=(13, 7.2), sharey=True)
    for ax, yv in zip(axes, years):
        i = res.years.index(yv) if yv in res.years else 0
        rl = region_lang(res, i)
        labels, vals = _fold(rl)
        share = vals / vals.sum(axis=1, keepdims=True) * 100
        left = np.zeros(len(codes))
        for k, lab in enumerate(labels):
            ax.barh(np.arange(len(codes)), share[:, k], left=left, height=0.7, color=lang_color(lab),
                    edgecolor=SURFACE, linewidth=1.0)
            left += share[:, k]
        ax.set_xlim(0, 100)
        ax.set_title(f"Home language by region, {yv} (%)")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(np.arange(len(codes)), names)
    axes[0].invert_yaxis()
    handles = [plt.Rectangle((0, 0), 1, 1, color=lang_color(c)) for c in MAIN_LANGS + ["other"]]
    fig.legend(handles, [LANG_LABEL.get(c, "Other") for c in MAIN_LANGS + ["other"]], ncol=8,
               loc="lower center", bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, path)


def fig_lithuania_poles(results: dict, path: str):
    """Polish speakers in the Lithuanian units (the Lauda question) by scenario."""
    fig, ax = plt.subplots(figsize=(9, 4))
    k = 0
    labelled: list[float] = []
    for name, res in results.items():
        codes = res.region_codes
        lt = [i for i, c in enumerate(codes) if c.startswith("LT")]
        if not lt:
            continue
        A = res.arrays()
        gpl = [g for g, (c, l) in enumerate(GROUPS) if l == "pl"]
        series = A["pop"][:, lt][:, :, :, gpl].sum(axis=(1, 2, 3)) / 1e3
        ax.plot(res.years, series, color=SLOTS[k % 8], label=name, lw=3.2 if name == "baseline" else 2.0,
                zorder=2 if name == "baseline" else 3)
        # label end values once; series ending at the same value share a label
        if all(abs(series[-1] - v) > 0.06 * max(v, 1) for v in labelled):
            ax.annotate(f"{series[-1]:.0f}k", (res.years[-1], series[-1]), xytext=(4, 0),
                        textcoords="offset points", fontsize=8, color=INK2, va="center")
            labelled.append(series[-1])
        k += 1
    ax.set_title("Home speakers of Polish in the Lithuanian units (thousands)")
    ax.legend(loc="upper left", ncol=2)
    ax.set_xlim(res.years[0], res.years[-1] + 6)
    fig.tight_layout()
    _save(fig, path)


def fig_scenario_population(results: dict, path: str):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    names = list(results)
    for k, n in enumerate(names):
        res = results[n]
        A = res.arrays()
        pl = np.array([not c.startswith("LT") for c in res.region_codes])
        plp = A["pop"][:, pl].sum(axis=(1, 2, 3)) / 1e6
        color = SLOTS[0] if n == "baseline" else OTHER
        lw = 2.2 if n == "baseline" else 1.2
        ax.plot(res.years, plp, color=color, lw=lw, zorder=3 if n == "baseline" else 2)
        ax.annotate(n, (res.years[-1], plp[-1]), xytext=(4, 0), textcoords="offset points", fontsize=7.5,
                    color=INK if n == "baseline" else MUTED, va="center")
    ax.set_title("Population of the Polish voivodeships by scenario (millions; single seeded run each)")
    ax.set_xlim(results[names[0]].years[0], results[names[0]].years[-1] + 18)
    fig.tight_layout()
    _save(fig, path)


def fig_migration(res, path: str):
    A = res.arrays()
    codes = res.region_codes
    yrs = np.array(res.years)
    pop = A["pop"].sum(axis=(2, 3))
    inflow = A["internal"].sum(axis=1)
    outflow = A["internal"].sum(axis=2)
    net = (inflow - outflow) / pop * 1000                  # (T,R)
    decades = list(range(1932, 2032, 10))
    M = np.zeros((len(codes), len(decades)))
    for j, d in enumerate(decades):
        idx = [i for i, y in enumerate(yrs) if d < y <= d + 10]
        M[:, j] = net[idx].mean(axis=0)
    names = [next(r.name for r in REGIONS if r.code == c) for c in codes]
    fig, ax = plt.subplots(figsize=(9, 7))
    lim = np.abs(M).max()
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])
    im = ax.imshow(M, cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(len(decades)), [f"{d}-{str(d + 9)[2:]}" for d in decades], rotation=45)
    ax.set_yticks(range(len(codes)), names)
    ax.grid(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=6.5,
                    color="white" if abs(v) > lim * 0.6 else INK)
    ax.set_title("Net internal (inter-regional) migration, per 1000 per year")
    cb = fig.colorbar(im, ax=ax, shrink=0.6)
    cb.outline.set_visible(False)
    fig.tight_layout()
    _save(fig, path)


def fig_towns(res, path: str, n: int = 20):
    first = np.array(res.town_pop[0])
    last = np.array(res.town_pop[-1])
    dom = np.array([nd.region != "EXT" for nd in NODES])
    order = np.argsort(-np.where(dom, last, -1))[:n]
    names = [NODES[i].name for i in order]
    y = np.arange(n)
    fig, ax = plt.subplots(figsize=(8, 6.4))
    ax.hlines(y, first[order], last[order], color=BASE, lw=1.5)
    ax.scatter(first[order], y, color=SLOTS[1], s=28, zorder=3, label="1932", edgecolor=SURFACE, linewidth=1.5)
    ax.scatter(last[order], y, color=SLOTS[0], s=28, zorder=3, label=str(res.years[-1]), edgecolor=SURFACE,
               linewidth=1.5)
    ax.set_xscale("log")
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlabel("thousand inhabitants (log)")
    ax.set_title("Largest towns (modelled urban population of the node)")
    ax.legend(loc="lower right")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    _save(fig, path)


# ---------------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------------
def table_html(header: list[str], rows: list[list], caption: str = "") -> str:
    h = "".join(f"<th>{html.escape(str(x))}</th>" for x in header)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in r) + "</tr>" for r in rows)
    cap = f"<caption>{html.escape(caption)}</caption>" if caption else ""
    return f"<table>{cap}<thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def language_table(res, years=(1932, 1950, 1970, 1990, 2010, 2032)):
    lt = lang_totals(res)
    rows = []
    for l in LANGUAGES:
        row = [l.name]
        for y in years:
            if y in res.years:
                i = res.years.index(y)
                row.append(f"{lt[i, LANG_INDEX[l.code]]:,.0f}")
        rows.append(row)
    return ["Language"] + [str(y) for y in years if y in res.years], rows


def img_tag(path: str, alt: str) -> str:
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return f'<img alt="{html.escape(alt)}" src="data:image/png;base64,{b64}"/>'
