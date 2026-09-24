#!/usr/bin/env python3
"""Controleer source/main.ptx tegen het PreTeXt-schema (pretext-dev.rng, inclusief interactieve
oefeningen). Vereist jing: pip install jingtrang."""
import glob
import os
import subprocess
import sys
import tempfile

import lxml.etree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cands = sorted(glob.glob(os.path.expanduser("~/.ptx/*/core/schema/pretext-dev.rng")))
if not cands:
    sys.exit("PreTeXt-schema niet gevonden; draai eerst 'pretext build' zodat ~/.ptx gevuld is.")
doc = ET.parse(os.path.join(ROOT, "source", "main.ptx"))
doc.xinclude()
with tempfile.NamedTemporaryFile("wb", suffix=".xml", delete=False) as f:
    doc.write(f)
    merged = f.name
r = subprocess.run(["pyjing", cands[-1], merged], capture_output=True, text=True)
out = [ln.replace(merged, "main.ptx") for ln in (r.stdout + r.stderr).splitlines() if "JAVA_TOOL_OPTIONS" not in ln]
print("\n".join(out))
print("geldig" if r.returncode == 0 else "%d fouten" % len(out))
sys.exit(r.returncode)
