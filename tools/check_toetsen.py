#!/usr/bin/env python3
"""Controleer de verborgen tests van alle programmeeroefeningen in Runestones Skulpt (via node).

Voor elke oefening:
  1. de referentie-oplossing moet alle tests halen;
  2. de startcode (zoals op CS Circles) en de foute oplossingen in spec["fout"] mogen niet
     alle tests halen;
  3. de referentie-oplossing moet in CPython dezelfde uitvoer geven als in Skulpt.

Skulpt komt uit de Runestone-repository:
  git clone --depth 1 --filter=blob:none --sparse https://github.com/RunestoneInteractive/rs
  cd rs && git sparse-checkout set --skip-checks bases/rsptx/interactives/runestone/activecode
en dan: SKULPT_DIR=.../rs/bases/rsptx/interactives/runestone/activecode/js python3 tools/check_toetsen.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import toetsen  # noqa: E402
from harnas import maak_tests, voorcode  # noqa: E402

SKULPT = os.environ.get("SKULPT_DIR")


def skulpt(prefix, code, tests, invoer=()):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"prefix": prefix, "code": code, "tests": tests, "invoer": list(invoer)}, f)
    r = subprocess.run(["node", os.path.join(ROOT, "tools", "skulpt_run.js"), SKULPT, f.name],
                       capture_output=True, text=True, timeout=300)
    os.unlink(f.name)
    return r.stdout + r.stderr


def cpython(code, geval):
    """Voer de referentie-oplossing uit in CPython, net als de harnas."""
    invoer = [str(x) for x in geval.get("invoer", [])]
    prog = (geval.get("voorcode") or "") + "\n" + code + "\n"
    if geval.get("aanroep"):
        prog += "print('<<RETURN>>', repr(%s))\n" % geval["aanroep"]
    r = subprocess.run([sys.executable, "-c", prog], input="\n".join(invoer) + "\n",
                       capture_output=True, text=True, timeout=60)
    return r.stdout, r.stderr


def startcodes():
    """Lees de startcode per oefening uit de gegenereerde PreTeXt."""
    import lxml.etree as ET
    res = {}
    for fn in os.listdir(os.path.join(ROOT, "source")):
        if not fn.startswith("les-"):
            continue
        d = ET.parse(os.path.join(ROOT, "source", fn))
        for prog in d.iter("program"):
            lab = prog.get("label", "")
            if lab.startswith("oef-") and lab.endswith("-code"):
                res[lab[:-5]] = (prog.findtext("code") or "").strip("\n")
    return res


def main():
    if not SKULPT:
        sys.exit("Zet SKULPT_DIR (zie docstring).")
    only = sys.argv[1:]
    starts = startcodes()
    fouten = 0
    for slug, spec in sorted(toetsen.ALLE.items()):
        if "oplossing" not in spec:
            continue
        label = "oef-" + re.sub(r"[^A-Za-z0-9]+", "-", slug).strip("-").lower()
        if only and slug not in only:
            continue
        start = spec.get("startcode", starts.get(label, ""))
        tests = maak_tests(slug, spec, start)
        pre = voorcode(spec)
        prefix = (pre.strip("\n") + "\n") if pre else ""
        gevallen = spec.get("gevallen") or [{}]
        invoer = gevallen[0].get("invoer", [])
        out = skulpt(prefix, spec["oplossing"].strip("\n"), tests, invoer)
        m = re.search(r"SUMMARY passed=(\d+) failed=(\d+)", out)
        ok = m and int(m.group(2)) == 0 and "SKULPT-FOUT" not in out
        out2 = skulpt(prefix, start, tests, invoer)
        m2 = re.search(r"SUMMARY passed=(\d+) failed=(\d+)", out2)
        start_faalt = (m2 is None) or int(m2.group(2)) > 0 or "SKULPT-FOUT" in out2
        # Alternatieve goede oplossingen (spec["goed"]) moeten alle tests halen.
        for goed in spec.get("goed", []):
            out4 = skulpt(prefix, goed.strip("\n"), tests, invoer)
            m4 = re.search(r"SUMMARY passed=(\d+) failed=(\d+)", out4)
            if not (m4 and int(m4.group(2)) == 0 and "SKULPT-FOUT" not in out4):
                ok = False
                print("   goede oplossing wordt afgekeurd:\n   " + goed.strip().replace("\n", "\n   "))
                print("   " + "\n   ".join(l for l in out4.splitlines() if "PASS" not in l)[:2000])
        # Foute oplossingen (spec["fout"]) moeten door de tests worden afgekeurd.
        for fout in spec.get("fout", []):
            out3 = skulpt(prefix, fout.strip("\n"), tests, invoer)
            m3 = re.search(r"SUMMARY passed=(\d+) failed=(\d+)", out3)
            if m3 and int(m3.group(2)) == 0 and "SKULPT-FOUT" not in out3:
                start_faalt = False
                print("   foute oplossing wordt goedgekeurd:\n   " + fout.strip().replace("\n", "\n   "))
        verschil = []
        for g in gevallen:
            so, se = cpython(spec["oplossing"], g)
            if se.strip():
                verschil.append("CPython-fout: " + se.strip().splitlines()[-1])
        status = "OK " if ok and start_faalt and not verschil else "FOUT"
        if status == "FOUT":
            fouten += 1
        print("%s %-28s %d gevallen%s%s%s" % (status, slug, len(gevallen),
                                             "" if ok else " | referentie faalt",
                                             "" if start_faalt else " | startcode slaagt",
                                             "".join(" | " + v for v in verschil)))
        if not ok:
            print("   " + "\n   ".join(l for l in out.splitlines() if "PASS" not in l)[:3000])
    print("%d fouten" % fouten)
    sys.exit(1 if fouten else 0)


if __name__ == "__main__":
    main()
