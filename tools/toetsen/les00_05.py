"""Toetsen voor les 0 t/m 5. Zie tools/harnas.py voor de betekenis van de velden."""

TOETSEN = {
    # ---------------- Les 0 ----------------
    "0.hallo": {
        "oplossing": 'print("Hallo iedereen!")',
    },

    # ---------------- Les 1 ----------------
    "1.heads": {
        "oplossing": """
hoofden = mensen
schouders = 2 * mensen
knieen = 2 * mensen
tenen = 10 * mensen
""",
        "gevallen": [
            {"voorcode": "mensen = 5", "aanroep": "(hoofden, schouders, knieen, tenen)"},
            {"voorcode": "mensen = 0", "aanroep": "(hoofden, schouders, knieen, tenen)"},
            {"voorcode": "mensen = 1", "aanroep": "(hoofden, schouders, knieen, tenen)"},
            {"voorcode": "mensen = 37", "aanroep": "(hoofden, schouders, knieen, tenen)"},
        ],
    },
    "1.bereken-de-snelheid": {
        # regels: 0 totaleAfstand=..., 1 print, 2 gemiddeldeSnelheid=..., 3 totaleTijd=...
        "volgorde": [0, 3, 2, 1],
        "afhankelijk": {2: [0, 3], 1: [2]},
    },
    "1.swap": {
        "oplossing": """
xOrigineel = x
x = y
y = xOrigineel
""",
        "gevallen": [
            {"voorcode": "x = 10\ny = 99", "aanroep": "(x, y)"},
            {"voorcode": "x = -3\ny = 7", "aanroep": "(x, y)"},
            {"voorcode": "x = 5\ny = 5", "aanroep": "(x, y)"},
            {"voorcode": "x = 0\ny = 123456", "aanroep": "(x, y)"},
        ],
        "fout": ["x = y\ny = x", "x = 99\ny = 10"],
    },

    # ---------------- Les 1E ----------------
    "1e.product": {
        "oplossing": "print(1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10)",
    },
    "1e.joe": {
        "oplossing": """
print("Hello")
username = "Joe"
print(username)
""",
        "maxwijzig": 2,
        "fout": ['print("Hello")\nprint("Joe")'],
    },
    "1e.growth": {
        "oplossing": """
populationIn2012 = 1000
populationIn2013 = populationIn2012 * 1.1
populationIn2014 = populationIn2013 * 1.1
populationIn2015 = populationIn2014 * 1.1
""",
        "gevallen": [{"aanroep": "(populationIn2013, populationIn2014, populationIn2015)"}],
        "maxwijzig": 3,
    },

    # ---------------- Les 2 ----------------
    "2.bridges1": {
        "oplossing": "print(min(a, b, c))",
        "gevallen": [
            {"voorcode": "a = 10\nb = 7\nc = 12"},
            {"voorcode": "a = 3\nb = 8\nc = 9"},
            {"voorcode": "a = 20\nb = 30\nc = 5"},
            {"voorcode": "a = 4\nb = 4\nc = 4"},
        ],
    },
    "2.bridges2": {
        "oplossing": "print(max(min(a, b, c), min(d, e)))",
        "gevallen": [
            {"voorcode": "a = 10\nb = 7\nc = 12\nd = 8\ne = 20"},
            {"voorcode": "a = 10\nb = 7\nc = 12\nd = 6\ne = 20"},
            {"voorcode": "a = 3\nb = 8\nc = 9\nd = 2\ne = 1"},
            {"voorcode": "a = 20\nb = 30\nc = 25\nd = 40\ne = 21"},
            {"voorcode": "a = 5\nb = 5\nc = 5\nd = 5\ne = 5"},
        ],
    },
    "2.klik-en-sleep-sorteer": {
        # regels: 0 print(max), 1 print(min), 2 print(midden)
        "volgorde": [1, 2, 0],
    },

    # ---------------- Les 2X ----------------
    "2x.simplifyagain": {
        "oplossing": "print(-max(-A, -B))",
        "fout": ["print(min(A, B))", "print(max(A, B))"],
        "gevallen": [
            {"voorcode": "A = 3\nB = 8"},
            {"voorcode": "A = 8\nB = 3"},
            {"voorcode": "A = -5\nB = 2"},
            {"voorcode": "A = 7\nB = 7"},
        ],
        "verboden": [("min", "Je mag de functie <code>min</code> niet gebruiken.")],
    },
    "2x.saldo": {
        "oplossing": "print(min(saldo, max(10, 0.021 * saldo)))",
        "gevallen": [
            {"voorcode": "saldo = 1000"},
            {"voorcode": "saldo = 600"},
            {"voorcode": "saldo = 25"},
            {"voorcode": "saldo = 8"},
            {"voorcode": "saldo = 476.19"},
        ],
        "vergelijk": "getallen",
        "fout": ["print(max(10, 0.021 * saldo))"],
        "verplicht": [("min", "Gebruik de functie <code>min</code>."),
                      ("max", "Gebruik de functie <code>max</code>.")],
    },
    "2x.versleep-oefening-sorteren": {
        # regels: 0 z=tmp, 1 y=tmp, 2 y=min(y,z), 3 y=tmp, 4 tmp=max(x,y), 5 tmp=max(x,y),
        #         6 tmp=max(y,z), 7 x=min(x,y), 8 x=min(x,y)
        "volgorde": [4, 7, 1, 6, 2, 0, 5, 8, 3],
    },

    # ---------------- Les 3 ----------------
    "3.debug": {
        "oplossing": """
# doel: druk het aantal seconden in een week af
secondsPerMinute = 60
secondsPerHour = secondsPerMinute * 60
secondsPerDay = secondsPerHour * 24
daysPerWeek = 7
print(secondsPerDay * daysPerWeek)
""",
    },
    "3.escape": {
        "oplossing": r"""print('Escape \'t aanhalingsteken met \'n backslash: \\"')""",
    },

    # ---------------- Les 4 ----------------
    "4.pizza": {
        "oplossing": """
L = float(inputStr)
print(int(L * L / 100))
""",
        "gevallen": [
            {"voorcode": 'inputStr = "17.5"'},
            {"voorcode": 'inputStr = "10"'},
            {"voorcode": 'inputStr = "9.99"'},
            {"voorcode": 'inputStr = "31.7"'},
            {"voorcode": 'inputStr = "100.0"'},
        ],
    },

    # ---------------- Les 5 ----------------
    "5.echo": {
        "oplossing": """
tekst = input()
print(tekst)
print(tekst)
""",
        "gevallen": [
            {"invoer": ["Echo"]},
            {"invoer": ["Hallo wereld!"]},
            {"invoer": ["42"]},
        ],
    },
}
