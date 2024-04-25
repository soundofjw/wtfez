"""
A 3D representation of the TOME (haikus) in Fez.
"""

TOME_3D = [
    [
        ["F", "T", "T", "O", "H", "D", "I", ""],
        ["F", "N", "Y", "E", "O", "R", "C", ""],
        ["I", "S", "P", "C", "T", "G", "O", ""],
        ["L", "R", "S", "N", "T", "T", "", ""],
        ["R", "H", "L", "N", "O", "A", "", ""],
        ["E", "T", "H", "A", "N", "E", "", ""],
        ["W", "N", "E", "A", "I", "E", "", ""],
        ["O", "E", "N", "C", "R", "P", "", ""],
    ],
    [
        ["O", "E", "O", "U", "X", "E", "E", ""],
        ["O", "O", "S", "P", "T", "T", "W", ""],
        ["P", "A", "N", "I", "F", "G", "S", ""],
        ["V", "N", "O", "S", "A", "E", "", ""],
        ["O", "N", "A", "B", "T", "L", "", ""],
        ["A", "E", "A", "S", "O", "N", "", ""],
        ["T", "I", "M", "E", "A", "N", "", ""],
        ["E", "R", "M", "I", "A", "C", "", ""],
    ],
    [
        ["O", "I", "O", "L", "H", "U", "F", ""],
        ["H", "D", "I", "R", "E", "N", "E", ""],
        ["S", "E", "H", "E", "U", "T", "T", ""],
        ["S", "O", "E", "N", "E", "T", "", ""],
        ["R", "G", "E", "T", "E", "F", "", ""],
        ["T", "O", "R", "H", "O", "S", "", ""],
        ["H", "T", "T", "D", "A", "T", "", ""],
        ["U", "V", "I", "N", "O", "O", "", ""],
    ],
    [
        ["T", "D", "R", "A", "D", "D", "P", ""],
        ["R", "O", "E", "P", "I", "I", "E", ""],
        ["I", "N", "P", "H", "B", "T", "N", ""],
        ["T", "B", "S", "E", "F", "R", "", ""],
        ["E", "V", "I", "L", "O", "I", "", ""],
        ["R", "D", "D", "R", "I", "A", "", ""],
        ["N", "D", "Y", "R", "T", "E", "", ""],
        ["I", "L", "E", "H", "E", "T", "", ""],
    ],
    [
        ["R", "H", "I", "B", "E", "E", "D", ""],
        ["N", "F", "E", "W", "N", "S", "E", ""],
        ["M", "P", "E", "T", "Y", "A", "E", ""],
        ["E", "O", "T", "G", "N", "H", "", ""],
        ["S", "I", "L", "S", "D", "L", "", ""],
        ["F", "H", "S", "Y", "T", "A", "", ""],
        ["A", "G", "O", "N", "N", "A", "", ""],
        ["V", "P", "E", "T", "N", "A", "", ""],
    ],
    [
        ["M", "H", "N", "I", "A", "P", "O", ""],
        ["W", "L", "W", "E", "H", "A", "H", ""],
        ["O", "C", "S", "V", "O", "A", "I", ""],
        ["I", "T", "T", "U", "M", "S", "", ""],
        ["U", "D", "T", "U", "H", "O", "", ""],
        ["C", "G", "C", "T", "F", "D", "", ""],
        ["C", "F", "E", "W", "P", "D", "", ""],
        ["R", "E", "P", "O", "C", "E", "", ""],
    ],
    [
        ["U", "D", "U", "D", "E", "N", "S", ""],
        ["E", "S", "D", "S", "S", "D", "R", ""],
        ["S", "I", "A", "T", "R", "E", "E", ""],
        ["I", "F", "S", "S", "O", "A", "", ""],
        ["B", "I", "W", "A", "P", "T", "", ""],
        ["O", "L", "E", "E", "R", "P", "", ""],
        ["I", "A", "R", "I", "T", "H", "", ""],
        ["S", "E", "R", "T", "D", "U", "", ""],
    ],
    [
        ["O", "E", "E", "N", "R", "E", "A", ""],
        ["E", "F", "O", "E", "X", "N", "D", ""],
        ["B", "F", "E", "I", "I", "O", "D", ""],
        ["O", "E", "E", "E", "G", "S", "", ""],
        ["N", "E", "T", "W", "I", "M", "", ""],
        ["S", "E", "G", "E", "G", "C", "", ""],
        ["G", "E", "A", "E", "E", "S", "", ""],
        ["N", "A", "T", "E", "A", "S", "", ""],
    ],
]

HAIKU_LINES = (
    "FROM OUT OF NOWHERE",
    "IMPOSSIBLE VISITORS",
    "OUR BENEFACTORS",
    "WATCHING OVER US",
    "IN THE HIDDEN FOLDS OF SPACE",
    "IN FRONT OF BEHIND",
    "GIVE THE GOLDEN GIFT",
    "A DEEP REVELATION",
    "OUR EYES WIDE OPEN",
    "SHAPES TO TESSELLATE",
    "WITH SACRED GEOMETRY",
    "AN EMPIRE TO BUILD",
    "A NEW PERSPECTIVE",
    "THINGS UNSEENS BUT ALWAYS THERE",
    "A NEW DIRECTION",
    "THE HEXAHEDRON",
    "THE SIXTY FOUR BIT NAME OF GOD",
    "THE POINT OF ORIGIN",
    "A PATTERN A CODE",
    "A DEEP UNDERSTANDING",
    "A GATE TO THE STARS",
    "ALL OF TIME AND SPACE",
    "AND THE SPACE OUTSIDE OF SPACE",
    "WHERE DOES IT END",
)

if __name__ == "__main__":
    print(
        f"""! Beautiful Haikus

What is this strange error on the 13th line?
  13: `{HAIKU_LINES[13][0:14]}`

It is in the 13th position: `{HAIKU_LINES[13][13]}`

This position is along a 2D diagonal.

What else along a 3D diagonal?
  `{"".join([TOME_3D[c][c][7-c] for c in range(8)])}`

wtfez does that mean?
"""
    )
