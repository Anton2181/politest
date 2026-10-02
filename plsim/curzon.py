"""An "equal-exchange Curzon line" for any year of a scenario.

The line is any continuous line across the whole state of the scenario
(Poland, with Lithuania in the union scenarios and Soviet Belarus where it is
part of the state), from one point of its outer border to another. It may wind
freely, cell by cell on the 3.5 km map grid, even through counties. It
divides the state into a Polish side and an other side, both in one piece,
so that

    non-Poles left on the Polish side  =  Poles left on the other side,

and, among all such lines, the Polish side holds as many Poles as possible.

Who is counted. Poles are the speakers of Polish at home. Kashubians,
Wymysorys speakers, Germans and Jews (by community, whatever their home
language) are left out of the count altogether: they are neither Poles nor
non-Poles. Everyone else (Ukrainians, Belarusians, West Polesians,
Lithuanians, Russians, Lemkos ...) is a non-Pole.

Since the non-Poles on the Polish side plus the Poles on the Polish side
make up the people counted there, and the Poles on both sides make up all
Poles, the condition is the same as: *the Polish side holds exactly as many
counted people as there are Poles*. The task is to find the most Polish
connected region of that size whose complement is connected too; the line is
their common boundary. Without the requirement of one piece on each side the
answer would be the most Polish cells wherever they lie; with it, Polish
islands far inside the other side are only taken in if a corridor to them
pays its way.

Method (a heuristic for a hard combinatorial problem):

1. Grow the Polish side from its most Polish large cell, always adding the
   most Polish cell on its edge, until it holds the target number of people.
2. Pieces of the other side cut off by this growth join the Polish side, so
   that both sides are in one piece.
3. Improve by exchange: while the side is too large, give away the least
   Polish cell on its edge; while too small, take the most Polish cell on
   the other side's edge. A cell only moves if neither side is split by it
   (a local test on its eight neighbours). Stop when the exchanges no longer
   add Poles.
4. The balance is made exact inside the last cell moved, whose people are
   split pro rata.
"""
from __future__ import annotations

import heapq

import numpy as np
from scipy import ndimage

from .data.geography import BBOX
from .data.languages import GROUPS, LANG_INDEX, NL

EXCLUDED_LANGS = ("csb", "wym", "de", "yi")      # Kashubian, Wymysorys, German; Yiddish (Jews)
EXCLUDED_COMMUNITIES = ("JW", "JH")              # Jews, whatever their home language
KX = 111.2 * np.cos(np.radians(52.0))            # km per degree of longitude (map projection)
KY = 111.2
OUT, POL, OTH = 0, 1, 2                          # cell labels: abroad, Polish side, other side
NB4 = ((-1, 0), (0, 1), (1, 0), (0, -1))
RING = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))   # N, NE, E ... NW


def excluded_share(res, year: int) -> np.ndarray:
    """(R, NL): share of each language's speakers in each region who are left
    out of the count (all speakers of the excluded languages; Jews of any
    other language)."""
    years = list(res.years)
    t = int(np.argmin([abs(y - year) for y in years]))
    P = np.asarray(res.pop[t], float)
    by_group = P.reshape(P.shape[0], P.shape[1], P.shape[2], -1).sum(axis=(1, 3))      # (R, G)
    lang = np.array([LANG_INDEX[l] for _, l in GROUPS])
    jew = np.array([c in EXCLUDED_COMMUNITIES for c, _ in GROUPS])
    tot = np.zeros((P.shape[0], NL))
    exc = np.zeros((P.shape[0], NL))
    np.add.at(tot.T, lang, by_group.T)
    np.add.at(exc.T, lang[jew], by_group[:, jew].T)
    f = np.where(tot > 0, exc / np.maximum(tot, 1e-12), 0.0)
    for l in EXCLUDED_LANGS:
        f[:, LANG_INDEX[l]] = 1.0
    return f


def _keeps_connected(lab, r, c, side) -> bool:
    """Can cell (r, c) leave ``side`` without splitting it? True when the
    side's cells among its eight neighbours that touch it edge-on are joined
    to each other around the ring (sufficient for 4-connectivity)."""
    ring = [lab[r + dr, c + dc] == side for dr, dc in RING]
    if not any(ring[k] for k in (0, 2, 4, 6)):
        return False                                  # no edge-on neighbour of its side
    if all(ring):
        return True
    start = ring.index(False)
    runs, in_run, has_orth = 0, False, False
    for k in range(1, 9):
        j = (start + k) % 8
        if ring[j]:
            if not in_run:
                in_run, has_orth = True, False
            has_orth |= j % 2 == 0
        elif in_run:
            runs += has_orth
            in_run = False
    if in_run:
        runs += has_orth
    return runs == 1


