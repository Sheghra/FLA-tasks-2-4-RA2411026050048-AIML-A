"""
Task 4 demo: infinite-loop detection, theory vs. practice.
NOTE: Nothing here decides the halting problem in general.
Each tool works only for a restricted case, or answers UNKNOWN.
"""

HALTS, LOOPS, UNKNOWN = "HALTS", "INFINITE LOOP", "UNKNOWN"

# ---------------------------------------------------------------
# 1. Finite-state programs: exact and decidable (hash-set method)
#    A deterministic program with finitely many states must either
#    halt or repeat a state. If a state repeats, it loops forever.
# ---------------------------------------------------------------
def halts_finite(step, init, is_halt, limit=10**6):
    seen, s = set(), init
    while True:
        if is_halt(s):
            return HALTS
        if s in seen:
            return LOOPS + " (state repeated)"
        seen.add(s)
        if len(seen) > limit:
            return UNKNOWN + " (budget exceeded)"
        s = step(s)

# ---------------------------------------------------------------
# 2. Same idea with O(1) memory: Floyd's tortoise and hare
# ---------------------------------------------------------------
def halts_floyd(step, init, is_halt, limit=10**6):
    t = h = init
    for _ in range(limit):
        if is_halt(h): return HALTS
        h = step(h)
        if is_halt(h): return HALTS
        h = step(h)
        t = step(t)
        if t == h:
            return LOOPS + " (cycle found by Floyd)"
    return UNKNOWN + " (budget exceeded)"

# ---------------------------------------------------------------
# 3. Bounded halting ("fuel"): decidable, but only "halts within k"
# ---------------------------------------------------------------
def run_with_fuel(step, init, is_halt, fuel=10_000):
    s = init
    for i in range(fuel):
        if is_halt(s):
            return f"{HALTS} (after {i} steps)"
        s = step(s)
    return UNKNOWN + f" (not finished in {fuel} steps)"

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

# ---------------------------------------------------------------
# 4. Turing-machine simulator with a step bound
#    This is a recogniser with fuel. It gives HALTS or UNKNOWN,
#    never a verified "loops forever".
#    delta[(state, symbol)] = (new_state, write_symbol, 'L'|'R')
# ---------------------------------------------------------------
def run_tm(delta, start, accept, reject, tape_str, max_steps=1000):
    tape = dict(enumerate(tape_str))
    head, state = 0, start
    for step in range(max_steps):
        if state in (accept, reject):
            return (HALTS, state, step)
        sym = tape.get(head, '_')
        if (state, sym) not in delta:          # no move: implicit reject
            return (HALTS, reject, step)
        state, tape[head], d = delta[(state, sym)]
        head += 1 if d == 'R' else -1
    return (UNKNOWN, state, max_steps)

# TM that flips 0<->1 and accepts at the first blank (always halts)
FLIP = {('q0', '0'): ('q0', '1', 'R'),
        ('q0', '1'): ('q0', '0', 'R'),
        ('q0', '_'): ('qa', '_', 'R')}

# TM that moves right forever (never halts)
LOOP = {('q0', '0'): ('q0', '0', 'R'),
        ('q0', '1'): ('q0', '1', 'R'),
        ('q0', '_'): ('q0', '_', 'R')}

# ---------------------------------------------------------------
# 5. Restricted loop class: while x > 0: x = x + c  (integers)
#    Termination is decidable for this class, with a proof each way:
#    a ranking function, or a recurrent set.
# ---------------------------------------------------------------
def analyze_linear_loop(x0, c):
    if x0 <= 0:
        return "TERMINATES (guard false at start)"
    if c < 0:
        return "TERMINATES (ranking function f(x)=x strictly decreases, bounded below by 0)"
    return "NON-TERMINATING (recurrent set {x>0}: x never decreases, guard stays true)"

# ---------------------------------------------------------------
# 6. Diagonal argument, made concrete
#    Any claimed halting decider can be defeated by D.
# ---------------------------------------------------------------
def make_D(candidate_halts):
    def D(p):
        if candidate_halts(p, p):
            while True:        # candidate said "halts", so D loops
                pass
        return "D halted"      # candidate said "loops", so D halts
    return D

# ---------------------------------------------------------------
# Demo
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("== 1. Finite-state, exact ==")
    wrap  = lambda s: (s + 1) % 256        # 8-bit counter, never reaches 300
    count = lambda s: s - 1
    print("8-bit counter  :", halts_finite(wrap, 0, lambda s: s == 300))
    print("countdown(10)  :", halts_finite(count, 10, lambda s: s == 0))

    print("\n== 2. Floyd, O(1) memory ==")
    print("8-bit counter  :", halts_floyd(wrap, 0, lambda s: s == 300))
    print("countdown(10)  :", halts_floyd(count, 10, lambda s: s == 0))

    print("\n== 3. Fuel-bounded: Collatz ==")
    print("n=27, fuel=10000:", run_with_fuel(collatz_step, 27, lambda n: n == 1, 10_000))
    print("n=27, fuel=50   :", run_with_fuel(collatz_step, 27, lambda n: n == 1, 50))
    print("(UNKNOWN does not mean it loops; it only means we ran out of fuel.)")

    print("\n== 4. Turing machine with step bound ==")
    print("FLIP on '0110':", run_tm(FLIP, 'q0', 'qa', 'qr', "0110"))
    print("LOOP on '0110':", run_tm(LOOP, 'q0', 'qa', 'qr', "0110", 1000))

    print("\n== 5. Restricted loop class ==")
    for x0, c in [(10, -3), (10, 0), (10, 2), (-5, 1)]:
        print(f"while x>0: x+={c:<2} (x0={x0:<3}) ->", analyze_linear_loop(x0, c))

    print("\n== 6. Diagonal argument ==")
    always_no = lambda p, x: False          # claims "nothing halts"
    D = make_D(always_no)
    print("Candidate says D(D) loops. Actual result of D(D):", D(D))
    print("-> candidate is wrong.")
    print("Candidate 'always yes' says D(D) halts, but then D enters its")
    print("infinite loop, so it is wrong too (not run here, it would hang).")
    print("Every candidate fails on its own D, so no decider exists.")