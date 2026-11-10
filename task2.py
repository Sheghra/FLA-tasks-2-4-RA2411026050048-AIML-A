import re

# ---------- 1. ATM PIN DFA ----------
def pin_dfa(s):
    state = 0
    for ch in s:
        if ch.isdigit() and ch in "0123456789" and state < 4:
            state += 1
        else:
            return False          # dead state
    return state == 4

# ---------- 2. Password DFA (product construction) ----------
SPECIAL = set("@#$%!&*")
def pw_dfa(s):
    n, U, L, D, S = 0, 0, 0, 0, 0
    for ch in s:
        if   'A' <= ch <= 'Z': U = 1
        elif 'a' <= ch <= 'z': L = 1
        elif '0' <= ch <= '9': D = 1
        elif ch in SPECIAL:    S = 1
        else: return False        # symbol not in alphabet -> dead
        n = min(n + 1, 8)
    return (n, U, L, D, S) == (8, 1, 1, 1, 1)

# ---------- 3. Email DFA (table-driven) ----------
T = {
 'S0': {'L':'S1','D':'S1'},
 'S1': {'L':'S1','D':'S1','.':'S2','_':'S2','@':'S3'},
 'S2': {'L':'S1','D':'S1'},
 'S3': {'L':'S4','D':'S4'},
 'S4': {'L':'S4','D':'S4','.':'S5'},
 'S5': {'L':'S6','D':'S8'},
 'S6': {'L':'S7','D':'S8','.':'S5'},
 'S7': {'L':'S7','D':'S8','.':'S5'},
 'S8': {'L':'S8','D':'S8','.':'S5'}}
def cls(c):
    if c.isascii() and c.isalpha(): return 'L'
    if c in "0123456789": return 'D'
    return c
def email_dfa(s):
    q = 'S0'
    for c in s:
        q = T[q].get(cls(c))
        if q is None: return False
    return q == 'S7'

tests = {
 pin_dfa: (["1234","0000","4821","0007","9087"], ["123","12345","12a4","","12 34"]),
 pw_dfa:  (["Srm@2026","Pa$$w0rdAI","Zx9!Zx9!","Fla#Auto1","Abcd#123x"],
           ["srm@2026","SRM@2026","Srm@abcd","Srm2026ab","Sr@2026"]),
 email_dfa: (["john.doe@srmist.edu.in","student_01@gmail.com","a@b.in",
              "AI2026@srm.ac.in","x.y_z@mail.org"],
             ["john@gmail","@gmail.com","john..doe@gmail.com","john@.com","john@gmail.c0m"])}
for f,(ok,bad) in tests.items():
    assert all(f(x) for x in ok) and not any(f(x) for x in bad), f.__name__
    print(f.__name__, "passed")