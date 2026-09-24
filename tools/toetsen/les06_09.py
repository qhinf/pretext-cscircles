"""Toetsen voor les 6 t/m 9. Zie tools/harnas.py voor de betekenis van de velden."""

TOETSEN = {
    # ---------------- Les 6 ----------------
    "6.ihop": {
        "oplossing": """
pannenkoeken = int(input())
if pannenkoeken > 3:
    print("Yum!")
if pannenkoeken <= 3:
    print("Still hungry!")
""",
        "gevallen": [{"invoer": [n]} for n in (5, 3, 4, 0, 100, -2)],
        "fout": ['pannenkoeken = int(input())\nif pannenkoeken >= 3:\n    print("Yum!")\n'
                 'if pannenkoeken < 3:\n    print("Still hungry!")'],
    },
    # De vier volgorde-oefeningen over inspringen. Regels (met hun inspringing):
    #   0 'if 1000 < 10:'  1 '   print("message 1")' (3 spaties)  2 '  print("message 2")' (2 spaties)
    #   3 'if 2 > 1:'      4 '  print("message 3")'
    # Er zijn soms meerdere goede volgordes; we kiezen er telkens één.
    "6.onverwacht-inspringen-eng-unexpected-indent": {
        # if / 2 spaties / 3 spaties -> unexpected indent
        "volgorde": [0, 2, 1, 3, 4],
    },
    "6.onverwacht-niet-inspringen-eng-unexpected-unindent": {
        # regels hier: 0 'if 1000 < 10:' 1 '  print("message 2")' 2 'if 2 > 1:' 3 '  print("message 3")'
        #              4 '   print("message 1")'
        # if / 3 spaties / 2 spaties -> unindent does not match any outer indentation level
        "volgorde": [0, 4, 1, 2, 3],
    },
    "6.inspringen-verwacht-eng-expected-indent": {
        # if / if -> expected an indented block
        "volgorde": [0, 3, 4, 2, 1],
    },
    "6.alles-in-orde": {
        "volgorde": [0, 1, 3, 4, 2],
    },
    "6.sign": {
        "oplossing": """
x = int(input())
if x > 0:
    print("Positief")
if x < 0:
    print("Negatief")
if x == 0:
    print("Nul")
""",
        "gevallen": [{"invoer": [n]} for n in (5, -3, 0, 1, -1, 1000)],
    },

    # ---------------- Les 6D ----------------
    "6d.timbits": {
        "oplossing": """
timbitsLeft = int(input()) # step 1: get the input
totalCost = 0              # step 2: initialize the total cost

# step 3: buy as many large boxes as you can
bigBoxes = int(timbitsLeft / 40)
totalCost = totalCost + bigBoxes * 6.19    # update the total price
timbitsLeft = timbitsLeft - 40 * bigBoxes  # calculate timbits still needed

if timbitsLeft >= 20:                # step 4, can we buy a medium box?
    totalCost = totalCost + 3.39
    timbitsLeft = timbitsLeft - 20
if timbitsLeft >= 10:                # step 5, can we buy a small box?
    totalCost = totalCost + 1.99
    timbitsLeft = timbitsLeft - 10

totalCost = totalCost + timbitsLeft * 0.20 # step 6
print(totalCost)                         # step 7
""",
        "gevallen": [{"invoer": [n]} for n in (45, 4, 10, 15, 20, 35, 39, 40, 456, 0)],
        "vergelijk": "getallen",
    },

    # ---------------- Les 7A ----------------
    "7a.firstlast": {
        "oplossing": "s = input()\nprint(s[1:len(s)-1])",
        "gevallen": [{"invoer": [w]} for w in ("Python", "ab", "Hallo wereld", "xyz")],
    },
    "7a.swap": {
        "oplossing": "s = input()\nprint(s[len(s)-1] + s[1:len(s)-1] + s[0])",
        "gevallen": [{"invoer": [w]} for w in ("kaart", "ab", "Python", "aa", "xyz")],
    },
    "7a.lowercase": {
        "oplossing": """
letter = input()
if letter == 'Z':
    print('A')
if letter != 'Z':
    print(chr(ord(letter) + 1))
""",
        "gevallen": [{"invoer": [c]} for c in ("A", "M", "Y", "Z", "Q")],
    },
    "7a.piglatin": {
        "oplossing": "woord = input()\nprint(woord[1:] + woord[0] + 'ay')",
        "gevallen": [{"invoer": [w]} for w in ("monkey", "word", "python", "a", "latin")],
    },
    "7a.namegame": {
        "oplossing": """
naam = input()
rest = naam[1:]
print(naam + ", " + naam + ", bo-b" + rest)
print("banana-fana fo-f" + rest)
print("fee-fi-mo-m" + rest)
print(naam + "!")
""",
        "gevallen": [{"invoer": [w]} for w in ("pearl", "katie", "fred", "shirley")],
    },

    # ---------------- Les 7B ----------------
    "7b.eggs": {
        "oplossing": "eieren = int(input())\nprint(eieren // 12)\nprint(eieren % 12)",
        "gevallen": [{"invoer": [n]} for n in (27, 12, 5, 0, 1000, 11)],
    },
    "7b.divisible": {
        "oplossing": """
a = int(input())
b = int(input())
if a % b == 0:
    print("deelbaar")
if a % b != 0:
    print("niet deelbaar")
""",
        "gevallen": [{"invoer": list(p)} for p in ((14, 3), (15, 3), (1, 1), (7, 14), (100, 25), (99, 2))],
    },
    "7b.pizza": {
        "oplossing": "import math\nr = float(input())\nprint(math.pi * r * r)",
        "gevallen": [{"invoer": [r]} for r in ("1", "10", "2.5", "0.5", "33.3")],
        "vergelijk": "getallen",
        "fout": ["r = float(input())\nprint(3.14 * r * r)"],
    },
    "7b.geometricmean": {
        "oplossing": "import math\na = float(input())\nb = float(input())\nprint(math.sqrt(a * b))",
        "gevallen": [{"invoer": list(p)} for p in (("5.0", "20.0"), ("2", "8"), ("1.5", "6"), ("3", "3"),
                                                   ("0.1", "1000"))],
        "vergelijk": "getallen",
    },
    "7b.skill": {
        "oplossing": "a = int(input())\nb = int(input())\nc = int(input())\nprint((a + b) * c)",
        "gevallen": [{"invoer": list(p)} for p in ((1, 2, 3), (10, -4, 7), (0, 0, 5), (123, 456, 789))],
        "fout": ["a = int(input())\nb = int(input())\nc = int(input())\nprint(a + b * c)"],
    },
    "7b.convert": {
        "oplossing": "print(float(input()) * 30.48)",
        "gevallen": [{"invoer": [x]} for x in ("0.5", "1", "6.2", "0", "1000")],
        "vergelijk": "getallen",
    },
    "7b.gravity": {
        "oplossing": """
import math
v = float(input())
t = (v - math.sqrt(v * v - 4 * (-4.9) * 11000)) / (2 * (-4.9))
print(t)
""",
        "gevallen": [{"invoer": [x]} for x in ("0", "10", "100.5", "250", "1")],
        "vergelijk": "getallen",
    },

    # ---------------- Les 7C ----------------
    "7c.countup": {
        "oplossing": """
getal = 1
while getal <= 10:
    print(getal)
    getal = getal + 1
print('Boem!')
""",
    },
    "7c.triangle": {
        "oplossing": """
n = int(input())
for i in range(1, n + 1):
    print('*' * i)
""",
        "gevallen": [{"invoer": [n]} for n in (3, 1, 5, 10)],
    },
    "7c.squares": {
        "oplossing": """
n = int(input())
counter = 1
while counter * counter < n:
    print(counter * counter)
    counter = counter + 1
""",
        "gevallen": [{"invoer": [n]} for n in (16, 17, 1, 2, 100, 1000)],
        "fout": ["n = int(input())\ncounter = 1\nwhile counter * counter <= n:\n"
                 "    print(counter * counter)\n    counter = counter + 1"],
    },
    "7c.skip": {
        "oplossing": """
counter = 0
while True:
  lineIn = input()
  if lineIn=='END':
    break
  if lineIn=='SKIP':
    continue
  counter = counter+1
  print('line', counter, '=', lineIn)
""",
        "gevallen": [
            {"invoer": ["eerste", "SKIP", "tweede", "END"]},
            {"invoer": ["SKIP", "SKIP", "a", "SKIP", "b", "c", "END", "d"]},
            {"invoer": ["END"]},
            {"invoer": ["skip", "SKIP ", "SKIP", "END"]},
        ],
    },
    "7c.factorize": {
        "oplossing": """
n = int(input())
for a in range(1, n + 1):
    for b in range(1, n + 1):
        if a * b == n:
            print(a, 'times', b, 'equals', n)
""",
        "gevallen": [{"invoer": [n]} for n in (10, 1, 7, 36, 64)],
    },

    # ---------------- Les 8 ----------------
    "8.adder": {
        "oplossing": """
S = input()
for position in range(0, len(S)):
    if S[position] == '+':
        plus = position
print(int(S[0:plus]) + int(S[plus+1:len(S)]))
""",
        "gevallen": [{"invoer": [s]} for s in ("5+12", "1+1", "123+4567", "1000000+1", "99+999")],
    },
    "8.substrings": {
        "oplossing": """
naald = input()
hooiberg = input()
aantal = 0
for i in range(0, len(hooiberg) - len(naald) + 1):
    if hooiberg[i:i+len(naald)] == naald:
        aantal = aantal + 1
print(aantal)
""",
        "gevallen": [{"invoer": list(p)} for p in (("ka", "katakana"), ("an", "trans-atlantische banaan"),
                                                   ("aa", "aaaa"), ("xyz", "abc"), ("banaan", "banaan"),
                                                   ("b", "a"))],
    },
    "8.pendulum": {
        "oplossing": """
import math
L = float(input())
A = float(input())
for T in range(0, 10):
    print(L * math.cos(A * math.cos(T * math.sqrt(9.8 / L))) - L * math.cos(A))
""",
        "gevallen": [{"invoer": list(p)} for p in (("53.1", "0.8"), ("1", "0.1"), ("10", "1.5"))],
        "vergelijk": "getallen",
    },
    "8.centering": {
        "oplossing": """
width = int(input())
while True:
    regel = input()
    if regel == "EINDE":
        break
    rechts = (width - len(regel)) // 2
    links = width - len(regel) - rechts
    print('.' * links + regel + '.' * rechts)
""",
        "gevallen": [
            {"invoer": ["13", "Tekst", "in", "het", "midden!", "EINDE"]},
            {"invoer": ["5", "abcde", "a", "", "EINDE"]},
            {"invoer": ["10", "EINDE"]},
            {"invoer": ["8", "Python", "is", "leuk", "EINDE"]},
        ],
    },
    "8.ending": {
        "oplossing": """
start = input()
D = int(input())
H = int(start[0:2])
M = int(start[3:5])
minuten = (M + D) % 60
uren = (H + (M + D) // 60) % 24
uitvoer = ''
if uren < 10:
    uitvoer = '0'
uitvoer = uitvoer + str(uren) + ':'
if minuten < 10:
    uitvoer = uitvoer + '0'
print(uitvoer + str(minuten))
""",
        "gevallen": [{"invoer": list(p)} for p in (("12:30", "47"), ("23:59", "13"), ("08:30", "0"),
                                                   ("14:07", "1440"), ("00:00", "5000"), ("09:55", "5"))],
    },
    "8.charmap": {
        "oplossing": """
for start in range(32, 128, 16):
    regel1 = 'chr: '
    regel2 = 'asc: '
    for code in range(start, start + 16):
        regel1 = regel1 + ' ' + chr(code) + '  '
        regel2 = regel2 + str(code) + ' ' * (4 - len(str(code)))
    print(regel1)
    print(regel2)
""",
    },

    # ---------------- Les 9 ----------------
    "9.abs": {
        "oplossing": """
x = int(input())
if x >= 0:
    print(x)
else:
    print(-x)
""",
        "gevallen": [{"invoer": [n]} for n in (5, -10, 0, -1, 12345)],
    },
    "9.ordinal": {
        "oplossing": """
x = int(input())
if x == 1:
    print('1st')
elif x == 2:
    print('2nd')
elif x == 3:
    print('3rd')
else:
    print(str(x) + 'th')
""",
        "gevallen": [{"invoer": [n]} for n in range(1, 10)],
    },
    "9.numberify": {
        "oplossing": """
letter = input()
if letter >= 'A' and letter <= 'Z':
    print(ord(letter) - ord('A') + 1)
else:
    print('niet toegestaan')
""",
        "gevallen": [{"invoer": [c]} for c in ("A", "Z", "M", "a", "5", "?", "[", "@")],
    },
}
