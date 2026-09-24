"""Maakt de verborgen unittests (<tests>) voor de programmeeroefeningen.

Runestone voert na de code van de leerling de verborgen tests uit (in Skulpt, in de browser).
De tests halen de code van de leerling op met getEditorText() en voeren die opnieuw uit met
exec(), met een eigen print() die de uitvoer opvangt en een eigen input() die de invoer van
het testgeval teruggeeft. Daarna wordt de uitvoer vergeleken met die van de referentie-
oplossing op dezelfde invoer. Zo kunnen we, net als op CS Circles, een programma met
meerdere invoeren testen, zonder verborgen code vóór het programma van de leerling (die zou
anders ook in CodeLens verschijnen).

Een specificatie (zie tools/toetsen/) is een dict met:
  oplossing   referentie-oplossing (verplicht)
  gevallen    lijst van testgevallen, elk een dict met
                invoer    lijst met invoerregels voor input()
                voorcode  code die vóór het programma wordt uitgevoerd (bv. variabelen die
                          "het nakijkprogramma voor je definieert")
                aanroep   expressie die na het programma wordt geëvalueerd (bv. "f(3)");
                          de returnwaarde wordt ook vergeleken
              standaard: één geval zonder invoer
  voorcode    verborgen code vóór het programma bij gewoon Uitvoeren (standaard: de voorcode
              van het eerste geval)
  vergelijk   "exact" (standaard; witruimte aan het eind van regels telt niet),
              "getallen" (getallen mogen iets afwijken, relatief volgens tolerantie, standaard
              1e-6), "woorden" (alle witruimte telt niet)
  hergebruik  True: voer het programma van de leerling niet opnieuw uit, maar evalueer de aanroepen
              in de variabelen van de gewone uitvoering (voor trage programma's; alleen zonder invoer)
  tolerantie  toegestane relatieve afwijking bij vergelijk="getallen"
  tijdslimiet tijdslimiet in milliseconden voor Runestone (attribuut timelimit)
  verboden    lijst van (tekst, melding): tekst mag niet in de code van de leerling staan
  verplicht   lijst van (tekst, melding): tekst moet in de code van de leerling staan
  maxlengte   maximum aantal tekens in de code (zonder spaties aan het eind)
  maxwijzig   maximum aantal tekens dat t.o.v. de startcode veranderd mag worden
              (bewerkingsafstand, zoals "je mag hoogstens twee tekens veranderen")
  extra       extra testmethode(n) (Python-broncode, ingesprongen met 4 spaties)
  startcode   beginsituatie van het programmeervak (standaard: zoals op CS Circles)
  volgorde    (alleen volgorde-oefeningen) de juiste volgorde van de getoonde regels
  afhankelijk (alleen volgorde-oefeningen) {regel: [regels die ervoor moeten staan]} als
              meerdere volgordes goed zijn
  goed        andere goede oplossingen die de tests moeten halen (alleen voor tools/check_toetsen.py)
  fout        foute oplossingen die de tests moeten afkeuren (alleen voor tools/check_toetsen.py)
"""

