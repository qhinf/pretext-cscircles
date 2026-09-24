"""Toetsen voor les 15A t/m 18. Zie tools/harnas.py voor de betekenis van de velden."""


def aanroepen(*exprs, voorcode=None):
    return [dict({"aanroep": e}, **({"voorcode": voorcode} if voorcode else {})) for e in exprs]


BASIC1 = ["5 GOTO 30", "10 GOTO 20", "20 GOTO 10", "30 GOTO 40", "40 END"]
BASIC2 = ["10 GOTO 21", "21 GOTO 37", "37 GOTO 21", "40 END"]
BASIC3 = ["100 END"]
BASIC4 = ["1 GOTO 3", "2 GOTO 4", "3 GOTO 2", "4 END"]
BASIC5 = ["7 GOTO 7", "8 END"]
BASIC6 = ["10 GOTO 30", "20 GOTO 50", "30 GOTO 20", "40 GOTO 10", "50 GOTO 40", "60 END"]

FINDLINE = """
def findLine(prog, target):
    for i in range(0, len(prog)):
        if prog[i].split()[0] == target:
            return i
"""

GETBASIC = """
def getBASIC():
    prog = []
    while True:
        regel = input()
        prog.append(regel)
        if regel.split()[1] == 'END':
            return prog
"""

EXECUTE = """
def execute(prog):
    visited = [False] * len(prog)
    location = 0
    while True:
        if location == len(prog) - 1:
            return "success"
        if visited[location]:
            return "infinite loop"
        visited[location] = True
        T = prog[location].split()[2]
        location = findLine(prog, T)
"""

DIGITALSUM = """
def digitalSum(n):
    if n < 10:
        return n
    else:
        return n % 10 + digitalSum(n // 10)
"""

LETTERGOODNESS = ("letterGoodness = [.0817, .0149, .0278, .0425, .1270, .0223, .0202, .0609, .0697, "
                  ".0015, .0077, .0402, .0241, .0675, .0751, .0193, .0009, .0599, .0633, .0906, .0276, "
                  ".0098, .0236, .0015, .0197, .0007]")

