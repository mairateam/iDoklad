# Měsíční aktualizace dat (postup pro naplánovanou úlohu)

Cíl: doplnit do reportu nový měsíc z Google Keyword Planneru a zveřejnit ho.
Seznam klíčových slov, kategorie, značky a Top 10 se NEMĚNÍ, bere se z `tools/config.json`.

## 1. Stažení dat z Plánovače
Pro každou zemi (`cz`, `sk`) v `tools/config.json` udělej 2 volání nástroje
`mcp__Databy_MCP__google_ads__get_keyword_historical_metrics` s parametry:
- `_google_account`: `"company"`
- `customer_id`: `countries.<cc>.customer_id`
- `language_id`: `countries.<cc>.language`, `geo_target_ids`: `[countries.<cc>.geo]`
- `limit`: 1000, bez `start_year_month` / `end_year_month` (celá historie ~48 měsíců)

Volání:
1. **značky** – `keywords` = všechna slova ze `countries.<cc>.brands[].keywords` → ulož do `raw/<cc>_brand.csv`
2. **vertikála** – `keywords` = první prvky ze `countries.<cc>.vertical_kws` (`[kw, kategorie]`) → ulož do `raw/<cc>_vert.csv`

Výsledek je velký, nástroj vrátí odkaz `https://ai.databy.io/api/results/...` (platí 10 minut).
Stáhni ho hned: `curl -sS -o raw/<cc>_brand.csv "<odkaz>"`. Soubor musí začínat hlavičkou
`keyword,avg_monthly_searches,...` a mít zhruba stejný počet řádků jako předchozí verze (`git diff --stat`).

## 2. Kontrola
- Poslední měsíc v datech (sloupec `monthly_search_volumes`) má být předchozí kalendářní měsíc.
- Pokud Plánovač nový měsíc ještě nemá (poslední měsíc je stejný jako v `history/CZ.json` → `months`),
  nic necommituj a skonči se zprávou „Plánovač zatím nemá data za <měsíc>“.

## 3. Sestavení stránky
```bash
cd tools
NO_PROXY=localhost no_proxy=localhost npm install --silent --noproxy=localhost
python3 build_data.py      # zapíše docs/index.html a history/*.json
```
Zkontroluj výpis (počet slov a duplicit by měl být podobný jako minule, žádná chyba).

## 4. Zveřejnění
```bash
git add docs history raw tools/config.json
git commit -m "Aktualizace dat: přidán měsíc YYYY-MM (běh YYYY-MM-DD)"
git push origin main
```
GitHub Pages (zdroj: větev `main`, složka `/docs`) stránku zveřejní do minuty:
https://mairateam.github.io/iDoklad/
