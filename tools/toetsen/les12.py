"""Toetsen voor les 12. Zie tools/harnas.py voor de betekenis van de velden."""

TOETSEN = {
    "12.alphabet": {
        "oplossing": """
for c in range(0, 26):
 print(chr(ord('A')+c), end='')
""",
        "fout": ["for c in range(0, 26):\n print(chr(ord('A')+c), end=' ')"],
    },
    "12.sevens": {
        "oplossing": """
for getal in range(17, 100, 10):
    print(getal)
""",
        "verplicht": [("for", "Gebruik een <code>for</code>-lus.")],
        "fout": ["for getal in range(7, 100, 10):\n    print(getal)"],
    },
}
