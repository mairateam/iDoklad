"""Generuje idoklad-hledanost.html (stejná šablona a vzhled jako report Flamaro).

Vstupy:  config.json, raw/{cz,sk}_{brand,vert}.csv (export historické hledanosti z Keyword Planneru),
         template.html (šablona stránky), node_modules/chart.js (vloží se do stránky, funguje offline)
Výstup:  docs/index.html, history/<CC>.json (archiv dat), history/kw_ids.json (stabilní ID slov)

Duplicity: slova se shodnou průměrnou hledaností, shodným dolním i horním CPC a shodnou měsíční
řadou jsou jedna skupina Plánovače; ponechá se jen první (pořadí v config.json), ostatní se odstraní.
"""
import csv, json, datetime, unicodedata
from pathlib import Path

ROOT = Path(__file__).parent          # tools/
REPO = ROOT.parent                     # kořen repa
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
HIST = REPO / "history"
HIST.mkdir(exist_ok=True)
ids_path = HIST / "kw_ids.json"
kw_ids = json.loads(ids_path.read_text(encoding="utf-8")) if ids_path.exists() else {}

GEO_LABEL = {"cz": "Česko a češtinu", "sk": "Slovensko a slovenštinu"}


def norm(s):
    return unicodedata.normalize("NFC", s.strip().lower())