TOETSEN = {
    # ---------------- Les 15A ----------------
    "15a.getbasic": {
        "oplossing": GETBASIC,
        "gevallen": [{"invoer": p, "aanroep": "getBASIC()"} for p in (BASIC1, BASIC2, BASIC3, BASIC6)],
    },
    "15a.goto": {
        "oplossing": FINDLINE,
        "gevallen": aanroepen("findLine(['10 GOTO 20', '20 END'], '10')",
                              "findLine(['10 GOTO 20', '20 END'], '20')",
                              "findLine(%r, '30')" % BASIC1, "findLine(%r, '5')" % BASIC1,
                              "findLine(%r, '37')" % BASIC2, "findLine(%r, '1')" % BASIC4,
                              "findLine(['1 GOTO 11', '11 GOTO 111', '111 END'], '11')"),
    },
    "15a.main": {
        "voorcode": FINDLINE,
        "oplossing": EXECUTE,
        "gevallen": aanroepen(*["execute(%r)" % p for p in (BASIC1, BASIC2, BASIC3, BASIC4, BASIC5, BASIC6)],
                              voorcode=FINDLINE),
    },
    "15a.overall": {
        "oplossing": GETBASIC + FINDLINE + EXECUTE + "\nprint(execute(getBASIC()))",
        "gevallen": [{"invoer": p} for p in (BASIC1, BASIC2, BASIC3, BASIC4, BASIC5, BASIC6)],
    },

    # ---------------- Les 15B ----------------
    "15b.degrees": {
        "oplossing": """
temp = input()
x = float(temp[0:len(temp)-1])
if temp[len(temp)-1] == 'C':
    print(str(x * 9 / 5 + 32) + 'F')
else:
    print(str((x - 32) * 5 / 9) + 'C')
""",
        "gevallen": [{"invoer": [t]} for t in ("8F", "12.5C", "-40C", "-40F", "100C", "0F", "98.6F", "37C")],
        "vergelijk": "getallen",
        "tolerantie": 1e-4,
        "goed": ["""
t = input()
g = float(t[:-1])
if t[-1] == 'C':
    print(str(round(g * 1.8 + 32, 3)) + 'F')
else:
    print(str(round((g - 32) / 1.8, 3)) + 'C')
"""],
        "fout": ["t = input()\nprint(t)"],
    },
    "15b.creditcard": {
        "oplossing": """
def check(S):
    if len(S) != 19:
        return False
    total = 0
    for i in range(0, 19):
        if i % 5 == 4:
            if S[i] != ' ':
                return False
        else:
            if S[i] < '0' or S[i] > '9':
                return False
            total = total + int(S[i])
    return total % 10 == 0
""",
        "gevallen": aanroepen("check('9384 3495 3297 0123')", "check('0000 0000 0000 0000')",
                              "check('4000 0000 0000 0006')", "check('5555 5555 5555 5555')",
                              "check('1111 1111 1111 1115')", "check('1111 1111 1111 1116')",
                              "check('9384349532970123')", "check('9384 3495 3297 012')",
                              "check('9384 3495 3297 01234')", "check('93a4 3495 3297 0123')",
                              "check('4000-0000-0000-0006')", "check(' 4000 0000 0000 006')",
                              "check('4000 0000 0000 0006 ')"),
    },
    "15b.poem": {
        "oplossing": """
woorden = []
while True:
    regel = input()
    if regel == '###':
        break
    woorden = woorden + regel.lower().split()
beste = woorden[0]
for woord in woorden:
    if woorden.count(woord) > woorden.count(beste):
        beste = woord
print(beste)
""",
        "gevallen": [
            {"invoer": ["Here is a line like sparkling wine", "Line up fast or be the last", "###"]},
            {"invoer": ["the cat and THE dog", "###"]},
            {"invoer": ["Turing", "###"]},
            {"invoer": ["a b c", "B c d", "c D e", "###"]},
        ],
    },
    "15b.choose": {
        "oplossing": """
def choose(n, k):
    result = 1
    for i in range(0, k):
        result = result * (n - i) / (k - i)
    return result
""",
        "gevallen": aanroepen("choose(5, 2)", "choose(10, 3)", "choose(6, 5)", "choose(20, 10)", "choose(2, 1)",
                              "choose(30, 15)"),
        "vergelijk": "getallen",
    },

    # ---------------- Les 15C ----------------
    "15c.autodecrypt": {
        "voorcode": LETTERGOODNESS,
        "oplossing": """
def verschuif(letter, S):
    if letter == ' ':
        return letter
    return chr((ord(letter) - ord('A') + S) % 26 + ord('A'))

tekst = input()
beste = ''
besteWaarde = -1
for S in range(0, 26):
    kandidaat = ''
    waarde = 0
    for letter in tekst:
        nieuw = verschuif(letter, S)
        kandidaat = kandidaat + nieuw
        if nieuw != ' ':
            waarde = waarde + letterGoodness[ord(nieuw) - ord('A')]
    if waarde > besteWaarde:
        beste = kandidaat
        besteWaarde = waarde
print(beste)
""",
        "gevallen": [{"voorcode": LETTERGOODNESS, "invoer": [t]} for t in (
            "LQKP OG CV GKIJV DA VJG BQQ", "JRRG", "TKJJ", "HUD",
            "QEB NRFZH YOLTK CLU GRJMP LSBO QEB IXWV ALD",
            "ZNK WAOIQ HXUCT LUD PASVY UBKX ZNK RGFE JUM")],
    },

    # ---------------- Les 16 ----------------
    "16.countup": {
        "oplossing": """
def countup(n):
    if n == 0:
        print('Boemm!')
    else:
        countup(n - 1)
        print(n)
""",
        "gevallen": aanroepen("countup(3)", "countup(0)", "countup(1)", "countup(10)"),
    },
    "16.countdownby2": {
        "oplossing": """
def countdownBy2(n):
  if n <= 0:
    print('Boemm!')
  else:
    print(n)
    countdownBy2(n - 2)
""",
        "gevallen": aanroepen("countdownBy2(6)", "countdownBy2(7)", "countdownBy2(1)", "countdownBy2(0)",
                              "countdownBy2(15)"),
    },
    "16.digitalsum": {
        "startcode": "def digitalSum(n):\n  if n < 10:\n    return n\n  else:\n    # recursive case\n",
        "oplossing": DIGITALSUM,
        "gevallen": aanroepen("digitalSum(2019)", "digitalSum(5)", "digitalSum(99999)", "digitalSum(1000000)",
                              "digitalSum(10)", "digitalSum(123456789)"),
    },
    "16.digitalroot": {
        "voorcode": DIGITALSUM,
        "oplossing": """
def digitalRoot(n):
    if n < 10:
        return n
    return digitalRoot(digitalSum(n))
""",
        "gevallen": aanroepen("digitalRoot(2019)", "digitalRoot(0)", "digitalRoot(9)", "digitalRoot(99999999)",
                              "digitalRoot(12345)", "digitalRoot(10)", voorcode=DIGITALSUM),
    },
    "16.hailstone": {
        "oplossing": """
def hagelsteen(n):
    print(n)
    if n == 1:
        return
    if n % 2 == 0:
        hagelsteen(n // 2)
    else:
        hagelsteen(3 * n + 1)
""",
        "gevallen": aanroepen("hagelsteen(5)", "hagelsteen(1)", "hagelsteen(7)", "hagelsteen(27)",
                              "hagelsteen(64)"),
        # n/2 geeft kommagetallen (16.0), dat is ook goed
        "vergelijk": "getallen",
        "goed": ["""
def hagelsteen(n):
    print(n)
    if n != 1:
        if n % 2 == 0:
            hagelsteen(n / 2)
        else:
            hagelsteen(3 * n + 1)
"""],
    },
    "16.fractal-lijn": {
        # regels: 0 print(n * '-')  1 ruler(n - 1)  2 def ruler(n):  3 print('-')  4 else:  5 if n == 1:
        #         6 ruler(n - 1)
        "volgorde": [2, 5, 3, 4, 1, 0, 6],
    },

    # ---------------- Les 18 ----------------
    "18.nibofacci": {
        # regels: 0 return 1  1 else:  2 def Fibonacci(n):  3 return Fibonacci(n-1) + Fibonacci(n-2)
        #         4 if (n==1 or n==2):
        "volgorde": [2, 4, 0, 1, 3],
    },
    "18.fast-fibonacci": {
        # regels: 0 sequence.append(...)  1 return sequence[n]  2 for i in range(3, n+1):
        #         3 def Fibonacci(n):  4 sequence = [0, 1, 1]
        "volgorde": [3, 4, 2, 0, 1],
    },
    "18.sieve": {
        # De referentie rekent niet de hele zeef uit (dat kost in de browser te veel tijd), maar
        # bepaalt alleen de opgevraagde waarden.
        "oplossing": """
class _Priemtabel:
    def __len__(self):
        return 1000001
    def __getitem__(self, i):
        if i < 2:
            return False
        d = 2
        while d * d <= i:
            if i % d == 0:
                return False
            d = d + 1
        return True
isPrime = _Priemtabel()
""",
        # Eén testgeval, zodat de (trage) zeef van de leerling maar één keer extra wordt uitgevoerd.
        "gevallen": [{"aanroep": "(len(isPrime), [isPrime[i] for i in range(0, 30)], "
                                 "[isPrime[i] for i in (97, 100, 7919, 7917, 65537, 999983, 999999, 1000000)])"}],
        "tijdslimiet": 60000,
        "hergebruik": True,
        "goed": ["""
N = 1000001
isPrime = [True] * N
isPrime[0] = False
isPrime[1] = False
for i in range(2, N):
    if isPrime[i]:
        for j in range(i * i, N, i):
            isPrime[j] = False
"""],
        "fout": ["isPrime = [False] * 1000001", "isPrime = [True] * 1000001"],
    },
}