HARNAS = r'''
import re as _re
from unittest.gui import TestCaseGui


class _TeWeinigInvoer(Exception):
    pass


def _voer_uit(_bron, _geval, _student=False):
    _regels = [str(_r) for _r in _geval.get("invoer", [])]
    _uit = []

    def _print(*args, **kw):
        _sep = kw.get("sep", " ")
        _end = kw.get("end", "\n")
        if _sep is None:
            _sep = " "
        if _end is None:
            _end = "\n"
        _uit.append(_sep.join([str(_a) for _a in args]) + _end)

    def _input(prompt=""):
        if len(_regels) == 0:
            raise _TeWeinigInvoer("het programma vraagt meer invoer (input) dan er is")
        return _regels.pop(0)

    _g = {"__name__": "__main__", "print": _print, "input": _input}
    _fout = None
    _waarde = None
    if _student and _HERGEBRUIK:
        # Het programma van de leerling is net al uitgevoerd; gebruik die variabelen.
        try:
            _waarde = eval(_geval["aanroep"], globals())
        except Exception as _e:
            _fout = type(_e).__name__ + ": " + str(_e)
        return "", _waarde, _fout
    try:
        if _geval.get("voorcode"):
            exec(_geval["voorcode"], _g)
        exec(_bron, _g)
        if _geval.get("aanroep"):
            _waarde = eval(_geval["aanroep"], _g)
    except Exception as _e:
        _fout = type(_e).__name__ + ": " + str(_e)
    return "".join(_uit), _waarde, _fout


def _normaal(_s):
    # Spaties aan het eind van een regel tellen niet mee, en het (onzichtbare) DEL-teken ook niet.
    _r = [_x.replace(chr(127), "").rstrip() for _x in _s.split("\n")]
    while len(_r) > 0 and _r[-1] == "":
        _r.pop()
    return "\n".join(_r)


def _getal(_s):
    try:
        return float(_s)
    except Exception:
        return None


def _stukken(_s):
    # Splits in getallen en overige tekens, zodat bv. "-13.333C" -> ["-13.333", "C"].
    return _re.findall(r"[-+]?(?:[0-9]+[.]?[0-9]*|[.][0-9]+)(?:[eE][-+]?[0-9]+)?|[^\s0-9.+-]+|\S", _s)


def _gelijk(_a, _b):
    if _VERGELIJK == "woorden":
        return _a.split() == _b.split()
    if _VERGELIJK == "getallen":
        _wa = _stukken(_a)
        _wb = _stukken(_b)
        if len(_wa) != len(_wb):
            return False
        for _i in range(len(_wa)):
            _x = _getal(_wa[_i])
            _y = _getal(_wb[_i])
            if _x is not None and _y is not None:
                if abs(_x - _y) > _TOLERANTIE * max(1.0, abs(_y)):
                    return False
            elif _wa[_i] != _wb[_i]:
                return False
        return True
    return _normaal(_a) == _normaal(_b)


def _afstand(_a, _b):
    """Bewerkingsafstand (Levenshtein) tussen twee strings."""
    _vorige = list(range(len(_b) + 1))
    for _i in range(len(_a)):
        _huidig = [_i + 1]
        for _j in range(len(_b)):
            _kosten = 0 if _a[_i] == _b[_j] else 1
            _huidig.append(min(_vorige[_j + 1] + 1, _huidig[_j] + 1, _vorige[_j] + _kosten))
        _vorige = _huidig
    return _vorige[-1]


def _zelfde(_a, _b):
    """Vergelijk returnwaarden; bij vergelijk="getallen" mogen kommagetallen iets afwijken."""
    if _VERGELIJK == "getallen" and type(_a) in (int, float) and type(_b) in (int, float) \
            and type(_a) != bool and type(_b) != bool:
        return abs(_a - _b) <= _TOLERANTIE * max(1.0, abs(_b))
    if type(_a) in (list, tuple) and type(_b) == type(_a):
        if len(_a) != len(_b):
            return False
        for _i in range(len(_a)):
            if not _zelfde(_a[_i], _b[_i]):
                return False
        return True
    return type(_a) == type(_b) and _a == _b


def _html(_s):
    return str(_s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _blok(_s):
    if _s == "":
        return "<i>(geen uitvoer)</i>"
    return "<pre style='text-align:left;margin:2px 0'>" + _html(_s) + "</pre>"


class _Toets(TestCaseGui):
    def test_1_programma(self):
        _bron = self.getEditorText()
        for _tekst, _melding in _VERPLICHT:
            self.assertTrue(_tekst in _bron, _melding)
        for _tekst, _melding in _VERBODEN:
            self.assertFalse(_tekst in _bron, _melding)
        if _MAXLENGTE:
            _lengte = len(_bron.rstrip())
            self.assertTrue(_lengte <= _MAXLENGTE, "Je code is %d tekens lang; het mag hoogstens %d zijn."
                            % (_lengte, _MAXLENGTE))
        if _MAXWIJZIG:
            _d = _afstand(_normaal(_ORIGINEEL), _normaal(_bron))
            self.assertTrue(_d <= _MAXWIJZIG, "Je hebt %d teken(s) veranderd; het mogen er hoogstens %d zijn."
                            % (_d, _MAXWIJZIG))
        _nr = 0
        for _geval in _GEVALLEN:
            _nr += 1
            _verwacht, _vwaarde, _vfout = _voer_uit(_OPLOSSING, _geval)
            _uitvoer, _waarde, _fout = _voer_uit(_bron, _geval, True)
            _info = "<b>Test %d</b>" % _nr
            if _geval.get("voorcode"):
                _info += "<br>vooraf: <code>" + _html("; ".join(_geval["voorcode"].strip().split("\n"))) + "</code>"
            if _geval.get("invoer"):
                _info += "<br>invoer:" + _blok("\n".join([str(_r) for _r in _geval["invoer"]]))
            if _geval.get("aanroep"):
                _info += "<br>aanroep: <code>" + _html(_geval["aanroep"]) + "</code>"
            if _fout is not None and _vfout is None:
                self.appendResult(False, _fout, "", _info + "<br>fout: <code>" + _html(_fout) + "</code>")
                continue
            _ok = _gelijk(_uitvoer, _verwacht)
            if _geval.get("aanroep"):
                _ok = _ok and _zelfde(_waarde, _vwaarde)
                _jij = _waarde
                _moet = _vwaarde
                if _normaal(_verwacht) != "" or _normaal(_uitvoer) != "":
                    _jij = _normaal(_uitvoer) + " / " + repr(_waarde)
                    _moet = _normaal(_verwacht) + " / " + repr(_vwaarde)
            else:
                _jij = _normaal(_uitvoer)
                _moet = _normaal(_verwacht)
            if not _ok:
                if _geval.get("aanroep"):
                    _info += "<br>verwachte returnwaarde: <code>" + _html(repr(_vwaarde)) + \
                             "</code><br>jouw returnwaarde: <code>" + _html(repr(_waarde)) + "</code>"
                if not _gelijk(_uitvoer, _verwacht) or _normaal(_verwacht) != "":
                    _info += "<br>verwachte uitvoer:" + _blok(_normaal(_verwacht)) + \
                             "jouw uitvoer:" + _blok(_normaal(_uitvoer))
            self.appendResult(_ok, _jij, _moet, _info)
'''


