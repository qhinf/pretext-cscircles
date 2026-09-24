// Voert een programma uit in de Skulpt-versie van Runestone (onder node), zoals ActiveCode dat doet:
// verborgen voorcode + code van de leerling + verborgen tests.
// Gebruik: node skulpt_run.js <skulpt-map> <json-bestand met {prefix, code, tests, invoer}>
const fs = require("fs");
const path = require("path");
const dir = process.argv[2];
const job = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
global.window = global;
global.self = global;
global.document = { getElementById: () => null };
global.componentMap = { test: { editor: { getValue: () => job.code } } };
eval(fs.readFileSync(path.join(dir, "skulpt.min.js"), "utf8"));
eval(fs.readFileSync(path.join(dir, "skulpt-stdlib.js"), "utf8"));
const gui = fs.readFileSync(path.join(__dirname, "skulpt_gui_stub.py"), "utf8");
const invoer = (job.invoer || []).slice();
Sk.configure({
  output: (t) => process.stdout.write(t),
  inputfun: (p) => (invoer.length ? invoer.shift() : ""),
  inputfunTakesPrompt: true,
  read: (f) => {
    if (f === "src/lib/unittest/gui.py") return gui;
    if (Sk.builtinFiles.files[f] !== undefined) return Sk.builtinFiles.files[f];
    throw "File not found: '" + f + "'";
  },
  __future__: Sk.python3,
  killableWhile: true,
  killableFor: true,
});
Sk.execLimit = 30000;
Sk.divid = "test";
const prog = (job.prefix || "") + job.code + "\n" + (job.tests || "");
Sk.misceval
  .asyncToPromise(() => Sk.importMainWithBody("<stdin>", false, prog, true))
  .then(
    () => {},
    (e) => { console.log("SKULPT-FOUT: " + e.toString()); process.exitCode = 1; }
  );
