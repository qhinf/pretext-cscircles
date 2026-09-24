"""De pagina's van de Nederlandse CS Circles, in volgorde, met hun PreTeXt-id's."""

import re
import urllib.parse

# naam: bestandsnaam in archief/ ; pad: pad op cscircles.cemc.uwaterloo.ca ; id: xml:id in PreTeXt
PAGINAS = [
    {"naam": "00-welkom", "pad": "nl/", "id": "les-00", "titel": "0: Hallo!"},
    {"naam": "01-variables", "pad": "1-variables-nl/", "id": "les-01", "titel": "1: Variabelen"},
    {"naam": "01e-errors", "pad": "1e-errors-nl/", "id": "les-01e", "titel": "1E: Foutmeldingen"},
    {"naam": "02-functions", "pad": "2-functions-nl/", "id": "les-02", "titel": "2: Functies"},
    {"naam": "02x-extra", "pad": "2x-extra-practice-nl/", "id": "les-02x", "titel": "2X: Extra oefening"},
    {"naam": "03-comments", "pad": "3-comments-and-quotes-nl/", "id": "les-03",
     "titel": "3: Commentaar en aanhalingstekens"},
    {"naam": "04-types", "pad": "4-types-nl/", "id": "les-04", "titel": "4: Types"},
    {"naam": "05-input", "pad": "5-input-nl/", "id": "les-05", "titel": "5: Invoer"},
    {"naam": "06-if", "pad": "06-if/", "id": "les-06", "titel": "6: If"},
    {"naam": "06d-design", "pad": "6d-nl/", "id": "les-06d", "titel": "6D: Design, debuggen en donuts"},
    {"naam": "07-rich-editor", "pad": "7-rich-editor-nl/", "id": "les-07", "titel": "7: De editor"},
    {"naam": "07a-strings", "pad": "7a-strings-nl/", "id": "les-07a", "titel": "7A: Strings"},
    {"naam": "07b-math", "pad": "7b-math-nl/", "id": "les-07b", "titel": "7B: Wiskunde"},
    {"naam": "07c-loops", "pad": "7c-loops-nl/", "id": "les-07c", "titel": "7C: Lussen"},
    {"naam": "08-remix", "pad": "8-remix-nl/", "id": "les-08", "titel": "8: Van alles wat"},
    {"naam": "09-else", "pad": "9-else-and-or-not-nl/", "id": "les-09", "titel": "9: Else, and, or, not"},
    {"naam": "10-def", "pad": "10-def-nl/", "id": "les-10", "titel": "10: Functies definiëren"},
    {"naam": "11a-lower", "pad": "11a-lower-case-nl/", "id": "les-11a", "titel": "11A: Kleine letters"},
    {"naam": "11b-scope", "pad": "11b-variable-scope-nl/", "id": "les-11b",
     "titel": "11B: De scope van een variabele"},
    {"naam": "11c-geometry", "pad": "11c-geometry-nl/", "id": "les-11c", "titel": "11C: Meetkunde"},
    {"naam": "12-tips", "pad": "12-tips-nl/", "id": "les-12", "titel": "12: Tips"},
    {"naam": "13-lists", "pad": "13-lists-arrays-nl/", "id": "les-13", "titel": "13: Lijsten (arrays)"},
    {"naam": "14-methods", "pad": "14-methods-nl/", "id": "les-14", "titel": "14: Methoden"},
    {"naam": "15a-termination", "pad": "15a-termination-determination-nl/", "id": "les-15a",
     "titel": "15A: Komt er een einde aan?"},
    {"naam": "15b-pushups", "pad": "15b-python-pushups-nl/", "id": "les-15b", "titel": "15B: Python push-ups"},
    {"naam": "15c-caesar", "pad": "15c-nl/", "id": "les-15c", "titel": "15C: Caesar's JVTIVK JRCRU IVTZGV"},
    {"naam": "16-recursion", "pad": "16-recursion-nl/", "id": "les-16", "titel": "16: Recursie"},
    {"naam": "17-is", "pad": "17-is-nl/", "id": "les-17", "titel": "17: Is"},
    {"naam": "18-efficiency", "pad": "18-efficiency-nl/", "id": "les-18", "titel": "18: Efficiëntie"},
    # Bijlagen
    {"naam": "x-cheatsheet", "pad": "cheatsheet-nl/", "id": "bijlage-spiekbriefje", "titel": "Spiekbriefje",
     "soort": "appendix"},
    {"naam": "x-runathome", "pad": "run-at-home-nl/", "id": "bijlage-python-thuis", "titel": "Python thuis",
     "soort": "appendix"},
    {"naam": "x-resources", "pad": "resources-nl/", "id": "bijlage-bronnen", "titel": "Bronnen",
     "soort": "appendix"},
    {"naam": "x-thanks", "pad": "thanks-nl/", "id": "bijlage-dank", "titel": "Dank",
     "soort": "appendix"},
]

# Paden die nog als (gearchiveerde) link zinvol zijn; al het andere op cscircles wordt platte tekst.
_KEEP = ("/wp-content/lesson_files/",)


def _slug(url):
    p = urllib.parse.urlparse(url)
    path = p.path
    if p.netloc and "cscircles" not in p.netloc:
        return None
    return path.strip("/")


def link_target(href):
    """Geef de xml:id van de les waar href naar verwijst, of None."""
    if href.startswith("#"):
        return None
    slug = _slug(href)
    if slug is None:
        return None
    for info in PAGINAS:
        pad = info["pad"].strip("/")
        if slug == pad or slug == re.sub(r"-nl$", "", pad) or slug + "-nl" == pad:
            return info["id"]
    # Engelse slugs zonder -nl, zoals /7a-strings/
    for info in PAGINAS:
        pad = re.sub(r"-nl$", "", info["pad"].strip("/"))
        if pad and slug.startswith(pad):
            return info["id"]
    return None


def keep_url(href):
    return any(k in href for k in _KEEP)


def image_name(src):
    """Een unieke, stabiele bestandsnaam voor een afbeelding."""
    p = urllib.parse.urlparse(src)
    path = p.path
    m = re.search(r"/lesson_files/img/([^/]+)/([^/]+)$", path)
    if m:
        return "%s-%s" % (m.group(1).lower(), m.group(2))
    base = path.rsplit("/", 1)[-1]
    if not base or "." not in base:
        return None
    return base
