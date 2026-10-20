# iDoklad: hledanost vertikály a konkurence

Klientský report hledanosti (Google Ads Keyword Planner) pro iDoklad, Česko a Slovensko.

- Stránka: https://mairateam.github.io/iDoklad/
- Přepínač v liště nahoře = země (Česko, Slovensko).
- Záložky = kategorie: Vertikála celkem, Top 10 konvertujících, Online fakturace a programy,
  Vystavení faktury, Vzory a typy faktur, Konkurence (share of search, index, korelace).
- Filtr klíčových slov se ukládá do adresy, odkaz jde sdílet.

## Struktura
- `docs/index.html` – zveřejněná stránka (generovaná, data i knihovna grafů uvnitř; ručně se neupravuje).
  GitHub Pages publikuje jen složku `docs/`.
- `tools/` – generátor (`build_data.py`), šablona (`template.html`), seznam slov a značek (`config.json`),
  postup měsíční aktualizace (`UPDATE.md`).
- `raw/` – poslední stažená data z Plánovače, `history/` – archiv zpracovaných dat a stabilní ID slov.

## Aktualizace
Jednou měsíčně (15. den) naplánovaná úloha stáhne nová data z Keyword Planneru, přegeneruje
stránku a pushne ji sem; GitHub Pages ji zveřejní během minuty. Postup je v `tools/UPDATE.md`.
