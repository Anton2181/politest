"""Read the 1931 census short results by powiat (GUS, "Drugi Powszechny Spis
Ludności z dn. 9 XII 1931 r. ... w postaci skróconej", MBC edition 14481)
into ``plsim/data/census1931_powiaty.csv``.

Each powiat (and city with county rights) has a page "Ludność według płci,
wyznania, języka ojczystego oraz umiejętności czytania i pisania" with rows
for towns and villages. The text layer is the library's OCR: the column set
changes from page to page and thousands are split by spaces, so the digit
groups of a row are joined by search, under the census's own identities:
total = sum of the religions = sum of the languages. Usage:

    python tools/parse_census1931.py 14481.txt [out.csv]

where 14481.txt is ``pdftotext -layout`` of the volume.
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata

VOIV = {"WARSZAWSKIE": "WAR", "ŁÓDZKIE": "LOD", "KIELECKIE": "KIE", "LUBELSKIE": "LUB", "BIAŁOSTOCKIE": "BIA",
        "WILEŃSKIE": "WIL", "NOWOGRÓDZKIE": "NOW", "POLESKIE": "POL", "WOŁYŃSKIE": "WOL", "POZNAŃSKIE": "POZ",
        "POMORSKIE": "POM", "ŚLĄSKIE": "SLA", "KRAKOWSKIE": "KRA", "LWOWSKIE": "LWO", "STANISŁAWOWSKIE": "STA",
        "TARNOPOLSKIE": "TAR"}
# GUS numbering of the voivodeships (the Roman numeral in each page's corner)
ROMAN = {"I": "WAW", "II": "WAR", "III": "LOD", "IV": "KIE", "V": "LUB", "VI": "BIA", "VII": "WIL", "VIII": "NOW",
         "IX": "POL", "X": "WOL", "XI": "POZ", "XII": "POM", "XIII": "SLA", "XIV": "KRA", "XV": "LWO", "XVI": "STA",
         "XVII": "TAR"}

# canonical column order of the tables; a page prints a subset, in this order
RELIGIONS = [("rc", ("rzym", "rzvm", "tolic")), ("gc", ("grecko", "greko", "grec")), ("or", ("prawo", "slaw", "sław")),
             ("ev", ("ewan", "gelic", "gelick")), ("jw", ("mojz", "mojs", "mojie", "szowe", "zeszo")),
             ("xc", ("chrzes", "cijan", "chrze")), ("ro", ("inne",)), ("rn", ("wiado",))]
LANGUAGES = [("pl", ("polski", "pol")), ("uk", ("ukrain", "ukra")), ("rue", ("ruski",)), ("be", ("bialo", "biało")),
             ("ru", ("rosyj", "rosvj")), ("de", ("niemiec", "miecki", "miec")), ("lt", ("litew",)),
             ("yi", ("zydow", "hebraj", "brajsk", "z he")), ("pls", ("tutej",)), ("cs", ("czesk",)),
             ("oth", ("inny", "lnny")), ("unk", ("wiado",))]
REL_ORDER = [c for c, _ in RELIGIONS]
LANG_ORDER = [c for c, _ in LANGUAGES]


def fold(s: str) -> str:
    s = s.replace("ł", "l").replace("Ł", "L")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


NUMFIX = str.maketrans({"I": "1", "l": "1", "i": "1", "|": "1", "O": "0", "o": "0", "Z": "2", "z": "2", "S": "5",
                        "B": "8", "Ó": "6", "ó": "6", "J": "1", "T": "7"})


def tokens(line: str) -> list[str]:
    """Digit groups of a data row, label removed. A group touching a letter
    is OCR noise for a digit (``i 475`` = 1 475)."""
    body = re.sub(r"^[^0-9]*?(\.{2,}|[.•■ ]{4,}|\s{2,})", "", line, count=1)
    out = []
    for raw in re.split(r"[\s,;:!|\]\[)(’'\"“”`^*]+", body):
        raw = raw.strip(".-—_°•■")
        if not raw:
            continue
        fixed = raw.translate(NUMFIX)
        if fixed.isdigit():
            out.append(fixed)
    return out


def split_any(tok: list[str], kmax: int = 8, mmax: int = 12, tol: float = 0.005):
    """Best readings of ``tok`` for any column counts: {(k, m): (values, residual)}."""
    out = {}
    for k in range(1, kmax + 1):
        for m in range(1, mmax + 1):
            best = split_numbers(tok, k, m, tol)
            if best:
                out[(k, m)] = best
    return out


def split_numbers(tok: list[str], k: int, m: int, tol: float = 0.005):
    """The reading of ``tok`` as total, k religions and m languages (then
    anything) that best satisfies total = sum(religions) = sum(languages).
    The printed tables themselves are off by a few persons at times, so a
    relative residual up to ``tol`` is accepted. Returns (values, residual)
    or None."""
    best = [None, tol + 1e-12]

    def numbers_from(i):
        if i >= len(tok):
            return
        v = tok[i]
        yield int(v), i + 1
        if len(v) <= 3:
            j = i + 1
            while j < len(tok) and len(tok[j]) == 3:
                v += tok[j]
                j += 1
                yield int(v), j

    def rec(i, vals):
        n = len(vals)
        t = vals[0]
        if n == 1 + k + m:
            r = max(abs(sum(vals[1:1 + k]) - t), abs(sum(vals[1 + k:]) - t)) / max(t, 1)
            if r < best[1]:
                best[0], best[1] = list(vals), r
            return
        if n == 1 + k:
            if abs(sum(vals[1:]) - t) / max(t, 1) > tol:
                return
        for v, j in numbers_from(i):
            part = sum(vals[1:]) + v if n <= k else sum(vals[1 + k:]) + v
            if part > t * (1 + tol):
                break
            rec(j, vals + [v])

    for v, j in numbers_from(0):
        if v >= 10:
            rec(j, [v])
    return (best[0], best[1]) if best[0] else None


def columns(header: str):
    h = re.sub(r"wieku\s*n\S*", " ", re.sub(r"\s+", " ", fold(header)))
    h = re.sub(r"nie\s*umia\S*", " ", h)
    rel = [c for c, keys in RELIGIONS if any(k in h for k in keys)]
    lang = [c for c, keys in LANGUAGES if any(k in h for k in keys)]
    if "be" in lang and "rue" in lang and h.count("ruski") <= h.count("bialo"):
        lang.remove("rue")                                   # "biało- ruski"
    return rel, lang


def fit_columns(toks, det_rel, det_lang, tpl_rel, tpl_lang):
    """Column sets near the header's (and the voivodeship's usual set) that
    let the row satisfy the identities. Returns (rel, lang, values, residual)
    or None; ties go to the set closest to the header."""
    import itertools
    always_rel, always_lang = {"rc"}, {"pl"}
    pool_rel = [c for c in REL_ORDER if c in set(det_rel) | set(tpl_rel) | always_rel]
    pool_lang = [c for c in LANG_ORDER if c in set(det_lang) | set(tpl_lang) | always_lang]
    opt_rel = [c for c in pool_rel if c not in always_rel]
    opt_lang = [c for c in pool_lang if c not in always_lang]
    cache, best = {}, None
    for nr in range(len(opt_rel) + 1):
        for sr in itertools.combinations(opt_rel, nr):
            rel = [c for c in REL_ORDER if c in always_rel or c in sr]
            d_r = len(set(rel) ^ set(det_rel)) + 0.5 * len(set(rel) ^ set(tpl_rel))
            for nl in range(len(opt_lang) + 1):
                for sl in itertools.combinations(opt_lang, nl):
                    lang = [c for c in LANG_ORDER if c in always_lang or c in sl]
                    d = d_r + len(set(lang) ^ set(det_lang)) + 0.5 * len(set(lang) ^ set(tpl_lang))
                    if best is not None and d > best[0]:
                        continue
                    km = (len(rel), len(lang))
                    if km not in cache:
                        cache[km] = split_numbers(toks, *km)
                    v = cache[km]
                    if v and (best is None or (d, v[1]) < (best[0], best[4])):
                        best = (d, rel, lang, v[0], v[1])
    return None if best is None else best[1:]


ROW = re.compile(r"^\W{0,3}(miasta i wie|miasta|miast|wie[sś]|ogo[lł]em|og[oó]lem)", re.I)


def parse_page(page: str):
    lines = page.splitlines()
    top = " ".join(lines[:8])
    unit = None
    m = re.search(r"\b(POWIAT|MIASTO|M\.\s*ST\.)\s+([A-ZĄĆĘŁŃÓŚŹŻ][A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-. ]+?)\s{2,}", top)
    if m:
        unit = (m.group(1).replace(".", "").replace(" ", "").upper(), m.group(2).strip())
    code = re.search(r"\b(X{0,1}V?I{0,3}|IV|IX|XIV|XIX)\s+(\d{1,2}[ab]?|\d{1,2}\s?[ab])\s*$", lines[0] if lines else "")
    roman = None
    for l in lines[:6]:
        mm = re.search(r"\b([XVI]{1,5})\s+(\d{1,2}\s?[a-z]?)\s*$", l.strip())
        if mm and mm.group(1) in ROMAN:
            roman = (mm.group(1), mm.group(2).replace(" ", ""))
            break
    tot = re.search(r"Ludno\S*\s+og\S*\s+([\d ]{3,12}),", " ".join(lines[:14]))
    total = int(tot.group(1).replace(" ", "")) if tot else None
    k0 = next((j for j, l in enumerate(lines) if re.search(r"j.zyka\s+ojczyst", l)), None)
    if k0 is None:
        return None
    rows, hdr = {}, []
    j = k0 + 1
    while j < len(lines) and not (ROW.search(fold(lines[j].strip())) and len(tokens(lines[j])) >= 4):
        hdr.append(lines[j])
        j += 1
    rel, lang = columns(" ".join(hdr))
    while j < len(lines) and "wieku" not in fold(lines[j]) and len(rows) < 6:
        l = lines[j].strip()
        mm = ROW.search(fold(l))
        if mm and len(tokens(l)) >= 4:
            key = mm.group(1)
            key = "all" if key.startswith("miasta i") or key.startswith("og") else ("town" if key.startswith("mias") else "rural")
            if key not in rows:
                rows[key] = tokens(l)
        j += 1
    return {"unit": unit, "roman": roman, "total": total, "rel": rel, "lang": lang, "rows": rows}


def is_table(page: str) -> bool:
    f = fold(page[:5000])
    return ("umia" in f and ("wyzna" in f or "rzym" in f or "ojczyst" in f)) or bool(re.search(r"j.zyka\s+ojczyst", page[:4000]))


def unit_name(page: str, nxt: str = ""):
    """(kind, name) from the page heading or the continuation page's "(dok.)" heading."""
    for q in (page, nxt):
        top = " ".join(x.strip() for x in q.splitlines()[:6])
        m = re.search(r"(POWIAT|MIASTO|Powiat|Miasto|M\. ST\.)\s+(.{2,60}?)(\s{2,}|\(do|$)", top)
        if m:
            return m.group(1).upper().replace(" ", ""), m.group(2).strip()
    return None