def read_csv(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("keyword") or r["keyword"].startswith("#"):
                continue
            series = json.loads(r["monthly_search_volumes"]) if r.get("monthly_search_volumes") else []
            rows[norm(r["keyword"])] = {
                "kw": r["keyword"].strip(),
                "avg": int(r["avg_monthly_searches"] or 0),
                "low": int(r["low_top_of_page_bid_micros"] or 0),
                "high": int(r["high_top_of_page_bid_micros"] or 0),
                "series": {m: int(v or 0) for m, v in series},
            }
    return rows


def strip_d(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")


def kw_id(cc, kw):
    m = kw_ids.setdefault(cc, {})
    if kw not in m:
        m[kw] = max(m.values(), default=0) + 1
    return m[kw]


def brand_id(name):
    return "".join(ch for ch in norm(name) if ch.isalnum())


today = datetime.date.today().isoformat()
out = {"generated": today, "countries": {}}
report = []

for cc, c in cfg["countries"].items():
    rows = {}
    for part in ("brand", "vert"):
        p = REPO / "raw" / f"{cc}_{part}.csv"
        if p.exists():
            rows.update(read_csv(p))
    months = sorted({m for r in rows.values() for m in r["series"]})

    wanted = []  # (keyword, "brand"/"cat", group id) v pořadí z configu
    for b in c["brands"]:
        for k in b["keywords"]:
            wanted.append((k, "brand", brand_id(b["name"])))
    if c.get("vertical_kws"):  # pořadí = priorita při odstraňování duplicit
        for k, cat in c["vertical_kws"]:
            wanted.append((k, "cat", cat))
    else:
        for cat, kws in c["vertical"].items():
            for k in kws:
                wanted.append((k, "cat", cat))

    seen_sig, seen_kw = {}, set()
    kept, removed, missing = [], [], []
    for k, gtype, gid in wanted:
        nk = norm(k)
        if nk in seen_kw:
            continue
        seen_kw.add(nk)
        r = rows.get(nk)
        if r is None:
            missing.append(k)
            continue
        sig = (r["avg"], r["low"], r["high"], tuple(r["series"].get(m, 0) for m in months))
        if sig in seen_sig:
            removed.append({"kw": r["kw"], "dupOf": seen_sig[sig]})
            continue
        seen_sig[sig] = r["kw"]
        kept.append((gtype, gid, {
            "kw": r["kw"], "id": kw_id(cc, r["kw"]),
            "monthly": [r["series"].get(m, 0) for m in months],
            "avg": r["avg"], "grp": None, "same": None, "foreign": False,
            "cpc_low": round(r["low"] / 1e6, 2), "cpc_high": round(r["high"] / 1e6, 2),
        }))

    def by_avg(lst):
        return sorted(lst, key=lambda k: (-k["avg"], k["kw"]))

    cats = []
    vert_all = [k for t, g, k in kept if t == "cat"]
    cats.append({"id": "vertikala", "name": "Vertikála celkem", "keywords": by_avg(vert_all)})

    # Top 10 nejkonvertujících nebrandových KWs z Google Ads. Slova, která Plánovač vede jako jednu
    # řadu (blízké varianty), se sloučí do jedné položky a konverze se sečtou -> 10 různých řad, žádná duplicita.
    def stems(t):
        return tuple(sorted(w[:6] for w in strip_d(t).split()))

    def planner_row(k):
        r = rows.get(norm(k))
        if r is not None:
            return r
        cand = [x for x in rows.values() if sorted(strip_d(x["kw"]).split()) == sorted(strip_d(k).split())] or \
               [x for x in rows.values() if stems(x["kw"]) == stems(k)]
        return max(cand, key=lambda x: x["avg"]) if cand else None

    groups = {}  # signatura řady -> {"row", "conv", "members": [(kw, conv)]}
    for k, cv in c.get("top10_candidates", []):
        r = planner_row(k)
        if r is None:
            continue
        sig = (r["avg"], r["low"], r["high"], tuple(r["series"].get(m, 0) for m in months))
        gr = groups.setdefault(sig, {"row": r, "conv": 0.0, "members": []})
        gr["conv"] += cv
        gr["members"].append((k, cv))
    top = []
    for rank, gr in enumerate(sorted(groups.values(), key=lambda x: -x["conv"])[:10], 1):
        r = gr["row"]
        name = max(gr["members"], key=lambda x: x[1])[0]  # název = varianta s nejvíc konverzemi
        top.append({"kw": name, "id": kw_id(cc, name), "monthly": [r["series"].get(m, 0) for m in months],
                    "avg": r["avg"], "grp": None, "same": None, "foreign": False, "rank": rank,
                    "conversions": round(gr["conv"]), "variants": [m for m, _ in gr["members"] if m != name],
                    "cpc_low": round(r["low"] / 1e6, 2), "cpc_high": round(r["high"] / 1e6, 2)})
    if top:
        cats.append({"id": "top10", "name": "Top 10 konvertujících", "keywords": top})
    for cat in cfg["categories"]:
        cats.append({"id": cat["id"], "name": cat["name"],
                     "keywords": by_avg([k for t, g, k in kept if t == "cat" and g == cat["id"]])})
    brand_kws = [dict(k, brand=g) for t, g, k in kept if t == "brand"]
    cats.append({"id": "konkurence", "name": "Konkurence", "keywords": by_avg(brand_kws)})

    data = {
        "country": cc.upper(), "country_name": c["label"], "geo_label": GEO_LABEL.get(cc, c["label"]),
        "generated": today, "history_start": months[0], "months": months,
        "brands": [{"id": brand_id(b["name"]), "name": b["name"], "color": b["color"], "client": b.get("client", False)}
                   for b in c["brands"]],
        "removed": removed, "categories": cats,
    }
    out["countries"][cc] = data
    (HIST / f"{cc.upper()}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    report.append(f"{cc}: {len(kept)} slov, {len(removed)} duplicit odstraněno, {len(missing)} Plánovač nevrátil, "
                  f"měsíce {months[0]}..{months[-1]}" + (f" | nevráceno: {missing}" if missing else ""))

ids_path.write_text(json.dumps(kw_ids, ensure_ascii=False, indent=1), encoding="utf-8")

# Do zveřejněné stránky nejdou interní čísla z Google Ads (konverze), zůstávají jen v history/
public = json.loads(json.dumps(out))
for d in public["countries"].values():
    for cat in d["categories"]:
        for k in cat["keywords"]:
            k.pop("conversions", None)
            k.pop("variants", None)
data_json = json.dumps(public, ensure_ascii=False).replace("</", "<\\/")
chart_js = (ROOT / "node_modules/chart.js/dist/chart.umd.js").read_text(encoding="utf-8")
html = (ROOT / "template.html").read_text(encoding="utf-8")
cdn = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>'
assert cdn in html and "<<DATA>>" in html
html = html.replace(cdn, "<script>" + chart_js + "</script>").replace("<<DATA>>", data_json)
(REPO / "docs" / "index.html").write_text(html, encoding="utf-8")
print("\n".join(report))
