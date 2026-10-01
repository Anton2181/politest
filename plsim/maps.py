"""Maps of language shift and population change, drawn from the spatial layer.

The colours follow ``report``: each language keeps its slot, and the
plurality maps fade toward the surface colour as the plurality share
falls.  Kashubian, Lemko-Rusyn and Wymysorys are grouped as "regional
languages" in the free red slot; everything else is grey.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import animation  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, LogNorm, TwoSlopeNorm  # noqa: E402
from matplotlib.patches import Patch, Polygon  # noqa: E402

from .data.geography import BBOX, load_base_geography  # noqa: E402
from .data.languages import LANG_INDEX  # noqa: E402
from .report import INK, INK2, MUTED, OTHER, SLOTS, SURFACE, _save  # noqa: E402

CATS = ["pl", "uk", "yi", "be", "lt", "de", "pls", "reg", "oth"]
CAT_LABEL = {"pl": "Polish", "uk": "Ukrainian", "yi": "Yiddish", "be": "Belarusian", "lt": "Lithuanian",
             "de": "German", "pls": "West Polesian", "reg": "Kashubian, Lemko, Wymysorys", "oth": "Other"}
CAT_COLOR = dict(zip(CATS, SLOTS[:8] + [OTHER]))
REGIONAL = ["csb", "rue", "wym"]
SEA = "#eef3f6"
FOREIGN = "#efeee9"
WATER = "#a9c8dc"
BORDER = "#5d5c58"
LAT0 = 52.0
XLIM = (15.35, 29.0)        # fixed map extent, so scenarios with and without Lithuania align
YLIM = (47.85, 56.85)
LABEL_TOWNS = ["Warszawa", "Łódź", "Kraków", "Lwów", "Poznań", "Wilno", "Kaunas", "Lublin", "Białystok",
               "Katowice", "Gdynia", "Brześć", "Pińsk", "Równe", "Stanisławów", "Grodno", "Klaipėda", "Šiauliai"]


def _hex(c: str) -> np.ndarray:
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0


def display_shares(X: np.ndarray) -> np.ndarray:
    """(Nc, NL) persons -> (Nc, 9) shares in CATS order."""
    tot = np.maximum(X.sum(axis=1), 1e-9)
    out = np.zeros((len(X), len(CATS)))
    for k, c in enumerate(CATS[:7]):
        out[:, k] = X[:, LANG_INDEX[c]]
    out[:, 7] = X[:, [LANG_INDEX[c] for c in REGIONAL]].sum(axis=1)
    out[:, 8] = tot - out[:, :8].sum(axis=1)
    return np.clip(out / tot[:, None], 0, 1)


class Canvas:
    """Raster geometry of a grid plus the base-map overlays."""

    def __init__(self, grid):
        self.g = grid
        self.row = np.round((grid.lat - (BBOX[1] + grid.dlat / 2)) / grid.dlat).astype(int)
        self.col = np.round((grid.lon - (BBOX[0] + grid.dlon / 2)) / grid.dlon).astype(int)
        self.H = int(np.round((BBOX[3] - BBOX[1]) / grid.dlat))
        self.W = int(np.round((BBOX[2] - BBOX[0]) / grid.dlon))
        self.extent = [BBOX[0], BBOX[0] + self.W * grid.dlon, BBOX[1], BBOX[1] + self.H * grid.dlat]
        self.geo = load_base_geography()
        self.xlim = XLIM
        self.ylim = YLIM
        self.borders, self.outline = self._borders()

    def raster(self, values: np.ndarray, fill=np.nan) -> np.ndarray:
        values = np.asarray(values)
        img = np.full((self.H, self.W) + values.shape[1:], fill, dtype=float)
        img[self.row, self.col] = values
        return img

    def _borders(self):
        region = self.g.region.copy()
        codes = list(self.g.region_codes)
        if "WAW" in codes and "WAR" in codes:          # the city region is drawn as part of its voivodeship
            region[region == codes.index("WAW")] = codes.index("WAR")
        reg = self.raster(region.astype(float), fill=-1)
        dl, dt = self.g.dlon, self.g.dlat
        x0, y0 = BBOX[0], BBOX[1]
        inner, outer = [], []
        for r in range(self.H):
            for c in range(self.W):
                a = reg[r, c]
                if c + 1 < self.W and a != reg[r, c + 1] and max(a, reg[r, c + 1]) >= 0:
                    seg = [(x0 + (c + 1) * dl, y0 + r * dt), (x0 + (c + 1) * dl, y0 + (r + 1) * dt)]
                    (inner if min(a, reg[r, c + 1]) >= 0 else outer).append(seg)
                if r + 1 < self.H and a != reg[r + 1, c] and max(a, reg[r + 1, c]) >= 0:
                    seg = [(x0 + c * dl, y0 + (r + 1) * dt), (x0 + (c + 1) * dl, y0 + (r + 1) * dt)]
                    (inner if min(a, reg[r + 1, c]) >= 0 else outer).append(seg)
        return inner, outer

    def base(self, ax, title: str = ""):
        ax.set_facecolor(SEA)
        for poly in self.geo["land"]:
            ax.add_patch(Polygon(poly, closed=True, facecolor=FOREIGN, edgecolor="none", zorder=0))
        for poly in self.geo["lakes"]:
            ax.add_patch(Polygon(poly, closed=True, facecolor=SEA, edgecolor="none", zorder=0.5))
        ax.set_xlim(*self.xlim)
        ax.set_ylim(*self.ylim)
        ax.set_aspect(1 / np.cos(np.radians(LAT0)))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
        if title:
            ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")

    def overlay(self, ax, rivers: bool = True, towns=None, inner_color: str = "white"):
        if rivers:
            ax.add_collection(LineCollection(self.geo["rivers"], colors=WATER, linewidths=0.5, zorder=3, alpha=0.9))
        for poly in self.geo["lakes"]:
            ax.add_patch(Polygon(poly, closed=True, facecolor=WATER, edgecolor="none", zorder=3))
        ax.add_collection(LineCollection(self.borders, colors=inner_color, linewidths=0.45, zorder=4, alpha=0.8))
        ax.add_collection(LineCollection(self.outline, colors=BORDER, linewidths=0.8, zorder=5))
        if towns is not None:
            names, lat, lon = towns
            for n, la, lo in zip(names, lat, lon):
                if n in LABEL_TOWNS:
                    ax.plot(lo, la, "o", ms=2.2, color=INK, zorder=6)
                    ax.text(lo + 0.08, la + 0.05, n, fontsize=6.5, color=INK, zorder=6,
                            path_effects=_halo())

    def show(self, ax, rgba: np.ndarray, **kw):
        im = ax.imshow(rgba, origin="lower", extent=self.extent, interpolation="nearest", zorder=2,
                       aspect=1 / np.cos(np.radians(LAT0)), **kw)
        ax.set_xlim(*self.xlim)
        ax.set_ylim(*self.ylim)
        return im


def _halo():
    from matplotlib import patheffects
    return [patheffects.withStroke(linewidth=2, foreground=SURFACE, alpha=0.85)]


def plurality_rgba(shares: np.ndarray, canvas: Canvas, surface: str = SURFACE) -> np.ndarray:
    k = shares.argmax(axis=1)
    s = shares.max(axis=1)
    t = np.clip((s - 0.3) / 0.5, 0.22, 1.0)[:, None]
    base = np.array([_hex(CAT_COLOR[c]) for c in CATS])[k]
    rgb = base * t + _hex(surface)[None, :] * (1 - t)
    img = canvas.raster(np.column_stack([rgb, np.ones(len(rgb))]), fill=0.0)
    return img


def _towns(sr):
    return sr.town_names, sr.town_lat, sr.town_lon


def _legend_cats(fig, present=None, y=0.0):
    cats = [c for c in CATS if present is None or c in present]
    handles = [Patch(facecolor=CAT_COLOR[c], edgecolor="none", label=CAT_LABEL[c]) for c in cats]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(handles), 5), bbox_to_anchor=(0.5, y),
               fontsize=8.5, frameon=False, handlelength=1.2, columnspacing=1.4)


# ---------------------------------------------------------------------------------
# Static figures
# ---------------------------------------------------------------------------------
def fig_plurality(sr, path: str, years=(1932, 1950, 1970, 1990, 2010, 2032), title: str = ""):
    cv = Canvas(sr.grid)
    ncol = 3
    nrow = int(np.ceil(len(years) / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(13, 5.0 * nrow + 0.8))
    present = set()
    for ax, y in zip(np.ravel(axs), years):
        sh = display_shares(sr.display(sr.frame(y)))
        present |= {CATS[i] for i in np.unique(sh.argmax(axis=1))}
        cv.base(ax, str(y))
        cv.show(ax, plurality_rgba(sh, cv))
        cv.overlay(ax, towns=_towns(sr) if y == years[0] else None)
    for ax in np.ravel(axs)[len(years):]:
        ax.axis("off")
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.07, 1, 0.97 if title else 1))
    _legend_cats(fig, present, y=0.025)
    fig.text(0.01, 0.005, "Colour: most widely spoken home language in each 7 km cell; pale = plurality below "
             "about 50 %. Towns are drawn as areas at urban density.", fontsize=8, color=INK2)
    _save(fig, path)


def _seq_cmap(color: str) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list("seq", [SURFACE, color, tuple(_hex(color) * 0.45)], N=256)


def fig_language_shares(sr, path: str, cats=("uk", "be", "pls", "lt", "yi", "de", "reg"), years=(1932, 1982, 2032)):
    cv = Canvas(sr.grid)
    frames = {y: display_shares(sr.display(sr.frame(y))) for y in years}
    fig, axs = plt.subplots(len(cats), len(years), figsize=(4.3 * len(years), 3.7 * len(cats)))
    for i, c in enumerate(cats):
        k = CATS.index(c)
        vmax = 1.0 if c in ("uk", "be", "pls", "lt") else 0.5
        for j, y in enumerate(years):
            ax = axs[i, j]
            sh = frames[y][:, k]
            n = (sr.display(sr.frame(y)).sum(axis=1) * sh).sum()
            cv.base(ax, f"{CAT_LABEL[c]}, {y}" if j == 0 else str(y))
            img = cv.raster(sh)
            im = cv.show(ax, np.ma.masked_invalid(img), cmap=_seq_cmap(CAT_COLOR[c]), vmin=0, vmax=vmax)
            cv.overlay(ax, rivers=False, inner_color="#d9d8d2")
            ax.text(0.02, 0.02, f"{n / 1e6:.2f} M speakers", transform=ax.transAxes, fontsize=8, color=INK2)
        cb = fig.colorbar(im, ax=axs[i, :], shrink=0.7, pad=0.01)
        cb.ax.tick_params(labelsize=7)
        cb.set_label("share of cell population", fontsize=7.5, color=INK2)
    _save(fig, path)


def fig_share_change(sr, path: str, cats=("pl", "uk", "be", "lt"), y0: int = 1932, y1: int = 2032):
    cv = Canvas(sr.grid)
    a = display_shares(sr.display(sr.frame(y0)))
    b = display_shares(sr.display(sr.frame(y1)))
    cmap = LinearSegmentedColormap.from_list("div", ["#b94a1f", "#f2a07f", "#f1f0ec", "#86b6ef", "#1c5cab"])
    fig, axs = plt.subplots(1, len(cats), figsize=(4.4 * len(cats), 4.6))
    for ax, c in zip(np.ravel(axs), cats):
        k = CATS.index(c)
        d = (b[:, k] - a[:, k]) * 100
        cv.base(ax, CAT_LABEL[c])
        im = cv.show(ax, np.ma.masked_invalid(cv.raster(d)), cmap=cmap, norm=TwoSlopeNorm(0, -60, 60))
        cv.overlay(ax, rivers=False, inner_color="#bfbeb6")
    cb = fig.colorbar(im, ax=axs, shrink=0.75, pad=0.01)
    cb.set_label("percentage points (orange = loss, blue = gain)", fontsize=8, color=INK2)
    fig.suptitle(f"Change in the share of each home language, {y0}–{y1}", x=0.01, ha="left", fontsize=12,
                 fontweight="bold", color=INK)
    _save(fig, path)


def fig_density(sr, path: str, years=(1932, 1960, 1990, 2032)):
    cv = Canvas(sr.grid)
    cmap = LinearSegmentedColormap.from_list("dens", ["#f4f3ee", "#c9dcf2", "#86b6ef", "#2a78d6", "#1c5cab",
                                                      "#0d366b", "#05172f"])
    fig, axs = plt.subplots(1, len(years), figsize=(4.4 * len(years), 4.7))
    for ax, y in zip(np.ravel(axs), years):
        d = sr.density(sr.frame(y))
        cv.base(ax, str(y))
        im = cv.show(ax, np.ma.masked_invalid(cv.raster(np.maximum(d, 2))), cmap=cmap, norm=LogNorm(8, 8000))
        cv.overlay(ax, rivers=False, inner_color="#ffffff", towns=_towns(sr) if y == years[0] else None)
        tot = sr.cells[sr.frame(y)].sum() + sr.towns[sr.frame(y)].sum()
        ax.text(0.02, 0.02, f"{tot / 1e6:.1f} M", transform=ax.transAxes, fontsize=9, color=INK2)
    cb = fig.colorbar(im, ax=axs, shrink=0.75, pad=0.01)
    cb.set_label("persons per km² (log scale)", fontsize=8, color=INK2)
    _save(fig, path)


def fig_pop_change(sr, path: str, periods=((1932, 1970), (1970, 2032), (1932, 2032))):
    cv = Canvas(sr.grid)
    cmap = LinearSegmentedColormap.from_list("div", ["#7a2e10", "#eb6834", "#f6c8b3", "#f1f0ec", "#86b6ef",
                                                     "#2a78d6", "#0d366b"])
    fig, axs = plt.subplots(1, len(periods), figsize=(4.6 * len(periods), 4.7))
    for ax, (y0, y1) in zip(np.ravel(axs), periods):
        a = sr.display(sr.frame(y0)).sum(axis=1)
        b = sr.display(sr.frame(y1)).sum(axis=1)
        r = np.log2(np.maximum(b, 1) / np.maximum(a, 1))
        cv.base(ax, f"{y0}–{y1}")
        im = cv.show(ax, np.ma.masked_invalid(cv.raster(r)), cmap=cmap, norm=TwoSlopeNorm(0, -2, 2))
        cv.overlay(ax, rivers=False, inner_color="#bfbeb6", towns=_towns(sr) if (y0, y1) == periods[0] else None)
    cb = fig.colorbar(im, ax=axs, shrink=0.75, pad=0.01, ticks=[-2, -1, 0, 1, 2])
    cb.ax.set_yticklabels(["÷4", "÷2", "=", "×2", "×4"])
    cb.set_label("population change (orange = decline, blue = growth)", fontsize=8, color=INK2)
    _save(fig, path)


def fig_scenarios_plurality(frames: dict, path: str, year: int = 2032, labels: dict | None = None):
    """``frames``: scenario -> (grid, (Nc, 9) display shares in ``year``)."""
    names = list(frames)
    ncol = 4
    nrow = int(np.ceil(len(names) / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 4.5 * nrow + 0.6))
    present = set()
    for ax, name in zip(np.ravel(axs), names):
        grid, sh = frames[name]
        cv = Canvas(grid)
        present |= {CATS[i] for i in np.unique(sh.argmax(axis=1))}
        cv.base(ax, (labels or {}).get(name, name))
        cv.show(ax, plurality_rgba(sh, cv))
        cv.overlay(ax, rivers=False)
    for ax in np.ravel(axs)[len(names):]:
        ax.axis("off")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _legend_cats(fig, present, y=0.0)
    _save(fig, path)


# ---------------------------------------------------------------------------------
# Animations
# ---------------------------------------------------------------------------------
def gif_plurality(sr, path: str, fps: int = 6, step: int = 1):
    cv = Canvas(sr.grid)
    years = sr.years[::step]
    if years[-1] != sr.years[-1]:
        years.append(sr.years[-1])
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    cv.base(ax)
    im = cv.show(ax, plurality_rgba(display_shares(sr.display(0)), cv))
    cv.overlay(ax, towns=_towns(sr))
    label = ax.text(0.02, 0.96, "", transform=ax.transAxes, fontsize=16, fontweight="bold", color=INK)
    ax.text(0.02, 0.91, "Most widely spoken home language", transform=ax.transAxes, fontsize=8.5, color=INK2)
    handles = [Patch(facecolor=CAT_COLOR[c], edgecolor="none", label=CAT_LABEL[c]) for c in CATS[:8]]
    ax.legend(handles=handles, loc="lower left", fontsize=7, frameon=False, handlelength=1)
    fig.tight_layout()

    def upd(y):
        im.set_data(plurality_rgba(display_shares(sr.display(sr.frame(y))), cv))
        label.set_text(str(y))
        return im, label

    anim = animation.FuncAnimation(fig, upd, frames=years, blit=False)
    anim.save(path, writer=animation.PillowWriter(fps=fps), dpi=90)
    plt.close(fig)


def gif_density(sr, path: str, fps: int = 6, step: int = 1):
    cv = Canvas(sr.grid)
    years = sr.years[::step]
    if years[-1] != sr.years[-1]:
        years.append(sr.years[-1])
    cmap = LinearSegmentedColormap.from_list("dens", ["#f4f3ee", "#c9dcf2", "#86b6ef", "#2a78d6", "#1c5cab",
                                                      "#0d366b", "#05172f"])
    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    cv.base(ax)
    im = cv.show(ax, np.ma.masked_invalid(cv.raster(np.maximum(sr.density(0), 2))), cmap=cmap,
                 norm=LogNorm(8, 8000))
    cv.overlay(ax, rivers=False, towns=_towns(sr))
    label = ax.text(0.02, 0.96, "", transform=ax.transAxes, fontsize=16, fontweight="bold", color=INK)
    sub = ax.text(0.02, 0.91, "", transform=ax.transAxes, fontsize=8.5, color=INK2)
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.01)
    cb.set_label("persons per km²", fontsize=8, color=MUTED)
    fig.tight_layout()

    def upd(y):
        j = sr.frame(y)
        im.set_data(np.ma.masked_invalid(cv.raster(np.maximum(sr.density(j), 2))))
        label.set_text(str(y))
        sub.set_text(f"Population {(sr.cells[j].sum() + sr.towns[j].sum()) / 1e6:.1f} M")
        return im, label, sub

    anim = animation.FuncAnimation(fig, upd, frames=years, blit=False)
    anim.save(path, writer=animation.PillowWriter(fps=fps), dpi=90)
    plt.close(fig)


def write_maps(sr, outdir: str, tag: str = "", gifs: bool = True) -> list[str]:
    os.makedirs(outdir, exist_ok=True)
    pre = f"{tag}_" if tag else ""
    out = []
    jobs = [("map_plurality", fig_plurality), ("map_language_shares", fig_language_shares),
            ("map_share_change", fig_share_change), ("map_density", fig_density),
            ("map_population_change", fig_pop_change)]
    for name, fn in jobs:
        p = os.path.join(outdir, f"{pre}{name}.png")
        fn(sr, p)
        out.append(p)
    if gifs:
        for name, fn in (("anim_languages", gif_plurality), ("anim_density", gif_density)):
            p = os.path.join(outdir, f"{pre}{name}.gif")
            fn(sr, p)
            out.append(p)
    return out
