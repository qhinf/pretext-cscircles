#!/usr/bin/env python3
"""Haal de CS Circles-pagina's op uit de Wayback Machine.

Nederlands: archief/<naam>.html     (paden uit tools/lessen.py)
Engels:     archief/en/<naam>.html  (paden uit het lessenmenu van de Engelse startpagina,
                                     met als terugval het Nederlandse pad zonder "-nl")

De verbinding met web.archive.org valt soms weg; elke pagina wordt daarom een aantal keer
opnieuw geprobeerd. Bestaande bestanden worden niet opnieuw opgehaald, dus bij een mislukte
pagina kun je het script gewoon nog eens draaien.

Gebruik: python3 tools/fetch_archive.py [--taal nl|en|alle] [naam ...]
         (standaard: --taal alle)
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lessen  # noqa: E402

SNAPSHOT = "20260316180938"
SITE = "https://cscircles.cemc.uwaterloo.ca/"


def archive_url(pad):
    # "id_" geeft de originele pagina zonder de werkbalk van de Wayback Machine
    return "https://web.archive.org/web/%sid_/%s%s" % (SNAPSHOT, SITE, pad)


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


def lesnummer(titel):
    """'01E: Errors' -> '1e', '0: Hallo!' -> '0'; None als er geen lesnummer is."""
    m = re.match(r"\s*0*(\d+[a-z]?)\s*:", titel, re.I)
    return m.group(1).lower() if m else None


def engelse_paden(index_html):
    """Lesnummer -> pad, uit het lessenmenu van de Engelse startpagina."""
    paden = {}
    for href, tekst in re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', index_html):
        nr = lesnummer(html.unescape(tekst))
        if not nr:
            continue
        pad = re.sub(r"^.*?cscircles\.cemc\.uwaterloo\.ca/", "", href).lstrip("/")
        if pad.startswith("http") or "-nl" in pad or "/" in pad.strip("/"):
            continue  # geen Engelse lespagina
        paden.setdefault(nr, pad)
    return paden


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--taal", choices=["nl", "en", "alle"], default="alle")
    ap.add_argument("namen", nargs="*")
    args = ap.parse_args()
    mislukt = []

    if args.taal in ("nl", "alle"):
        os.makedirs(os.path.join(ROOT, "archief"), exist_ok=True)
        for info in lessen.PAGINAS:
            if args.namen and info["naam"] not in args.namen:
                continue
            ok = fetch(archive_url(info["pad"]), os.path.join(ROOT, "archief", info["naam"] + ".html"))
            print("nl", info["naam"], "ok" if ok else "MISLUKT")
            if not ok:
                mislukt.append("nl/" + info["naam"])

    if args.taal in ("en", "alle"):
        doel = os.path.join(ROOT, "archief", "en")
        os.makedirs(doel, exist_ok=True)
        # Les 0 is de Engelse startpagina; die bevat ook het menu met de andere lessen.
        index = os.path.join(doel, "00-welkom.html")
        paden = {}
        if fetch(archive_url(""), index):
            with open(index, encoding="utf-8", errors="replace") as f:
                paden = engelse_paden(f.read())
        else:
            print("waarschuwing: Engelse startpagina niet opgehaald; paden worden geraden", file=sys.stderr)
        for info in lessen.PAGINAS:
            if args.namen and info["naam"] not in args.namen:
                continue
            nr = lesnummer(info["titel"])
            if info["pad"] == "nl/":
                pad = ""
            elif nr and nr in paden:
                pad = paden[nr]
            else:
                pad = re.sub(r"-nl/$", "/", info["pad"])  # bv. cheatsheet-nl/ -> cheatsheet/
            ok = fetch(archive_url(pad), os.path.join(doel, info["naam"] + ".html"))
            print("en", info["naam"], "<-", pad or "(startpagina)", "ok" if ok else "MISLUKT")
            if not ok:
                mislukt.append("en/" + info["naam"])

    if mislukt:
        print("\nMislukt (draai het script opnieuw): " + ", ".join(mislukt))
        sys.exit(1)


if __name__ == "__main__":
    main()