def _partition(lab, C, Pp, share, target, max_moves=400000):
    """Steps 1-4 of the module docstring on a padded label raster ``lab``
    (cells of the state labelled OTH on entry). Returns (lab, Poles on the
    Polish side at exact balance)."""
    H, W = lab.shape
    inside = lab != OUT
    # 1. grow from the most Polish large cell
    big = np.where(inside & (C > np.percentile(C[inside], 90)), share, -np.inf)
    seed = np.unravel_index(int(np.argmax(big)), big.shape)
    lab[seed] = POL
    cA, pA = C[seed], Pp[seed]
    heap, tick = [], 0

    def push_front(r, c):
        nonlocal tick
        for dr, dc in NB4:
            rr, cc = r + dr, c + dc
            if lab[rr, cc] == OTH:
                tick += 1
                heapq.heappush(heap, (-share[rr, cc], tick, rr, cc))
    push_front(*seed)
    while heap and cA < target:
        _, _, r, c = heapq.heappop(heap)
        if lab[r, c] != OTH:
            continue
        lab[r, c] = POL
        cA += C[r, c]
        pA += Pp[r, c]
        push_front(r, c)
    # 2. the other side in one piece: cut-off pieces join the Polish side
    comp, n = ndimage.label(lab == OTH)
    if n > 1:
        sizes = ndimage.sum(C + 1e-9, comp, index=np.arange(1, n + 1))
        keep = 1 + int(np.argmax(sizes))
        cut = (comp > 0) & (comp != keep)
        lab[cut] = POL
        cA, pA = C[lab == POL].sum(), Pp[lab == POL].sum()

    # 3. exchange along the line
    edge_pol, edge_oth = [], []

    def touches(r, c, side):
        return any(lab[r + dr, c + dc] == side for dr, dc in NB4)

    def push(r, c):
        nonlocal tick
        tick += 1
        if lab[r, c] == POL and touches(r, c, OTH):
            heapq.heappush(edge_pol, (share[r, c], tick, r, c))
        elif lab[r, c] == OTH and touches(r, c, POL):
            heapq.heappush(edge_oth, (-share[r, c], tick, r, c))
    rr, cc = np.nonzero(lab != OUT)
    for r, c in zip(rr, cc):
        push(r, c)

    def take(heap_, side, sign):
        while heap_:
            s, _, r, c = heapq.heappop(heap_)
            other = OTH if side == POL else POL
            if lab[r, c] == side and touches(r, c, other) and _keeps_connected(lab, r, c, side):
                return r, c, sign * s
        return None

    best_pa, best_lab, last_gain, crossings = -np.inf, lab.copy(), 0, 0
    above = cA > target
    for _ in range(max_moves):
        mv = take(edge_pol, POL, 1) if cA > target else take(edge_oth, OTH, -1)
        if mv is None:
            break
        r, c, s = mv
        if cA > target:
            lab[r, c] = OTH
            cA -= C[r, c]
            pA -= Pp[r, c]
        else:
            lab[r, c] = POL
            cA += C[r, c]
            pA += Pp[r, c]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if lab[r + dr, c + dc] != OUT:
                    push(r + dr, c + dc)
        now_above = cA > target
        if now_above != above:                      # crossed the target: score at exact balance
            crossings += 1
            pa_bal = pA - (cA - target) * max(s, 0.0)
            if pa_bal > best_pa + 1e-6 * max(target, 1.0):
                best_pa, best_lab, last_gain = pa_bal, lab.copy(), crossings
            elif crossings - last_gain > 60:
                break
            above = now_above
    if best_pa == -np.inf:                          # never crossed: balance inside the last cell
        best_pa, best_lab = pA - (cA - target) * float(np.clip(Pp.sum() / max(C.sum(), 1e-9), 0, 1)), lab.copy()
    return best_lab, float(best_pa)


def _rdp(pts: np.ndarray, tol: float) -> np.ndarray:
    """Ramer-Douglas-Peucker simplification of a polyline."""
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    d = b - a
    L = np.hypot(*d) or 1e-12
    dist = np.abs(d[0] * (pts[:, 1] - a[1]) - d[1] * (pts[:, 0] - a[0])) / L
    k = int(np.argmax(dist))
    if dist[k] <= tol:
        return np.array([a, b])
    return np.vstack([_rdp(pts[:k + 1], tol)[:-1], _rdp(pts[k:], tol)])


