"""An "equal-exchange Curzon line" for any year of a scenario.

The line is a continuous line across the whole state of the scenario
(Poland, with Lithuania in the union scenarios and Soviet Belarus where it is
part of the state), from one point of its outer border to another, that
follows county borders: every county lies wholly on one side. It divides the
state into a Polish side and an other side, both in one piece, so that

    non-Poles left on the Polish side  =  Poles left on the other side,

and, among all such lines, the Polish side holds as many Poles as possible.
With whole counties the two sides balance only to within a county; the
residual is reported. (``split`` without ``units`` draws the line cell by
cell on the 3.5 km grid instead, with exact balance; the maps used that
until the county version replaced it as less noisy.)

Who is counted. Poles are the speakers of Polish at home. Kashubians,
Wymysorys speakers, Germans and Jews (by community, whatever their home
language) are left out of the count altogether: they are neither Poles nor
non-Poles. Everyone else (Ukrainians, Belarusians, West Polesians,
Lithuanians, Russians, Lemkos ...) is a non-Pole.

Since the non-Poles on the Polish side plus the Poles on the Polish side
make up the people counted there, and the Poles on both sides make up all
Poles, the condition is the same as: *the Polish side holds as many counted
people as there are Poles*. The task is to find the most Polish connected
set of counties of that size whose complement is connected too; the line
is their common border.

County method: grow the Polish side from its most Polish large county,
always taking the most Polish county on its edge, but never one that would
cut the other side in two unless every piece cut off is Polish-majority
(those pieces then join the Polish side; a cut-off Lithuania would not);
then exchange counties along the line, each move keeping both sides in one
piece, and keep the best crossing of the target (scored by the Poles held at
exact balance, the last county counted pro rata), taking whichever of its
two whole-county states is nearer to balance.

Cell method (``units=None``), a heuristic for the same problem on cells:

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


# The historical Curzon line: the Allied declaration of 8 December 1919 and
# Curzon's note of 11 July 1920, with "line A" in Eastern Galicia (Lwów on
# the other side; "line B" would have given Lwów and Drohobych to Poland).
# Digitised approximately (to about 10 km) from its description, north to
# south: the eastern and northern boundary of the Suwałki district from the
# East Prussian border to the Niemen, the Niemen past Grodno, the Łosośna to
# its source, south-west past Jałówka and east of Hajnówka to the Bug at
# Niemirów, the Bug upstream past Brest, Włodawa, Dorohusk and Uściług to
# Kryłów, then west of Rawa Ruska and east of Przemyśl to the Carpathians.
# (lat, lon), south to north.
HISTORICAL_LINE = np.array([
    (49.00, 22.86), (49.30, 22.85), (49.55, 22.92), (49.78, 22.97), (50.00, 23.15), (50.24, 23.45),
    (50.45, 23.80), (50.68, 24.07), (50.86, 24.15), (51.02, 24.02), (51.17, 23.82), (51.40, 23.65),
    (51.55, 23.55), (51.80, 23.60), (52.08, 23.62), (52.20, 23.38), (52.36, 23.12), (52.55, 23.45),
    (52.74, 23.70), (53.02, 23.92), (53.35, 23.98), (53.66, 23.78), (53.85, 23.90), (54.00, 23.97),
    (54.18, 23.50), (54.33, 23.05), (54.38, 22.78)])
# closes the Polish (west) side around East Prussia, the Baltic and the west
_HIST_CLOSE = np.array([(54.38, 19.6), (56.5, 19.6), (56.5, 10.0), (47.0, 10.0), (47.0, 22.86)])


def historical_side(lat, lon) -> np.ndarray:
    """True for points west of (on the Polish side of) the historical line."""
    from matplotlib.path import Path
    poly = np.vstack([HISTORICAL_LINE, _HIST_CLOSE])[:, ::-1]           # (lon, lat)
    return Path(poly).contains_points(np.column_stack([np.asarray(lon, float), np.asarray(lat, float)]))


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


def _unit_adjacency(U: np.ndarray, n: int) -> list:
    """Neighbour sets of units (counties) from a raster of unit ids (-1 outside)."""
    adj = [set() for _ in range(n)]
    for a, b in ((U[:, :-1], U[:, 1:]), (U[:-1, :], U[1:, :])):
        m = (a >= 0) & (b >= 0) & (a != b)
        for x, y in set(zip(a[m].tolist(), b[m].tolist())):
            adj[x].add(y)
            adj[y].add(x)
    return adj


def _connected(members: set, adj: list) -> bool:
    if not members:
        return False
    start = next(iter(members))
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v in members and v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(members)


def _partition_units(adj: list, C: np.ndarray, Pp: np.ndarray, target: float, units: set,
                     max_moves: int = 5000, tabu: int = 6) -> tuple[set, float]:
    """The county version of steps 1-4: whole units on each side, both sides
    connected on the unit graph. Every crossing of the target is scored by the
    Poles the Polish side would hold at exact balance (the last unit counted
    pro rata), as in the cell version; of the two whole-unit states around the
    best crossing, the one nearer to balance is kept. Returns (Polish units,
    Poles on the Polish side at exact balance)."""
    share = np.where(C > 0, Pp / np.maximum(C, 1e-12), 0.0)
    cand = [u for u in units if C[u] > 0]
    big = np.percentile(C[cand], 75) if cand else 0.0
    seed = max((u for u in units if C[u] >= big), key=lambda u: share[u])
    pol = {seed}
    cA, pA = C[seed], Pp[seed]
    heap, tick = [], 0
    for v in adj[seed]:
        if v in units:
            tick += 1
            heapq.heappush(heap, (-share[v], tick, v))
    oth = units - pol

    def pieces_of(members):
        out, left = [], set(members)
        while left:
            start = left.pop()
            comp, stack = {start}, [start]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y in left:
                        left.discard(y)
                        comp.add(y)
                        stack.append(y)
            out.append(comp)
        return out

    while heap and cA < target:
        _, _, u = heapq.heappop(heap)
        if u in pol:
            continue
        add = {u}
        rest = oth - {u}
        if not _connected(rest, adj):
            # the move cuts the other side: the piece with the most non-Poles
            # stays; the others may join the Polish side only if they are
            # Polish-majority (a remote Polish district, not a whole Lithuania)
            parts = pieces_of(rest)
            main = max(parts, key=lambda c: (C[list(c)] - Pp[list(c)]).sum())
            cut = [c for c in parts if c is not main]
            if any(Pp[list(c)].sum() < 0.5 * C[list(c)].sum() for c in cut):
                continue
            for c in cut:
                add |= c
        for x in add:
            pol.add(x)
            oth.discard(x)
            cA += C[x]
            pA += Pp[x]
            for v in adj[x]:
                if v in units and v not in pol:
                    tick += 1
                    heapq.heappush(heap, (-share[v], tick, v))
    # the other side in one piece: cut-off pieces join the Polish side
    pieces, left = [], set(oth)
    while left:
        start = left.pop()
        comp, stack = {start}, [start]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v in left:
                    left.discard(v)
                    comp.add(v)
                    stack.append(v)
        pieces.append(comp)
    if len(pieces) > 1:
        keep = max(pieces, key=lambda c: C[list(c)].sum())
        for comp in pieces:
            if comp is not keep:
                pol |= comp
        oth = keep
        cA, pA = C[list(pol)].sum(), Pp[list(pol)].sum()
    # exchange along the line
    last = {}
    best, best_score, last_gain, crossings = set(pol), -np.inf, 0, 0
    above = cA > target
    for step in range(max_moves):
        if cA > target:
            side, other, rev = pol, oth, False
        else:
            side, other, rev = oth, pol, True
        edge = [u for u in side if any(v in other for v in adj[u]) and step - last.get(u, -tabu) >= tabu]
        edge.sort(key=lambda u: share[u], reverse=rev)
        mv = next((u for u in edge if _connected(side - {u}, adj)), None)
        if mv is None:
            break
        prev = set(pol)
        side.discard(mv)
        other.add(mv)
        last[mv] = step
        d = C[mv] if other is pol else -C[mv]
        cA += d
        pA += Pp[mv] if other is pol else -Pp[mv]
        now_above = cA > target
        if now_above != above:
            crossings += 1
            score = pA - (cA - target) * share[mv]
            if score > best_score + 1e-6 * max(target, 1.0):
                near_now = abs(cA - target) <= abs(cA - d - target)
                best, best_score, last_gain = (set(pol) if near_now else prev), score, crossings
            elif crossings - last_gain > 60:
                break
            above = now_above
    if best_score == -np.inf:
        best_score = pA
    return best, float(best_score)


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


def split(lat, lon, poles, people, dlat: float, dlon: float, units=None) -> dict:
    """Equal-exchange line for cells at (lat, lon) with ``poles`` and counted
    ``people`` (persons). Returns the line (polylines of lon/lat), the side of
    each cell (True = Polish side) and the counts ("west" is the Polish side).
    With ``units`` (the county of each cell) whole counties go to one side and
    the line follows county borders; the balance is then exact only to within
    a county, and ``residual`` (counted people on the Polish side minus all
    Poles) says by how much."""
    if units is not None:
        return _split_units(lat, lon, poles, people, dlat, dlon, np.asarray(units))
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
            "east_poles": target - pa, "east_others": total - target - (target - pa), "residual": 0.0}


def _split_units(lat, lon, poles, people, dlat, dlon, units) -> dict:
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    poles, people = np.asarray(poles, float), np.asarray(people, float)
    rows = np.round((lat - (BBOX[1] + dlat / 2)) / dlat).astype(int)
    cols = np.round((lon - (BBOX[0] + dlon / 2)) / dlon).astype(int)
    r0, c0 = rows.min() - 1, cols.min() - 1
    H, W = rows.max() - r0 + 2, cols.max() - c0 + 2
    ri, ci = rows - r0, cols - c0
    ids, u = np.unique(units, return_inverse=True)
    n = len(ids)
    U = np.full((H, W), -1, int)
    U[ri, ci] = u
    C = np.bincount(u, people, n)
    Pp = np.bincount(u, poles, n)
    adj = _unit_adjacency(U, n)
    target = float(poles.sum())
    # units that do not touch the main body (islands) stay on their majority's side
    comps, left = [], set(range(n))
    while left:
        start = left.pop()
        comp, stack = {start}, [start]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y in left:
                    left.discard(y)
                    comp.add(y)
                    stack.append(y)
        comps.append(comp)
    main = max(comps, key=lambda c: C[list(c)].sum())
    share = np.where(C > 0, Pp / np.maximum(C, 1e-12), 0.0)
    isl_pol = {x for c in comps if c is not main for x in c if share[x] >= 0.5}
    pol, pa_bal = _partition_units(adj, C, Pp, target - C[list(isl_pol)].sum() if isl_pol else target, main)
    pol = pol | isl_pol
    lab = np.zeros((H, W), np.int8)
    lab[ri, ci] = OTH
    in_pol = np.isin(u, list(pol))
    lab[ri[in_pol], ci[in_pol]] = POL
    work = lab.copy()
    isl_cells = np.isin(u, [x for c in comps if c is not main for x in c])
    work[ri[isl_cells], ci[isl_cells]] = OUT
    west = float(C[list(pol)].sum())
    pa = float(Pp[list(pol)].sum())
    total = float(people.sum())
    return {"lines": _interface(work, r0, c0, dlat, dlon, tol=0.004),
            "polish_side": in_pol, "poles": target, "people": total,
            "west": west, "west_poles": pa, "west_others": west - pa,
            "east_poles": target - pa, "east_others": total - west - (target - pa),
            "residual": west - target, "poles_at_balance": pa_bal}


# Counting by declared nationality (``curzon_count: identity``): Poles are the
# people of Polish national identity (plsim.identity), whatever their home
# language; Jews, Germans and Kashubians by identity are not counted.
ID_EXCLUDED = ("jw", "de", "csb")


def count_mode(res) -> str:
    return (getattr(res, "params", None) or {}).get("curzon_count", "language")


def identity_cells(sr, res, year: int) -> np.ndarray:
    """(cells, NI) persons by national identity: each cell's speakers of a
    language take their region's identity mix for that language (the run's
    ``identity_lang`` at the nearest snapshot year)."""
    IL = res.identity_lang
    y = min(IL, key=lambda t: abs(t - year))
    L = np.asarray(IL[y], float)                                        # (R, NL, NI)
    sh = L / np.maximum(L.sum(axis=2, keepdims=True), 1e-12)
    X = sr.display(sr.frame(year))                                      # (cells, NL)
    return np.einsum("cl,cli->ci", X, sh[sr.grid.region])


def counts(sr, res, year: int, count: str | None = None):
    """(Poles, counted people, persons not counted) per cell."""
    count = count or count_mode(res)
    X = sr.display(sr.frame(year))                     # (cells, languages), persons
    if count == "identity":
        from .identity import ID_INDEX
        Icell = identity_cells(sr, res, year)
        exc = Icell[:, [ID_INDEX[k] for k in ID_EXCLUDED]].sum(axis=1)
        people = Icell.sum(axis=1) - exc
        return Icell[:, ID_INDEX["pl"]], people, float(X.sum() - people.sum())
    pl = LANG_INDEX["pl"]
    keep = 1.0 - excluded_share(res, year)[sr.grid.region]   # (cells, languages)
    people = (X * keep).sum(axis=1)
    return X[:, pl] * keep[:, pl], people, float(X.sum() - people.sum())


def lines_for(sr, res, years, count: str | None = None) -> list[dict]:
    """The line for each of ``years`` in a downscaled scenario
    (``spatial.SpatialResult``) and its run (which gives the community of
    each language's speakers, region by region). ``count``: "language"
    (Poles speak Polish at home; the default) or "identity" (Poles by
    declared nationality); by default the scenario's ``curzon_count``."""
    g = sr.grid
    w = historical_side(g.lat, g.lon)
    out = []
    for y in years:
        poles, people, excluded = counts(sr, res, y, count)
        s = split(g.lat, g.lon, poles, people, g.dlat, g.dlon, units=g.region)
        s["year"] = int(y)
        s["excluded"] = excluded
        # the same count on either side of the historical line
        s["hist_west_poles"] = float(poles[w].sum())
        s["hist_west_others"] = float(people[w].sum() - poles[w].sum())
        s["hist_east_poles"] = float(poles[~w].sum())
        s["hist_east_others"] = float(people[~w].sum() - poles[~w].sum())
        out.append(s)
    return out


FIELDS = ["year", "poles", "people", "excluded", "west", "west_poles", "west_others", "east_poles", "east_others",
          "residual", "hist_west_poles", "hist_west_others", "hist_east_poles", "hist_east_others"]


def write_csv(lines: list[dict], path: str) -> str:
    """One row per year: counted persons on each side of the line ("west" is
    the Polish side), the persons not counted, and the line (polylines of
    lon,lat points separated by " | "). The ``hist_`` columns count the same
    people on either side of the historical Curzon line."""
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
