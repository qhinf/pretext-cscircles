"""Referentie-oplossingen en testgevallen per oefening, per les in een eigen module.

Elke module definieert TOETSEN = {slug: specificatie}; zie tools/harnas.py voor de velden.
"""

import importlib
import os
import pkgutil

ALLE = {}

for _m in pkgutil.iter_modules([os.path.dirname(__file__)]):
    _mod = importlib.import_module(__name__ + "." + _m.name)
    for _slug, _spec in getattr(_mod, "TOETSEN", {}).items():
        if _slug.lower() in ALLE:
            raise ValueError("dubbele slug %s" % _slug)
        ALLE[_slug.lower()] = _spec


def get(slug):
    return ALLE.get(slug.lower()) if slug else None