def maak_tests(slug, spec, startcode=""):
    gevallen = spec.get("gevallen") or [{}]
    lines = []
    lines.append("# Verborgen tests voor %s (gegenereerd door tools/harnas.py)" % slug)
    lines.append("_OPLOSSING = %r" % spec["oplossing"].strip("\n"))
    lines.append("_GEVALLEN = %r" % [clean_case(g) for g in gevallen])
    lines.append("_VERGELIJK = %r" % spec.get("vergelijk", "exact"))
    lines.append("_TOLERANTIE = %r" % spec.get("tolerantie", 1e-6))
    lines.append("_HERGEBRUIK = %r" % bool(spec.get("hergebruik")))
    lines.append("_VERBODEN = %r" % [tuple(x) for x in spec.get("verboden", [])])
    lines.append("_VERPLICHT = %r" % [tuple(x) for x in spec.get("verplicht", [])])
    lines.append("_MAXLENGTE = %r" % spec.get("maxlengte", 0))
    lines.append("_MAXWIJZIG = %r" % spec.get("maxwijzig", 0))
    lines.append("_ORIGINEEL = %r" % (startcode if spec.get("maxwijzig") else ""))
    code = "\n".join(lines) + "\n" + HARNAS
    if spec.get("extra"):
        code += "\n" + spec["extra"].rstrip() + "\n"
    code += "\n\n_Toets().main()\n"
    return code


def clean_case(g):
    out = {}
    for k in ("invoer", "voorcode", "aanroep"):
        if g.get(k):
            out[k] = g[k] if k != "invoer" else [str(x) for x in g[k]]
    return out


def voorcode(spec):
    """Verborgen code die bij gewoon Uitvoeren vóór het programma staat."""
    if "voorcode" in spec:
        return spec["voorcode"]
    gevallen = spec.get("gevallen") or [{}]
    return gevallen[0].get("voorcode")
