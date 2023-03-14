# Body záchrany v OSM
**Úvod**

Tento skript jsem vytvořil jako pomůcku při zadávání bodů záchrany na území ČR do [Openstreetmap](https://www.openstreetmap.org/#map=8/49.368/15.087).
Před lety jsem původně od Lesů ČR (jako zřizovatele bodů) obdržel kompletní seznam bodů záchrany po celé ČR.
Jelikož licence, kterou mi k tomu poskytli nesplňuje požadavky pro přímé zadání do OSM, rozhodl jsem se, že na to půjdu od lesa.
Tímto bych chtěl poděkovat uživateli [mahdi1234](https://www.openstreetmap.org/user/mahdi1234) s jeho projektem na [tříděný odpad](https://umap.openstreetmap.fr/en/map/odpad_bez_urceni_cr_553696#8/49.398/15.955), za inspiraci a cenné rady.

**Popis funkce**

V seznamu je obsaženo 2171 bodů ve formátu csv. Skrip po načtení seznamu začne generovat dotazy, které odesílá na službu [Overpass turbo](https://overpass-turbo.eu). V OSM existují dva způsoby značení bodů záchrany a to:
- [highway=emergency_access_point](highway=emergency_access_point)
- [emergency=access_point](https://wiki.openstreetmap.org/wiki/Cs:Tag:emergency%3Daccess_point)
 
Pro jeden bod se tedy odesílají dva dotazi. Jelikož délka jednoho dotazu je omezená jeden dotaz obsahuje maximálně 20 bodů. Dotaz je proveden tak, že server vrátí všechny body záchrany v okruhu 100 m od zadanné souřadnice. Seznam odeslaných doztazů se ukládád do souboru [comm_wr.txt](comm_wr.txt).
- Všechny nalezené body se ukládají do souboru [OSMBZ.csv](OSMBZ.csv).
- Nalezené body, které mají problém s hodnotou *REF* (např hodnota chybí nebo nodpovídá seznamu LČR) jsou uloženy do souboru [OSMbodychybejiciref.csv](OSMbodychybejiciref.csv)
- Body, které je potřeba do OSM doplnit se ukládají primárně do [OSMbodybezref.csv](OSMbodybezref.csv) bez hodnoty *REF*. Následně jsou pro lepší přenositelnot převedeny na formát [gpx](OSMbodybezref.gpx) a [geojson ](OSMbodybezref.geojson).
Script se spouští každých 24 hodin.

**Zdávání bodů záchrany**

V OSM existují dva způsoby zadávání bodů záchrany viz výše. V obou případech je potřeba vyplnit hodnotu *REF* viz příklad [zde](https://wiki.openstreetmap.org/wiki/Cs:Tag:highway%3Demergency_access_point). Hodnota *REF* by se měla vyplňovat bez mezer a prázdných znaků.
Pozor je třeba dávat u zadávání bodů v Osmadu, kde při zadávání *highway=emergency_access_point* je přednastavena pouze hodnota *NAME*.

**Visualizace**

Pro názornost jsou body, které chybí v OSM znázorněni na mapě [uMAP](https://umap.openstreetmap.fr/cs-cz/map/body-zachrany_554926#8/49.434/14.746) a to červenou barvou. Body, které již v OSM exitují jsou vykresleny světle modrou. Problémové body jsou tmavě modrou barvou.

**Statistika**

Script vytváří soubor statistika.csv, kam se ukládájí hodnoty: datum, celkový počet bodů v OSM a přírůstek. Do tohoto souboru je hodnota zapsána jen pokud se počet bodů v OSM zvýšil.  Hodnoty jsou také zpracovány pomocí [koláčového diagramu](https://github.com/RichMar/BZ/wiki), kde je stav BZ znázorněn v procentech a ve [sloupcovém grafu](https://github.com/RichMar/BZ/wiki/Prirustky-bodu-zachrany-do-OSM) kde jsou znázorněny přírústky v jednotlivých dnech.

