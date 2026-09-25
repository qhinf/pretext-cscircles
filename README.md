# CS Circles (Nederlands) in PreTeXt

De Nederlandse editie van [Computer Science Circles](https://cscircles.cemc.uwaterloo.ca/nl/) (CEMC,
University of Waterloo), omgezet naar [PreTeXt](https://pretextbook.org) voor gebruik op
[Runestone](https://runestone.academy). De website ging in 2026 offline; de lessen komen uit de
[Wayback Machine](https://web.archive.org/web/20260316180938/https://cscircles.cemc.uwaterloo.ca/nl/)
(snapshot van 16 maart 2026).

## Inhoud

* Alle lessen (0 t/m 18, inclusief 1E, 2X, 6D, 7A–7C, 11A–11C, 15A–15C) en de bijlagen
  Spiekbriefje, Python thuis, Bronnen en Dank.
* **Voorbeelden** zijn ActiveCode-programma's met de knop *Show CodeLens* (de Python-visualisatie,
  Online Python Tutor). De ingebedde Python Tutor-voorbeelden zijn CodeLens-programma's.
* **Programmeeroefeningen** hebben verborgen unittests (zie hieronder).
* **Volgorde-oefeningen** zijn Parsons-problemen, **meerkeuzevragen** en **korte-antwoordvragen**
  zijn PreTeXt-meerkeuze- en invuloefeningen.
* Afbeeldingen komen uit [cemc/cscircles-wp-content](https://github.com/cemc/cscircles-wp-content)
  (de Nederlandse versies waar die bestaan).

## Bouwen

```
pip install -r requirements.txt
pretext build web         # statische HTML in output/web
pretext build runestone   # voor een Runestone-server
pretext view web
```

Voor de CodeLens-programma's heeft `pretext build` toegang nodig tot de tracer-server van Runestone
(`http://tracer.runestone.academy:5000`).

## Opbouw van de repository

| Pad | Inhoud |
| --- | --- |
| `source/les-*.ptx`, `source/bijlage-*.ptx`, `source/main.ptx` | **gegenereerd** door `tools/convert.py` |
| `source/docinfo.ptx`, `source/frontmatter.ptx` | met de hand geschreven |
| `archief/` | de gearchiveerde HTML-pagina's (bron van de omzetting) |
| `assets/images/` | afbeeldingen |
| `tools/convert.py` | omzetting HTML → PreTeXt |
| `tools/lessen.py` | lijst van pagina's, id's en titels |
| `tools/toetsen/` | referentie-oplossingen en testgevallen per oefening |
| `tools/harnas.py` | maakt de verborgen tests uit `tools/toetsen/` |
| `tools/check_toetsen.py` | controleert alle tests in Runestones Skulpt (via node) |
| `tools/validate.py` | controleert de PreTeXt tegen het schema |
| `tools/fetch_archive.py` | haalt de pagina's opnieuw op uit de Wayback Machine |

Wijzigingen in de lessen maak je dus in `tools/` (of in `archief/`) en daarna:

```
python3 tools/convert.py
python3 tools/validate.py          # pip install jingtrang
SKULPT_DIR=... python3 tools/check_toetsen.py
```

## De tests van de programmeeroefeningen

CS Circles controleerde programma's op de server, met invoer en voorgedefinieerde variabelen die
per test verschilden. De oorspronkelijke tests en modeloplossingen waren niet openbaar, dus die zijn
voor deze versie opnieuw geschreven (`tools/toetsen/`).

Runestone voert Python in de browser uit (Skulpt). Na **Run** voert Runestone eerst het programma
van de leerling uit (met gewone `input()`), en daarna de verborgen tests. Die halen de code van de
leerling op met `getEditorText()` en voeren haar voor elk testgeval opnieuw uit met `exec()`, met
een eigen `print` (om de uitvoer op te vangen) en `input` (die de invoer van het testgeval
teruggeeft). De uitvoer en eventuele returnwaarden worden vergeleken met die van de
referentie-oplossing. Zo is er geen verborgen code vóór het programma nodig, en toont CodeLens alleen
de code van de leerling. Alleen oefeningen waarbij "het nakijkprogramma variabelen voor je
definieert" hebben een verborgen voorcode met die variabelen.

`tools/check_toetsen.py` controleert voor elke oefening dat de referentie-oplossing (en eventuele
alternatieve goede oplossingen) alle tests haalt, en dat de startcode en een aantal foute
oplossingen worden afgekeurd.

## Bekende verschillen met CS Circles

* De tekst verwijst soms naar knoppen van de oude website (*Uitvoeren*, *Visualiseren*, de
  console, inloggen); het voorwoord legt uit hoe dat in deze versie werkt.
* Volgorde-oefeningen waarbij meerdere volgordes goed zijn (bv. de inspring-oefeningen in les 6)
  accepteren nu één (of een beperkt aantal) volgorde(s).
* In de oefening *Priem klaar voor takeoff* (les 18) is de tijdslimiet 60 seconden: Python in de
  browser is veel trager dan op de server van CS Circles.
* In *Digital Sum* (les 16) is de inspringing van de startcode hersteld.

## Licentie

Deze versie valt onder [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
(zie [LICENSE.md](LICENSE.md)). Het is een bewerking van Computer Science Circles
© 2010–2026 Centre for Education in Mathematics and Computing, University of Waterloo:

* de lesinhoud van CS Circles is uitgegeven onder
  [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/)
  (volgens de [pagina voor auteurs](https://web.archive.org/web/20260208095951/https://cscircles.cemc.uwaterloo.ca/authoring/));
* het materiaal van het CEMC valt onder
  [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
  (volgens [cemc.uwaterloo.ca/copyright.html](http://cemc.uwaterloo.ca/copyright.html), waar het
  CC-logo onderaan elke pagina van CS Circles naar verwees).

CC BY-NC-SA 3.0 staat bewerkingen toe onder een latere versie van dezelfde licentie, en CC BY-NC 4.0
staat bewerkingen onder elke licentie toe; CC BY-NC-SA 4.0 is dus met beide verenigbaar.