def ocr_rows(pdf: str, page_no: int, workdir: str) -> dict:
    """Re-read a table page with tesseract (2x upscaled), keeping the column
    rules as separators. Returns {row: tokens}."""
    import os
    import subprocess
    from PIL import Image
    base = os.path.join(workdir, f"p{page_no + 1}")
    if not os.path.exists(base + ".png"):
        subprocess.run(["pdftoppm", "-f", str(page_no + 1), "-l", str(page_no + 1), "-r", "150", "-gray", "-png",
                        "-singlefile", pdf, base], check=True, capture_output=True)
        im = Image.open(base + ".png")
        im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
        im.save(base + ".png")
    txt = subprocess.run(["tesseract", base + ".png", "-", "--psm", "6", "-l", "pol"], capture_output=True,
                         text=True).stdout
    rows = {}
    for l in txt.splitlines():
        mm = ROW.search(fold(l.strip()))
        if mm and len(tokens(l)) >= 4:
            key = mm.group(1)
            key = "all" if key.startswith("miasta i") or key.startswith("og") else ("town" if key.startswith("mias") else "rural")
            rows.setdefault(key, tokens(l))
    return rows


def main(path, out=None, pdf=None, workdir="/tmp"):
    pages = open(path, encoding="utf-8").read().split("\f")
    recs = []
    for i, p in enumerate(pages):
        if not is_table(p):
            continue
        r = parse_page(p) or {"rows": {}, "rel": [], "lang": [], "total": None, "roman": None}
        r["page"] = i
        r["name"] = unit_name(p, pages[i + 1] if i + 1 < len(pages) else "")
        k, m = len(r["rel"]), len(r["lang"])
        res = {key: split_numbers(tok, k, m) for key, tok in r["rows"].items()}
        r["src"] = {key: "text" for key, v in res.items() if v}
        if pdf and (not res or not all(res.values()) or not r["rows"]):
            alt = ocr_rows(pdf, i, workdir)
            for key, tok in alt.items():
                if not res.get(key):
                    v = split_numbers(tok, k, m)
                    if v:
                        res[key] = v
                        r["src"][key] = "tesseract"
                    elif key not in r["rows"]:
                        r["rows"][key] = tok
        r["sol"] = res
        recs.append(r)
    return recs


