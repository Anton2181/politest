"""Maps of language shift and population change, drawn from the spatial layer.

The colours follow ``report``: each language keeps its slot, and the
plurality maps fade toward the surface colour as the plurality share
falls.  Kashubian, Lemko-Rusyn, Wymysorys and the Latgalian (Latvian)
speech of Latgale are grouped as "regional languages" in the free red slot;
everything else is grey.
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
from matplotlib.patches import Patch, PathPatch, Polygon  # noqa: E402
from matplotlib.path import Path  # noqa: E402

from .data.geography import BBOX, build_grid, load_base_geography, load_borders  # noqa: E402
from .data.regions import REGIONS, state_of_code  # noqa: E402
from .data.languages import LANG_INDEX  # noqa: E402
from .report import INK, INK2, MUTED, OTHER, SLOTS, SURFACE, _save  # noqa: E402

CATS = ["pl", "uk", "yi", "be", "lt", "de", "pls", "reg", "oth"]
CAT_LABEL = {"pl": "Polish", "uk": "Ukrainian", "yi": "Yiddish", "be": "Belarusian", "lt": "Lithuanian",
             "de": "German", "pls": "West Polesian", "reg": "Kashubian, Lemko, Wymysorys, Latgalian",
             "oth": "Other (incl. Russian)"}
CAT_COLOR = dict(zip(CATS, SLOTS[:8] + [OTHER]))
CURZON = "#c4007f"          # the Curzon line: magenta, apart from borders and language colours
# national identity, drawn with the colour of the matching language category
IDCATS = ["pl", "uk", "jw", "be", "lt", "de", "loc", "reg", "oth"]
IDCAT_LABEL = {"pl": "Polish", "uk": "Ukrainian", "jw": "Jewish", "be": "Belarusian", "lt": "Lithuanian",
               "de": "German", "loc": "Local ('tutejszy')", "reg": "Kashubian, Lemko/Rusyn, Latvian, Silesian", "oth": "Other (incl. Russian)"}
REGIONAL = ["csb", "rue", "wym", "lv"]     # Latvian: the Latgalian speech of Latgale (include_krai_east)
SEA = "#eef3f6"
FOREIGN = "#efeee9"
WATER = "#a9c8dc"
BORDER = "#5d5c58"
LAT0 = 52.0
XLIM = (15.35, 29.0)        # fixed map extent, so scenarios with and without Lithuania align
XLIM_BY = (15.35, 33.0)     # ... widened for scenarios with Soviet Belarus
XLIM_WEST = 13.9            # ... and to the west for scenarios with German land (data.west)
YLIM = (47.85, 56.85)
YLIM_XK = (47.85, 57.55)    # ... raised for scenarios with Latgale (include_krai_east)
LABEL_TOWNS = ["Warszawa", "Łódź", "Kraków", "Lwów", "Poznań", "Wilno", "Kaunas", "Lublin", "Białystok", "Mińsk",
               "Witebsk", "Homel", "Mohylew",
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
        # state borders (CShapes, 1932): Poland, plus Lithuania and Soviet Belarus when the grid has them
        b = load_borders()
        present = {state_of_code(c) for c in grid.region_codes} | {"PL"}
        states = [s for s in ("PL", "LT", "BY", "XK", "DE", "DZ", "CS") if s in present]
        self.with_lt, self.with_by, self.with_xk = "LT" in states, "BY" in states, "XK" in states
        self.with_west = bool({"DE", "DZ", "CS"} & set(states))
        self.xlim = XLIM_BY if self.with_by else XLIM
        if self.with_west:
            self.xlim = (XLIM_WEST, self.xlim[1])
        self.ylim = YLIM_XK if self.with_xk else YLIM
        rings = [r[0] for st in states for r in b[st]]
        self.clip = Path.make_compound_path(*[Path(np.array(r), closed=True) for r in rings])
        # the Polish state alone (the Curzon line leaves Lithuania out)
        self.clip_pl = Path.make_compound_path(*[Path(np.array(r[0]), closed=True)
                                                 for st in states if st != "LT" for r in b[st]])
        # land of the whole state(s); cells missing from this grid were left out (``exclude``)
        whole = build_grid([r.code for r in REGIONS if state_of_code(r.code) in states], grid.dlat, grid.dlon)
        self.terr = np.zeros((self.H, self.W), dtype=bool)
        self.terr[self._rc(whole)] = True
        self.kept = np.zeros((self.H, self.W), dtype=bool)
        self.kept[self.row, self.col] = True
        key = "+".join(states)
        lines = b["outline"] if key == "PL+LT" else b.get("outlines", {}).get(key, rings)
        self.outline = self._split_lines(lines, inner=False) + self._excluded_edges()
        self.borders = (self._borders() + (self._split_lines(b["PL_LT"], inner=True) if self.with_lt else [])
                        + (self._split_lines(b["PL_BY"], inner=True) if self.with_by else [])
                        + (self._split_lines(b["BY_XK"], inner=True) if self.with_xk and "BY_XK" in b else [])
                        + [ln for pair, lines in b.get("inner", {}).items()
                           if set(pair.split("|")) <= set(states) for ln in self._split_lines(lines, inner=True)])

    def _rc(self, g):
        return (np.round((g.lat - (BBOX[1] + g.dlat / 2)) / g.dlat).astype(int),
                np.round((g.lon - (BBOX[0] + g.dlon / 2)) / g.dlon).astype(int))

    def _side(self, lon, lat, nx, ny):
        """Kept / excluded / unknown (1, 0, -1) for the first territory pixel
        found from (lon, lat) along the direction (nx, ny)."""
        for d in (0.5, 1.0, 2.0, 3.0):
            la, lo = lat + ny * d * self.g.dlat, lon + nx * d * self.g.dlon
            r = int(np.floor((la - BBOX[1]) / self.g.dlat))
            c = int(np.floor((lo - BBOX[0]) / self.g.dlon))
            if 0 <= r < self.H and 0 <= c < self.W and self.terr[r, c]:
                return int(self.kept[r, c])
        return -1

    def _split_lines(self, lines, inner: bool) -> list:
        """Keep the parts of the 1932 border lines that still bound this grid's
        territory: for the outline, where the land inside is kept; for the
        Polish-Lithuanian line (``inner``), where both sides are kept."""
        out = []
        for ln in lines:
            p = np.array(ln)
            run = [p[0]]
            for a, b in zip(p[:-1], p[1:]):
                d = b - a
                L = np.hypot(d[0], d[1]) or 1.0
                nx, ny = -d[1] / L, d[0] / L
                m = (a + b) / 2
                s1, s2 = self._side(m[0], m[1], nx, ny), self._side(m[0], m[1], -nx, -ny)
                keep = (s1 != 0 and s2 != 0) if inner else (max(s1, s2) == 1 or (s1 == s2 == -1))
                if keep:
                    run.append(b)
                else:
                    if len(run) > 1:
                        out.append(np.array(run))
                    run = [b]
            if len(run) > 1:
                out.append(np.array(run))
        return out

    def _excluded_edges(self) -> list:
        """Cell edges between kept territory and territory left out of the state."""
        ex = self.terr & ~self.kept
        if not ex.any():
            return []
        dl, dt = self.g.dlon, self.g.dlat
        x0, y0 = BBOX[0], BBOX[1]
        segs = []
        rr, cc = np.nonzero(self.kept[:, :-1] & ex[:, 1:] | ex[:, :-1] & self.kept[:, 1:])
        segs += [[(x0 + (c + 1) * dl, y0 + r * dt), (x0 + (c + 1) * dl, y0 + (r + 1) * dt)] for r, c in zip(rr, cc)]
        rr, cc = np.nonzero(self.kept[:-1, :] & ex[1:, :] | ex[:-1, :] & self.kept[1:, :])
        segs += [[(x0 + c * dl, y0 + (r + 1) * dt), (x0 + (c + 1) * dl, y0 + (r + 1) * dt)] for r, c in zip(rr, cc)]
        return segs

    def raster(self, values: np.ndarray, fill=np.nan, dilate: bool = True) -> np.ndarray:
        """Grid values as an image.  With ``dilate``, empty pixels next to the
        territory take a neighbour's value, so that the image clipped to the
        state border (``show``) has no gaps where a cell's centre lies just
        outside it."""
        values = np.asarray(values)
        img = np.full((self.H, self.W) + values.shape[1:], fill, dtype=float)
        img[self.row, self.col] = values
        if dilate:
            done = np.zeros((self.H, self.W), dtype=bool)
            done[self.row, self.col] = True
            filled = done.copy()
            src = img.copy()
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                # only past the state border (clipped there), never into land left out of the state
                take = np.roll(filled, (dr, dc), axis=(0, 1)) & ~done & ~self.terr
                img[take] = np.roll(src, (dr, dc), axis=(0, 1))[take]
                done |= take
        return img

    def _borders(self):
        codes = list(self.g.region_codes)
        parents = list(dict.fromkeys(c.split(".")[0] for c in codes))     # counties draw as their voivodeship
        pidx = np.array([parents.index(c.split(".")[0]) for c in codes])
        region = pidx[self.g.region]
        if "WAW" in parents and "WAR" in parents:      # the city region is drawn as part of its voivodeship
            region[region == parents.index("WAW")] = parents.index("WAR")
        reg = self.raster(region.astype(float), fill=-1, dilate=False)
        lt = np.array([state_of_code(p) for p in parents])
        dl, dt = self.g.dlon, self.g.dlat
        x0, y0 = BBOX[0], BBOX[1]
        inner = []

        def internal(a, b):     # a border between two regions of the same state
            return min(a, b) >= 0 and a != b and lt[int(a)] == lt[int(b)]
        for r in range(self.H):
            for c in range(self.W):
                a = reg[r, c]
                if c + 1 < self.W and internal(a, reg[r, c + 1]):
                    inner.append([(x0 + (c + 1) * dl, y0 + r * dt), (x0 + (c + 1) * dl, y0 + (r + 1) * dt)])
                if r + 1 < self.H and internal(a, reg[r + 1, c]):
                    inner.append([(x0 + c * dl, y0 + (r + 1) * dt), (x0 + (c + 1) * dl, y0 + (r + 1) * dt)])
        return inner

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
        im.set_clip_path(PathPatch(self.clip, transform=ax.transData))
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
    fig.text(0.01, 0.005, "Colour: most widely spoken home language in each 3.5 km cell; pale = plurality below "
             "about 50 %. Towns are drawn as areas at urban density.", fontsize=8, color=INK2)
    _save(fig, path)


def fig_curzon(sr, lines: list[dict], path: str, years=(1932, 1982, 2032), title: str = ""):
    """Plurality map with the equal-exchange Curzon line (``plsim.curzon``) of each year."""
    cv = Canvas(sr.grid)
    by_year = {s["year"]: s for s in lines}
    years = [y for y in years if y in by_year]
    fig, axs = plt.subplots(1, len(years), figsize=(4.6 * len(years), 5.6))
    present = set()
    for ax, y in zip(np.atleast_1d(axs), years):
        sh = display_shares(sr.display(sr.frame(y)))
        present |= {CATS[i] for i in np.unique(sh.argmax(axis=1))}
        cv.base(ax, str(y))
        cv.show(ax, plurality_rgba(sh, cv))
        cv.overlay(ax, rivers=False)
        s = by_year[y]
        for lw, col in ((3.2, "white"), (1.6, CURZON)):
            ax.add_collection(LineCollection([np.asarray(ln) for ln in s["lines"]], colors=col, linewidths=lw,
                                             zorder=7, capstyle="round", joinstyle="round"))
        ax.text(0.02, 0.02, f"Polish side: {s['west'] / 1e6:.1f} M counted, {s['west_others'] / 1e6:.1f} M not Polish\n"
                f"Other side: {s['east_poles'] / 1e6:.1f} M Poles, {s['east_others'] / 1e6:.1f} M others",
                transform=ax.transAxes, fontsize=7.5, color=INK, path_effects=_halo(), zorder=8)
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.09, 1, 0.95 if title else 1))
    _legend_cats(fig, present, y=0.035)
    fig.text(0.01, 0.005, "Magenta line: the line along county borders that leaves as many non-Poles on its Polish side "
             "as Poles on the other (to within a county), with the most Poles on the Polish side. Kashubians, "
             "Wymysorys, Germans and Jews are not counted.", fontsize=8, color=INK2)
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


# ---------------------------------------------------------------------------------
# National identity and ensemble certainty
# ---------------------------------------------------------------------------------
def identity_shares(I: np.ndarray) -> np.ndarray:
    """(R, NI) identity counts -> (R, 9) shares in IDCATS order."""
    from .identity import IDENTITIES
    idx = {k: i for i, k in enumerate(IDENTITIES)}
    out = np.zeros((len(I), len(IDCATS)))
    for k, c in enumerate(IDCATS[:7]):
        out[:, k] = I[:, idx[c]]
    out[:, 7] = I[:, idx["csb"]] + I[:, idx["rue"]] + I[:, idx["lv"]] + I[:, idx["sil"]]
    out[:, 8] = I.sum(axis=1) - out[:, :8].sum(axis=1)
    return np.clip(out / np.maximum(I.sum(axis=1, keepdims=True), 1e-9), 0, 1)


def identity_at(res, year: int) -> np.ndarray:
    """(R, NI) identity counts at 1 January of ``year``."""
    if year == res.params["start_year"] and res.identity0 is not None:
        return np.asarray(res.identity0)
    return np.asarray(res.identity[res.years.index(year)])


def fig_identity(sr, res, path: str, years=(1932, 1982, 2032), title: str = ""):
    """Most common national identity of each county (identity is tracked by
    county, not by cell), beside the most common home language."""
    cv = Canvas(sr.grid)
    g = sr.grid
    fig, axs = plt.subplots(2, len(years), figsize=(4.4 * len(years), 10.2))
    for j, y in enumerate(years):
        ax = axs[0, j]
        cv.base(ax, f"Home language, {y}" if j == 0 else str(y))
        cv.show(ax, plurality_rgba(display_shares(sr.display(sr.frame(y))), cv))
        cv.overlay(ax, rivers=False)
        ax = axs[1, j]
        sh = identity_shares(identity_at(res, y))[g.region]
        cv.base(ax, f"National identity, {y}" if j == 0 else str(y))
        cv.show(ax, plurality_rgba(sh, cv))
        cv.overlay(ax, rivers=False)
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.07, 1, 0.96 if title else 1))
    handles = [Patch(facecolor=CAT_COLOR[c], edgecolor="none",
                     label=CAT_LABEL[c] if CAT_LABEL[c] == IDCAT_LABEL[i] else f"{CAT_LABEL[c]} / {IDCAT_LABEL[i]}")
               for c, i in zip(CATS, IDCATS)]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0), fontsize=8.5, frameon=False)
    _save(fig, path)


def plurality_probability(cells: np.ndarray) -> np.ndarray:
    """(members, Nc, NL) language shares -> (Nc, 9): share of members in
    which each map category is the most spoken home language of the cell."""
    out = np.zeros((cells.shape[1], len(CATS)))
    for S in cells:
        top = display_shares(S.astype(np.float32)).argmax(axis=1)
        out[np.arange(len(top)), top] += 1
    return out / len(cells)


def fig_uncertainty(grid, prob: dict, path: str, n: int, title: str = ""):
    """Ensemble certainty: the most likely leading language of each cell,
    paler where fewer runs agree; and the probability that Belarusian,
    Ukrainian or Lithuanian leads."""
    cv = Canvas(grid)
    years = sorted(prob)
    show = ("be", "uk", "lt")
    fig, axs = plt.subplots(len(years), 1 + len(show), figsize=(4.2 * (1 + len(show)), 4.6 * len(years) + 0.9))
    axs = np.atleast_2d(axs)
    fig.subplots_adjust(left=0.01, right=0.95, top=0.93 if title else 0.97, bottom=0.11, wspace=0.04, hspace=0.12)
    for i, y in enumerate(years):
        P = prob[y]
        k = P.argmax(axis=1)
        p = P.max(axis=1)
        t = np.clip((p - 0.34) / 0.66, 0.12, 1.0)[:, None]
        base = np.array([_hex(CAT_COLOR[c]) for c in CATS])[k]
        rgb = base * t + _hex(SURFACE)[None, :] * (1 - t)
        ax = axs[i, 0]
        cv.base(ax, f"Most likely leading language, {y}")
        cv.show(ax, cv.raster(np.column_stack([rgb, np.ones(len(rgb))]), fill=0.0))
        cv.overlay(ax, rivers=False)
        unsure = (p < 0.8).mean()
        ax.text(0.02, 0.02, f"{unsure * 100:.0f}% of cells: leader in under 80% of runs", transform=ax.transAxes,
                fontsize=8, color=INK2, path_effects=_halo())
        for j, c in enumerate(show):
            ax = axs[i, 1 + j]
            q = P[:, CATS.index(c)]
            cv.base(ax, f"P({CAT_LABEL[c]} leads), {y}")
            img = cv.raster(np.where(q > 0, q, np.nan))
            im = cv.show(ax, np.ma.masked_invalid(img), cmap=_seq_cmap(CAT_COLOR[c]), vmin=0, vmax=1)
            cv.overlay(ax, rivers=False, inner_color="#d9d8d2")
        pos = axs[i, -1].get_position()
        cax = fig.add_axes([pos.x1 + 0.006, pos.y0 + 0.15 * pos.height, 0.008, 0.7 * pos.height])
        cb = fig.colorbar(im, cax=cax)
        cb.ax.tick_params(labelsize=7)
        cb.set_label("share of runs", fontsize=8)
    if title:
        fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK)
    _legend_cats(fig, None, y=0.035)
    fig.text(0.01, 0.008, f"Ensemble of {n} runs of the baseline (parameters drawn from their uncertainty ranges and the "
             "calibrated set, own random shocks), each downscaled to the 3.5 km grid. Left: paler where fewer runs "
             "agree on the leading language.", fontsize=8, color=INK2)
    _save(fig, path)
