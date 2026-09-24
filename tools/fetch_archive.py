#!/usr/bin/env python3
"""Haal de Nederlandse CS Circles-pagina's op uit de Wayback Machine naar archief/.

De verbinding met web.archive.org valt soms weg; elke pagina wordt daarom een aantal keer
opnieuw geprobeerd. Bestaande bestanden worden niet opnieuw opgehaald.

Gebruik: python3 tools/fetch_archive.py [naam ...]
"""
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lessen  # noqa: E402

SNAPSHOT = "20260316180938"


def fetch(url, out, tries=30):
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return True
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
            with open(out, "wb") as f:
                f.write(data)
            return True
        except Exception as e:  # noqa: BLE001
            print("  opnieuw (%d): %s" % (i + 1, e), file=sys.stderr)
            time.sleep(min(2 + i * 3, 20))
    return False


def main():
    os.makedirs(os.path.join(ROOT, "archief"), exist_ok=True)
    only = sys.argv[1:]
    for info in lessen.PAGINAS:
        if only and info["naam"] not in only:
            continue
        # "id_" geeft de originele pagina zonder de werkbalk van de Wayback Machine
        url = "https://web.archive.org/web/%sid_/https://cscircles.cemc.uwaterloo.ca/%s" % (SNAPSHOT, info["pad"])
        ok = fetch(url, os.path.join(ROOT, "archief", info["naam"] + ".html"))
        print(info["naam"], "ok" if ok else "MISLUKT")


if __name__ == "__main__":
    main()