if __name__ == "__main__":
    recs = main(*sys.argv[1:2])
    for r in recs[:5]:
        print(r)


# ------------------------------------------------------------------ to counties
# first page of each voivodeship's section in the MBC edition (0-based)
SECTIONS = [(11, "WAW"), (35, "WAR"), (97, "LOD"), (174, "KIE"), (230, "LUB"), (282, "BIA"), (319, "WIL"),
            (359, "NOW"), (381, "POL"), (408, "WOL"), (443, "POZ"), (524, "POM"), (569, "SLA"), (602, "KRA"),
            (662, "LWO"), (745, "STA"), (779, "TAR")]
# towns with county rights (or towns tabulated apart) that are not county seats
CITY_COUNTY = {"tomaszow": "LOD.brzeziny", "pabianice": "LOD.lask", "zgierz": "LOD.lodz", "zdunsk": "LOD.sieradz",
               "zyrardow": "WAR.grodziskmazowi", "pruszkow": "WAR.warszawa", "ostrowiec": "KIE.opatow",
               "sosnowiec": "KIE.bedzin", "czeladz": "KIE.bedzin", "boryslaw": "LWO.drohobycz",
               "myslowice": "SLA.katowice", "chorzow": "SLA.swietochlowice", "krolewsk": "SLA.swietochlowice",
               "gdynia": "POM.wejherowo", "morski": "POM.wejherowo", "baranowicze": "NOW.baranowicze",
               "wilno": "WIL.wilno", "grudziadz": "POM.grudziadz", "torun": "POM.torun", "stryj": "STA.stryj"}


