"""Toetsen voor les 10 t/m 14. Zie tools/harnas.py voor de betekenis van de velden."""


def aanroepen(*exprs):
    return [{"aanroep": e} for e in exprs]


HYPOTENUSE = """
import math
def hypotenuse(a, b):
    return math.sqrt(a * a + b * b)
"""

DISTANCE2D = HYPOTENUSE + """
def distance2D(x1, y1, x2, y2):
    return hypotenuse(x2 - x1, y2 - y1)
"""

LOWERCHAR = """
def lowerChar(char):
    if char >= 'A' and char <= 'Z':
        return chr(ord(char) - ord('A') + ord('a'))
    return char
"""

TOETSEN = {
    # ---------------- Les 10 ----------------
    "10.cube": {
        "oplossing": "def derdeMacht(n):\n    return n * n * n",
        "gevallen": aanroepen("derdeMacht(3)", "derdeMacht(0)", "derdeMacht(-2)", "derdeMacht(10)",
                              "derdeMacht(1.5)"),
        "fout": ["def derdeMacht(n):\n    print(n * n * n)"],
    },
    "10.rectangle": {
        "oplossing": "def omtrek(breedte, hoogte):\n    return 2 * (breedte + hoogte)",
        "gevallen": aanroepen("omtrek(3, 4)", "omtrek(10, 10)", "omtrek(0, 7)", "omtrek(2.5, 1)",
                              "omtrek(1, 100)"),
        "fout": ["def omtrek(breedte, hoogte):\n    return breedte * hoogte"],
    },

    # ---------------- Les 11A ----------------
    "11a.lowerchar": {
        "oplossing": LOWERCHAR,
        "gevallen": aanroepen("lowerChar('A')", "lowerChar('Z')", "lowerChar('M')", "lowerChar('q')",
                              "lowerChar('!')", "lowerChar('5')", "lowerChar(' ')", "lowerChar('[')",
                              "lowerChar('@')"),
        "verboden": [(".lower", "Gebruik <code>lower()</code> niet; schrijf de omzetting zelf.")],
    },
    "11a.lowerstring": {
        "oplossing": LOWERCHAR + """
def lowerString(string):
    result = ""
    for i in range(0, len(string)):
        result = result + lowerChar(string[i])
    return result
""",
        "gevallen": aanroepen("lowerString('Hallo Wereld!')", "lowerString('')", "lowerString('ABC xyz 123')",
                              "lowerString('Python@CS-Circles')"),
        "verboden": [(".lower", "Gebruik <code>lower()</code> niet; gebruik je eigen functie "
                                "<code>lowerChar</code>.")],
    },

    # ---------------- Les 11C ----------------
    "11c.hypotenuse": {
        "oplossing": HYPOTENUSE,
        "gevallen": aanroepen("hypotenuse(3, 4)", "hypotenuse(5, 12)", "hypotenuse(1, 1)",
                              "hypotenuse(0, 7)", "hypotenuse(2.5, 6)"),
        "vergelijk": "getallen",
    },
    "11c.rightperimeter": {
        "vergelijk": "getallen",
        "oplossing": HYPOTENUSE + """
def rightTrianglePerimeter(a, b):
    return a + b + hypotenuse(a, b)
""",
        "gevallen": aanroepen("rightTrianglePerimeter(3, 4)", "rightTrianglePerimeter(5, 12)",
                              "rightTrianglePerimeter(1, 1)", "rightTrianglePerimeter(8, 15)"),
    },
    "11c.distance": {
        "vergelijk": "getallen",
        "voorcode": HYPOTENUSE,
        "oplossing": """
def distance2D(x1, y1, x2, y2):
    return hypotenuse(x2 - x1, y2 - y1)
""",
        "gevallen": [{"voorcode": HYPOTENUSE, "aanroep": e} for e in (
            "distance2D(0, 0, 3, 4)", "distance2D(1, 2, 4, 6)", "distance2D(5, 5, 5, 5)",
            "distance2D(-1, -1, 2, 3)", "distance2D(0.5, 0, 0, 1.2)")],
    },
    "11c.perimeter": {
        "vergelijk": "getallen",
        "voorcode": DISTANCE2D,
        "oplossing": """
def trianglePerimeter(xA, yA, xB, yB, xC, yC):
    return distance2D(xA, yA, xB, yB) + distance2D(xB, yB, xC, yC) + distance2D(xC, yC, xA, yA)
""",
        "gevallen": [{"voorcode": DISTANCE2D, "aanroep": e} for e in (
            "trianglePerimeter(0, 0, 3, 0, 0, 4)", "trianglePerimeter(1, 1, 1, 1, 1, 1)",
            "trianglePerimeter(-2, 0, 2, 0, 0, 5)", "trianglePerimeter(0, 0, 1, 0, 0.5, 0.866)")],
    },

    # ---------------- Les 13 ----------------
    "13.middle": {
        "oplossing": "def middle(L):\n    return L[len(L) // 2]",
        "gevallen": aanroepen("middle([8, 0, 100, 12, 1])", "middle([7])", "middle(['a', 'b', 'c'])",
                              "middle([1, 2, 3, 4, 5, 6, 7, 8, 9])"),
    },
    "13.natural": {
        "oplossing": """
def naturalNumbers(n):
    result = []
    for i in range(1, n + 1):
        result = result + [i]
    return result
""",
        "gevallen": aanroepen("naturalNumbers(5)", "naturalNumbers(1)", "naturalNumbers(10)"),
    },
    "13.palindrome": {
        "oplossing": """
def isPalindrome(S):
    for i in range(0, len(S)):
        if S[i] != S[len(S) - 1 - i]:
            return False
    return True
""",
        "gevallen": aanroepen("isPalindrome('racecar')", "isPalindrome('racecars')", "isPalindrome('a')",
                              "isPalindrome('')", "isPalindrome('abba')", "isPalindrome('abca')",
                              "isPalindrome('lepel')", "isPalindrome('Lepel')"),
    },
    "13.product": {
        "oplossing": """
def prod(L):
    result = 1
    for i in range(0, len(L)):
        result = result * L[i]
    return result
""",
        "gevallen": aanroepen("prod([2, 3, 4])", "prod([])", "prod([5])", "prod([-1, 2, -3, 0.5])",
                              "prod([10, 0, 7])"),
    },
    "13.foreach": {
        "oplossing": """
def prod(L):
    result = 1
    for x in L:
        result = result * x
    return result
""",
        "gevallen": aanroepen("prod([2, 3, 4])", "prod([])", "prod([5])", "prod([-1, 2, -3, 0.5])",
                              "prod([10, 0, 7])"),
        "verplicht": [(" in ", "Gebruik een lus van de vorm <code>for x in L:</code>.")],
    },
    "13.la-mode": {
        # regels: 0 if frequency[i]==max(frequency):  1 return i  2 for i in L:  3 for i in range(0, 10):
        #         4 def mode(L):  5 frequency[i] = frequency[i] + 1  6 frequency = [0]*10
        "volgorde": [4, 6, 2, 5, 3, 0, 1],
    },

    # ---------------- Les 14 ----------------
    "14.replace": {
        "oplossing": """
def replace(list, X, Y):
    while X in list:
        i = list.index(X)
        list.pop(i)
        list.insert(i, Y)
""",
        "gevallen": [
            {"voorcode": "L = [3, 1, 4, 1, 5, 9]", "aanroep": "(replace(L, 1, 7), L)"},
            {"voorcode": "L = [3, 1, 4, 1, 5, 9]", "aanroep": "(replace(L, 2, 7), L)"},
            {"voorcode": "L = []", "aanroep": "(replace(L, 1, 2), L)"},
            {"voorcode": "L = ['a', 'b', 'a', 'a']", "aanroep": "(replace(L, 'a', 'c'), L)"},
            {"voorcode": "L = [1, 1, 1]", "aanroep": "(replace(L, 1, 0), L)"},
        ],
        "verboden": [("[", "Je mag geen <code>[]</code> gebruiken.")],
        "fout": ["def replace(list, X, Y):\n    return list"],
    },
    "14.postal": {
        "oplossing": """
def postalValidate(S):
    S = S.replace(' ', '')
    if len(S) != 6:
        return False
    for i in range(0, 6):
        if i % 2 == 0 and not S[i].isalpha():
            return False
        if i % 2 == 1 and not S[i].isdigit():
            return False
    return S.upper()
""",
        "gevallen": aanroepen("postalValidate('N2L 3G1')", "postalValidate('n2l3g1')",
                              "postalValidate(' n 2 l 3 g 1 ')", "postalValidate('N2L 3G')",
                              "postalValidate('N2L 3G12')", "postalValidate('22L 3G1')",
                              "postalValidate('NNL 3G1')", "postalValidate('')", "postalValidate('a1b2c3')",
                              "postalValidate('M5W-1E6')"),
    },
}
