"""The 1921 nationality census, for the identity layer (``plsim.identity``).

The census of 30 September 1921 asked nationality (narodowość) and religion,
not language. It did not cover the Wilno land (then Central Lithuania) or
Upper Silesia (not yet Polish). Poland's totals (27.18 M; the shares of the
answers): Polish 69.23 %, Ukrainian and Ruthenian 15.17, Jewish 7.97,
Belarusian 4.03, German 2.99, Russian 0.19, "tutejszy" 0.15, Czech 0.12,
Lithuanian 0.09. Of the Jews by religion about three quarters gave Jewish
nationality.

Voivodeships (grade A: confirmed in two sources; grade C: recalled from the
census tables, used as a check only):

* Wołyń (A): Ukrainian and Ruthenian 68.4 %, Polish 16.6.
* Stanisławów (A): Ukrainian and Ruthenian 70.2 %, Polish 21.8, Jewish 6.8,
  German 1.1.
* Tarnopol (A): Polish 49.3 %, Ukrainian and Ruthenian 45.5.
* Polesie (A): Belarusian 42.6 % (375 thousand), Ruthenian 17.7 (156
  thousand), Jewish 10.5, "tutejszy" 4.4, Polish 24.3.
* Lwów (A): Polish 56.58 %, Ruthenian 35.88, Jewish 7.00, German 0.46
  (2,718,014 persons; Table XI of the census volume, Statystyka Polski
  t. XIII, nationality by religion). Of the Greek Catholics 13.9 % gave
  Polish nationality, 86.1 % Ruthenian; of the Jews by religion 38.9 %
  Polish, 60.8 % Jewish.
* Nowogródek (C): Polish about 52 %, Belarusian 39, Jewish 7.6.
* Białystok (C): Polish about 77 %, Belarusian 10, Jewish 11.

County tables. The "Skorowidz miejscowości" volumes give nationality by
locality, with a summary by powiat; the voivodeship volumes of the census
("mieszkania, ludność, stosunki zawodowe") give it for the voivodeship only
(Lwów, Table XI, above). ``census1921_powiaty.csv`` holds the powiaty of the
Łódź voivodeship from the summary of the Skorowidz, t. II (1925; the Łódź
county is the city and the powiat together; every row adds up to its total;
the 430 "Ruthenians" of Kalisz were the Ukrainian army interned there). The
table at
``plsim/data/census1921_powiaty.csv`` with the columns ``code`` (a county
code of ``data.counties``, e.g. ``WOL.luck``), ``total``, ``pl``, ``uk``
(Ukrainian and Ruthenian), ``be``, ``tut``, ``jw``, ``de``, ``ru``, ``lt``,
``cs``, ``other`` (persons) is read by ``county_table`` and checked by
``plsim.validate.identity_1921`` county by county.
"""
from __future__ import annotations

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# shares (%) of the nationality answers; grade
NATIONAL = {"pl": 69.23, "uk": 15.17, "jw": 7.97, "be": 4.03, "de": 2.99, "ru": 0.19, "tut": 0.15, "cs": 0.12,
            "lt": 0.09}
VOIVODESHIPS = {
    "WOL": ({"uk": 68.4, "pl": 16.6}, "A"),
    "STA": ({"uk": 70.2, "pl": 21.8, "jw": 6.8, "de": 1.1}, "A"),
    "TAR": ({"pl": 49.3, "uk": 45.5}, "A"),
    "POL": ({"be": 42.6, "uk": 17.7, "jw": 10.5, "tut": 4.4, "pl": 24.3}, "A"),
    "LWO": ({"pl": 56.58, "uk": 35.88, "jw": 7.00, "de": 0.46}, "A"),
    "NOW": ({"pl": 52.0, "be": 39.0, "jw": 7.6}, "C"),
    "BIA": ({"pl": 77.0, "be": 10.0, "jw": 11.0}, "C"),
}
# regions the census did not cover
NOT_COVERED = ("WIL", "SLA")
CATEGORIES = ["pl", "uk", "be", "tut", "jw", "de", "ru", "lt", "cs", "other"]


def county_table(path: str | None = None) -> dict:
    """County nationality counts {code: {category: persons}} from the CSV
    described in the module docstring, or {} if there is none."""
    path = path or os.path.join(HERE, "census1921_powiaty.csv")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["code"]] = {k: float(row.get(k) or 0) for k in ["total"] + CATEGORIES}
    return out