def section_of(page: int) -> str | None:
    cur = None
    for start, code in SECTIONS:
        if page >= start:
            cur = code
    return cur


def county_of(rec, counties) -> str | None:
    """Match a page to a county of its voivodeship: town table first, then the
    closest folded name (seat or adjectival name; the OCR garbles a few)."""
    import difflib
    par = section_of(rec["page"])
    if par is None or rec["name"] is None:
        return None
    kind, name = rec["name"]
    nm = fold(re.split(r"\s+b\S*\s+m", name)[0])            # drop "bez miasta ..."
    nm = re.sub(r"[^a-z]", "", nm.translate(str.maketrans("1503", "isoe")))
    for key, code in CITY_COUNTY.items():
        if nm.startswith(key) and code.split(".")[0] == par:
            return code
    best, score = None, 0.0
    for c in counties:
        if c.parent != par:
            continue
        for cand in (fold(c.seat), fold(c.name)):
            cand = re.sub(r"[^a-z]", "", cand)
            r = max(difflib.SequenceMatcher(None, nm[:len(cand) + 2], cand).ratio(),
                    difflib.SequenceMatcher(None, nm, cand[:len(nm) + 2]).ratio())
            if r > score:
                best, score = c.code, r
    return best if score >= 0.6 else None


def tess_rows(path: str) -> dict:
    """Rows of a cached tesseract page (see ``ocr_rows``)."""
    rows = {}
    try:
        txt = open(path, encoding="utf-8").read()
    except OSError:
        return rows
    for l in txt.splitlines():
        mm = ROW.search(fold(l.strip()))
        if mm and len(tokens(l)) >= 4:
            key = mm.group(1)
            key = "all" if key.startswith("miasta i") or key.startswith("og") else ("town" if key.startswith("mias") else "rural")
            rows.setdefault(key, tokens(l))
    return rows


def header_of(text: str) -> str:
    lines = text.splitlines()
    k0 = next((j for j, l in enumerate(lines) if re.search(r"j.zyk|wyzna|Wyzna", l)), None)
    if k0 is None:
        return ""
    out = []
    for l in lines[k0:k0 + 16]:
        if ROW.search(fold(l.strip())) and len(tokens(l)) >= 4:
            break
        out.append(l)
    return " ".join(out)


