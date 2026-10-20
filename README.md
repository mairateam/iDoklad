# iDoklad: hledanost vertikály a konkurence

Klientský report hledanosti (Google Ads Keyword Planner) pro iDoklad, Česko a Slovensko.

- Stránka: https://mairateam.github.io/iDoklad/
- Přepínač v liště nahoře = země (Česko, Slovensko).
- Záložky = kategorie: Vertikála celkem, Top 10 konvertujících, Online fakturace a programy,
  Vystavení faktury, Vzory a typy faktur, Konkurence.
- Konkurence: přepínač značek, měsíční hledanost po značkách, share of search po měsících,
  indexovaný graf vertikála vs. značky a korelace značek s vertikálou.
- Filtr klíčových slov: vyhledávání a zaškrtávání, grafy a tabulky se přepočítají
  jen z vybraných slov. Vybraný pohled je v adrese, odkaz jde sdílet.
- Data: měsíční hledanost z Google Keyword Planneru (CZ: Česko + čeština, SK: Slovensko + slovenština).
  Duplicitní varianty (stejná měsíční řada, hledanost i CPC) jsou odstraněné.
  Období a datum poslední aktualizace jsou uvedené přímo ve stránce.

Soubor `index.html` je generovaný (data i knihovna grafů jsou vložené uvnitř), ručně se neupravuje.
Složka `history/` je archiv měsíčních dat (záloha, stránka ho nečte).
Aktualizace = nové stažení dat z Keyword Planneru, přegenerování stránky a push
do tohoto repa; GitHub Pages ji zveřejní během minuty.