def _interface(lab, r0, c0, dlat, dlon, tol=0.01) -> list[np.ndarray]:
    """The line: the cell edges between the two sides, chained into
    polylines (lon, lat) and simplified."""
    edges = []
    A, B = lab == POL, lab == OTH
    for r, c in zip(*np.nonzero((A[:, :-1] & B[:, 1:]) | (B[:, :-1] & A[:, 1:]))):
        edges.append(((r, c + 1), (r + 1, c + 1)))
    for r, c in zip(*np.nonzero((A[:-1, :] & B[1:, :]) | (B[:-1, :] & A[1:, :]))):
        edges.append(((r + 1, c), (r + 1, c + 1)))
    at: dict = {}
    for k, (p, q) in enumerate(edges):
        at.setdefault(p, []).append(k)
        at.setdefault(q, []).append(k)
    used = np.zeros(len(edges), bool)
    lines = []
    while not used.all():
        odd = [p for p, ks in at.items() if sum(not used[k] for k in ks) % 2 == 1]
        start = odd[0] if odd else edges[int(np.argmin(used))][0]
        path, p = [start], start
        while True:
            nxt = [k for k in at[p] if not used[k]]
            if not nxt:
                break
            k = nxt[0]
            used[k] = True
            p = edges[k][1] if edges[k][0] == p else edges[k][0]
            path.append(p)
        if len(path) > 1:
            xy = np.array([[BBOX[0] + (c0 + c) * dlon, BBOX[1] + (r0 + r) * dlat] for r, c in path])
            lines.append(_rdp(xy, tol))
    lines.sort(key=len, reverse=True)
    return lines


def split(lat, lon, poles, people, dlat: float, dlon: float) -> dict:
    """Equal-exchange line for cells at (lat, lon) with ``poles`` and counted
    ``people`` (persons). Returns the line (polylines of lon/lat), the side of
    each cell (True = Polish side) and the counts ("west" is the Polish side)."""
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    poles, people = np.asarray(poles, float), np.asarray(people, float)
    rows = np.round((lat - (BBOX[1] + dlat / 2)) / dlat).astype(int)
    cols = np.round((lon - (BBOX[0] + dlon / 2)) / dlon).astype(int)
    r0, c0 = rows.min() - 1, cols.min() - 1
    H, W = rows.max() - r0 + 2, cols.max() - c0 + 2
    ri, ci = rows - r0, cols - c0
    lab = np.zeros((H, W), np.int8)
    C, Pp = np.zeros((H, W)), np.zeros((H, W))
    lab[ri, ci] = OTH
    np.add.at(C, (ri, ci), people)
    np.add.at(Pp, (ri, ci), poles)
    share = np.where(C > 0, Pp / np.maximum(C, 1e-12), 0.0)
    target = float(poles.sum())
    # land that does not touch the main body (islands, the Hel tip ...) stays on its majority's side
    comp, n = ndimage.label(lab != OUT)
    sizes = ndimage.sum(np.ones_like(C), comp, index=np.arange(1, n + 1))
    islands = (comp > 0) & (comp != 1 + int(np.argmax(sizes)))
    isl_pol, isl_oth = islands & (share >= 0.5), islands & (share < 0.5)
    work = lab.copy()
    work[islands] = OUT
    work, pa_main = _partition(work, C, Pp, share, target - C[isl_pol].sum())
    final = work.copy()
    final[isl_pol], final[isl_oth] = POL, OTH
    pa = pa_main + float(Pp[isl_pol].sum())
    total = float(people.sum())
    return {"lines": _interface(work, r0, c0, dlat, dlon),
            "polish_side": final[ri, ci] == POL, "poles": target, "people": total,
            "west": target, "west_poles": pa, "west_others": target - pa,
            "east_poles": target - pa, "east_others": total - target - (target - pa)}


def lines_for(sr, res, years) -> list[dict]:
    """The line for each of ``years`` in a downscaled scenario
    (``spatial.SpatialResult``) and its run (which gives the community of
    each language's speakers, region by region)."""
    g = sr.grid
    pl = LANG_INDEX["pl"]
    out = []
    for y in years:
        X = sr.display(sr.frame(y))                     # (cells, languages), persons
        keep = 1.0 - excluded_share(res, y)[g.region]    # (cells, languages)
        people = (X * keep).sum(axis=1)
        poles = X[:, pl] * keep[:, pl]
        s = split(g.lat, g.lon, poles, people, g.dlat, g.dlon)
        s["year"] = int(y)
        s["excluded"] = float(X.sum() - people.sum())
        out.append(s)
    return out


FIELDS = ["year", "poles", "people", "excluded", "west", "west_poles", "west_others", "east_poles", "east_others"]


def write_csv(lines: list[dict], path: str) -> str:
    """One row per year: counted persons on each side of the line ("west" is
    the Polish side), the persons not counted, and the line (polylines of
    lon,lat points separated by " | ")."""
    import csv
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS + ["line_lon_lat"])
        for s in lines:
            w.writerow([s["year"]] + [round(s[k]) for k in FIELDS[1:]]
                       + [" | ".join(" ".join(f"{x:.3f},{y:.3f}" for x, y in ln) for ln in s["lines"])])
    return path