def extract(txt_path: str, ocr_dir: str, skip=("WAW",)) -> list[dict]:
    """Every table page: unit name, header total, and the fitted rows."""
    import collections
    import os
    pages = open(txt_path, encoding="utf-8").read().split("\f")
    tab = [i for i, p in enumerate(pages) if is_table(p) and section_of(i) not in skip]
    info = {}
    for i in tab:
        tess = open(f"{ocr_dir}/p{i + 1}.txt", encoding="utf-8").read() if os.path.exists(f"{ocr_dir}/p{i + 1}.txt") else ""
        r1, l1 = columns(header_of(pages[i]))
        r2, l2 = columns(header_of(tess))
        info[i] = {"det_rel": sorted(set(r1) | set(r2), key=REL_ORDER.index),
                   "det_lang": sorted(set(l1) | set(l2), key=LANG_ORDER.index),
                   "text": (parse_page(pages[i]) or {"rows": {}})["rows"], "tess": tess_rows(f"{ocr_dir}/p{i + 1}.txt")}
    tpl = {}
    for sec in {section_of(i) for i in tab}:
        ii = [i for i in tab if section_of(i) == sec]
        cr = collections.Counter(c for i in ii for c in info[i]["det_rel"])
        cl = collections.Counter(c for i in ii for c in info[i]["det_lang"])
        tpl[sec] = ([c for c in REL_ORDER if cr[c] >= 0.3 * len(ii)], [c for c in LANG_ORDER if cl[c] >= 0.3 * len(ii)])
    recs = []
    for i in tab:
        d = info[i]
        tr, tl = tpl[section_of(i)]
        rows = {}
        for key in ("town", "rural", "all"):
            cands = []
            for src in ("text", "tess"):
                toks = d[src].get(key)
                if toks:
                    f = fit_columns(toks, d["det_rel"], d["det_lang"], tr, tl)
                    if f:
                        cands.append((f, src))
            if cands:
                cands.sort(key=lambda c: (len(set(c[0][0]) ^ set(d["det_rel"])) + len(set(c[0][1]) ^ set(d["det_lang"])), c[0][3]))
                (rel, lang, vals, res), src = cands[0]
                agree = len(cands) == 2 and cands[0][0][2] == cands[1][0][2]
                rows[key] = {"rel": rel, "lang": lang, "vals": vals, "res": res, "src": "both" if agree else src}
            elif d["text"].get(key) or d["tess"].get(key):
                rows[key] = {"vals": None, "text": d["text"].get(key), "tess": d["tess"].get(key)}
        m = re.search(r"Ludno\S*\s+og\S*\s+([\d ]{3,12}),", pages[i][:2500])
        recs.append({"page": i, "section": section_of(i), "name": unit_name(pages[i], pages[i + 1] if i + 1 < len(pages) else ""),
                     "total": int(m.group(1).replace(" ", "")) if m else None, "rows": rows,
                     "det": (d["det_rel"], d["det_lang"])})
    return recs


def page_values(rec) -> dict | None:
    """Town + rural (or the 'all' row) of a page as {column: persons}, with
    'pop'; None unless every row present was read."""
    rows = rec["rows"]
    keys = ["all"] if "all" in rows and rows["all"].get("vals") and not ("town" in rows or "rural" in rows) else \
        [k for k in ("town", "rural") if k in rows]
    if not keys or any(not rows[k].get("vals") for k in keys):
        return None
    out = {"pop": 0, "urban": 0}
    for k in keys:
        r = rows[k]
        v = r["vals"]
        out["pop"] += v[0]
        if k == "town":
            out["urban"] += v[0]
        for c, x in zip(r["rel"], v[1:1 + len(r["rel"])]):
            out["r_" + c] = out.get("r_" + c, 0) + x
        for c, x in zip(r["lang"], v[1 + len(r["rel"]):]):
            out["l_" + c] = out.get("l_" + c, 0) + x
    return out


def by_county(recs, counties, manual=None):
    """{county: {"pages": [...], "values": summed values or None}}. City
    districts are dropped: of several town pages of the same name, only the
    one with the largest population (the whole city) is kept."""
    import collections
    manual = manual or {}
    groups = collections.defaultdict(list)
    for r in recs:
        c = manual.get(r["page"], county_of(r, counties))
        if c:
            groups[c].append(r)
    out = {}
    for c, rs in groups.items():
        keep, seen = [], {}
        for r in rs:
            nm = fold(r["name"][1])[:6] if r["name"] else str(r["page"])
            town = r["name"] and r["name"][0] == "MIASTO"
            if town:
                if nm in seen:
                    j = seen[nm]
                    if (r["total"] or 0) > (keep[j]["total"] or 0):
                        keep[j] = r
                    continue
                seen[nm] = len(keep)
            keep.append(r)
        vals = [page_values(r) for r in keep]
        tot = None
        if all(v is not None for v in vals):
            tot = collections.Counter()
            for v in vals:
                tot.update(v)
        out[c] = {"pages": [r["page"] for r in keep], "values": dict(tot) if tot else None,
                  "header": sum(r["total"] or 0 for r in keep)}
    return out
