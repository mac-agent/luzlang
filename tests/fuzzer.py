"""
fuzzer.py — Grammar-based fuzzer for the Luz interpreter.

Generates random Luz programs and runs them through the interpreter.
A "crash" is any Python exception that is NOT a LuzError subclass —
those are interpreter bugs (unhandled edge cases).

Usage:
    python tests/fuzzer.py              # 500 iterations, prints crashes
    python tests/fuzzer.py 2000         # custom iteration count
    python tests/fuzzer.py 500 --seed 42  # reproducible run
"""

import random
import subprocess
import sys
import os
import tempfile
import time
import argparse
from pathlib import Path

# ── Root of the repo (so we can call `python main.py`) ────────────────────────
REPO = Path(__file__).parent.parent
CRASHES_DIR = REPO / "tests" / "crashes"
TIMEOUT = 3  # seconds per snippet

# ── Helpers ───────────────────────────────────────────────────────────────────

def rng():
    return random.random()

def pick(*choices):
    return random.choice(choices)

def maybe(prob=0.5):
    return random.random() < prob

# ── Literals ──────────────────────────────────────────────────────────────────

def gen_int():
    return str(random.choice([
        0, 1, -1, 2, -2, 10, -10, 100, 0, 0,  # weighted toward small/edge values
        random.randint(-1000, 1000),
    ]))

def gen_float():
    val = random.choice([0.0, 1.0, -1.0, 0.5, -0.5, random.uniform(-100, 100)])
    return str(val)

def gen_bool():
    return pick("true", "false")

def gen_null():
    return "null"

def gen_string():
    chars = random.choice([
        "",                    # empty string — common edge case
        "hello",
        "world",
        "abc",
        "123",
        " ",
        "hello world",
        "a" * random.randint(0, 20),
        pick("foo", "bar", "baz"),
    ])
    escaped = chars.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'

def gen_literal(depth):
    return pick(gen_int, gen_float, gen_bool, gen_null, gen_string)()

# ── Expressions ───────────────────────────────────────────────────────────────

VARS = ["x", "y", "z", "n", "s", "lst", "d", "result"]

def gen_var():
    return random.choice(VARS)

def gen_expr(depth=0):
    if depth >= 3:
        return pick(gen_int, gen_float, gen_bool, gen_string, gen_var)()

    kind = random.randint(0, 13)

    if kind == 0:
        return gen_literal(depth)
    elif kind == 1:
        return gen_var()
    elif kind == 2:
        # Binary arithmetic — include edge cases like ** with negative
        op = pick("+", "-", "*", "/", "%", "//", "**")
        return f"({gen_expr(depth+1)} {op} {gen_expr(depth+1)})"
    elif kind == 3:
        op = pick("==", "!=", "<", ">", "<=", ">=")
        return f"({gen_expr(depth+1)} {op} {gen_expr(depth+1)})"
    elif kind == 4:
        op = pick("and", "or")
        return f"({gen_expr(depth+1)} {op} {gen_expr(depth+1)})"
    elif kind == 5:
        op = pick("-", "not ")
        return f"({op}{gen_expr(depth+1)})"
    elif kind == 6:
        return gen_list_literal(depth)
    elif kind == 7:
        return gen_dict_literal(depth)
    elif kind == 8:
        return gen_builtin_call(depth)
    elif kind == 9:
        return gen_index_expr(depth)
    elif kind == 10:
        return gen_string_method(depth)
    elif kind == 11:
        return gen_list_method(depth)
    elif kind == 12:
        return gen_fstring(depth)
    else:
        return gen_in_expr(depth)

def gen_list_literal(depth=0):
    n = random.randint(0, 4)
    items = ", ".join(gen_expr(depth+1) for _ in range(n))
    return f"[{items}]"

def gen_dict_literal(depth=0):
    n = random.randint(0, 3)
    pairs = ", ".join(f'"{pick("a","b","c","x","y")}": {gen_expr(depth+1)}' for _ in range(n))
    return f"{{{pairs}}}"

def gen_index_expr(depth=0):
    """Generate list/string indexing — common source of IndexFault crashes."""
    obj = pick(gen_list_literal(depth), gen_string())
    idx = pick("0", "-1", "1", "-2", "100", "-100", gen_int())
    return f"({obj})[{idx}]"

def gen_string_method(depth=0):
    s = gen_string()
    method = pick(
        f'{s}.uppercase()',
        f'{s}.lowercase()',
        f'{s}.trim()',
        f'{s}.split(" ")',
        f'{s}.swap("a", "b")',
        # Intentionally call nonexistent methods to probe error paths
        f'{s}.find("x")',
        f'{s}.count("a")',
        f'{s}.len()',        # not a real string method — should raise
        f'{s}.reverse()',   # not a real string method — should raise
    )
    return method

def gen_list_method(depth=0):
    lst = gen_list_literal(depth)
    method = pick(
        f'{lst}.len()',
        f'{lst}.append({gen_expr(depth+1)})',
        f'{lst}.pop()',
        f'{lst}.pop(0)',
        f'{lst}.pop(100)',  # out of bounds
        f'{lst}.contains({gen_expr(depth+1)})',
        f'{lst}.join(", ")',
        f'{lst}.reverse()',   # not wired yet — should raise
        f'{lst}.index({gen_expr(depth+1)})',  # not wired yet
        f'{lst}.any()',
        f'{lst}.all()',
    )
    return method

def gen_dict_method(depth=0):
    d = gen_dict_literal(depth)
    method = pick(
        f'{d}.keys()',
        f'{d}.values()',
        f'{d}.len()',
        f'{d}.contains("a")',
        f'{d}.remove("a")',
    )
    return method

def gen_fstring(depth=0):
    val = gen_expr(depth+1)
    return f'f"result: {{{val}}}"'

def gen_lambda(depth=0):
    param = pick("x", "a", "n")
    body = gen_expr(depth+1)
    return f"fn({param}) => {body}"

def gen_comprehension(depth=0):
    var = pick("x", "i", "n")
    lst = gen_list_literal(depth)
    expr = gen_expr(depth+1)
    return f"[{expr} for {var} in {lst}]"

def gen_in_expr(depth=0):
    """Test the `in` operator on various types."""
    needle = gen_expr(depth+1)
    haystack = pick(gen_list_literal(depth), gen_string(), gen_dict_literal(depth))
    return f"({needle} in {haystack})"

def gen_builtin_call(depth=0):
    name = random.choice([
        ("write",    lambda: gen_expr(depth+1)),
        ("len",      lambda: pick(gen_list_literal(depth), gen_string(), gen_dict_literal(depth))),
        ("typeof",   lambda: gen_expr(depth+1)),
        ("to_int",   lambda: gen_expr(depth+1)),
        ("to_float", lambda: gen_expr(depth+1)),
        ("to_str",   lambda: gen_expr(depth+1)),
        ("to_bool",  lambda: gen_expr(depth+1)),
        ("abs",      lambda: gen_expr(depth+1)),
        ("sqrt",     lambda: gen_expr(depth+1)),
        ("min",      lambda: f"{gen_expr(depth+1)}, {gen_expr(depth+1)}"),
        ("max",      lambda: f"{gen_expr(depth+1)}, {gen_expr(depth+1)}"),
        ("append",   lambda: f"{gen_list_literal(depth)}, {gen_expr(depth+1)}"),
        ("pop",      lambda: pick(gen_list_literal(depth), f"{gen_list_literal(depth)}, {gen_int()}")),
        ("reverse",  lambda: pick(gen_list_literal(depth), gen_string())),
        ("index",    lambda: f"{gen_list_literal(depth)}, {gen_expr(depth+1)}"),
        ("insert",   lambda: f"{gen_list_literal(depth)}, {gen_int()}, {gen_expr(depth+1)}"),
        ("any",      lambda: gen_list_literal(depth)),
        ("all",      lambda: gen_list_literal(depth)),
        ("sum",      lambda: gen_list_literal(depth)),
        ("keys",     lambda: gen_dict_literal(depth)),
        ("values",   lambda: gen_dict_literal(depth)),
        ("remove",   lambda: f'{gen_dict_literal(depth)}, {gen_string()}'),
        ("uppercase",lambda: gen_expr(depth+1)),
        ("lowercase",lambda: gen_expr(depth+1)),
        ("trim",     lambda: gen_expr(depth+1)),
        ("swap",     lambda: f'{gen_expr(depth+1)}, {gen_string()}, {gen_string()}'),
        ("split",    lambda: pick(f'{gen_string()}', f'{gen_string()}, {gen_string()}')),
        ("find",     lambda: f'{gen_expr(depth+1)}, {gen_expr(depth+1)}'),
        ("count",    lambda: f'{gen_expr(depth+1)}, {gen_expr(depth+1)}'),
        ("begins",   lambda: f'{gen_expr(depth+1)}, {gen_expr(depth+1)}'),
        ("ends",     lambda: f'{gen_expr(depth+1)}, {gen_expr(depth+1)}'),
        ("contains", lambda: f'{gen_expr(depth+1)}, {gen_expr(depth+1)}'),
        ("floor",    lambda: gen_expr(depth+1)),
        ("ceil",     lambda: gen_expr(depth+1)),
        ("round",    lambda: pick(gen_expr(depth+1), f"{gen_expr(depth+1)}, {gen_int()}")),
        ("clamp",    lambda: f"{gen_expr(depth+1)}, {gen_expr(depth+1)}, {gen_expr(depth+1)}"),
        ("odd",      lambda: gen_expr(depth+1)),
        ("even",     lambda: gen_expr(depth+1)),
        ("pow",      lambda: f"{gen_expr(depth+1)}, {gen_expr(depth+1)}"),
    ])
    fn, args_fn = name
    return f"{fn}({args_fn()})"

# ── Statements ────────────────────────────────────────────────────────────────

def gen_assign():
    var = random.choice(VARS)
    return f"{var} = {gen_expr()}"

def gen_write():
    return f"write({gen_expr()})"

def gen_if(depth=0):
    cond = gen_expr()
    body = gen_block(depth+1)
    if maybe(0.4):
        else_body = gen_block(depth+1)
        return f"if {cond} {{\n{body}\n}} else {{\n{else_body}\n}}"
    return f"if {cond} {{\n{body}\n}}"

def gen_while(depth=0):
    # Use a counter to avoid infinite loops
    var = random.choice(["i", "j", "k"])
    limit = random.randint(1, 5)
    return (
        f"{var} = 0\n"
        f"while {var} < {limit} {{\n"
        f"    {var} = {var} + 1\n"
        f"}}"
    )

def gen_for(depth=0):
    var = pick("i", "j", "k", "n")
    start = random.randint(0, 3)
    end = random.randint(start, start + 5)
    body = gen_block(depth+1)
    return f"for {var} = {start} to {end} {{\n{body}\n}}"

def gen_function(depth=0):
    name = pick("foo", "bar", "baz", "helper", "calc")
    params = random.sample(["a", "b", "c", "x"], random.randint(0, 2))
    body = gen_block(depth+1)
    ret = gen_expr()
    return (
        f"function {name}({', '.join(params)}) {{\n"
        f"{body}\n"
        f"    return {ret}\n"
        f"}}"
    )

def gen_attempt(depth=0):
    body = gen_block(depth+1)
    rescue = gen_block(depth+1)
    return f"attempt {{\n{body}\n}} rescue {{\n{rescue}\n}}"

def gen_statement(depth=0):
    if depth >= 2:
        return random.choice([gen_assign, gen_write])()

    kind = random.randint(0, 7)
    if kind == 0:
        return gen_assign()
    elif kind == 1:
        return gen_write()
    elif kind == 2:
        return gen_if(depth)
    elif kind == 3:
        return gen_while(depth)
    elif kind == 4:
        return gen_for(depth)
    elif kind == 5:
        return gen_function(depth)
    elif kind == 6:
        return gen_attempt(depth)
    else:
        return gen_builtin_call()

def gen_block(depth=0, n=None):
    count = n or random.randint(1, 3)
    lines = []
    for _ in range(count):
        stmt = gen_statement(depth)
        # Indent each line
        lines.append("\n".join("    " + l for l in stmt.splitlines()))
    return "\n".join(lines)

def gen_edge_case():
    """Targeted snippets that probe known-dangerous areas."""
    return random.choice([
        # POW edge cases
        f"write(0 ** {pick('-1', '-2', '-0.5', gen_int())})",
        f"write({pick('-1','-2','-3','-4')} ** {pick('0.5','0.25','1.5','0.1')})",
        # IDIV / MOD with non-numeric strings
        f"write({gen_string()} // {gen_int()})",
        f"write({gen_string()} // {gen_string()})",
        # round with non-int digits
        f"write(round({gen_expr()}, {gen_string()}))",
        f"write(round({gen_expr()}, {gen_float()}))",
        # `in` with dict — should work but currently raises TypeClashFault
        f'write({gen_string()} in {gen_dict_literal()})',
        # Calling non-callables
        f"x = {gen_literal(0)}\nwrite(x())",
        # Index with float
        f"write([1,2,3][{gen_float()}])",
        # Arithmetic on complex result
        f"x = {pick('-1','-4','-9')} ** 0.5\nwrite(x + 1)",
        # Chained method on wrong type
        f"write({gen_int()}.uppercase())",
        f"write({gen_int()}.len())",
        # Large negative list index
        f"write([1,2,3][-{random.randint(4, 100)}])",
        # Empty list operations
        "write(reverse([]))",
        "write(pop([]))",
        "write(index([], 99))",
        # String * negative
        f'write("abc" * {pick("-1", "-5", "0")})',
        # Nested format string with null
        'x = null\nwrite(f"val: {x}")',
    ])

def gen_program():
    # 30% chance of a targeted edge-case program
    if maybe(0.3):
        return gen_edge_case()
    n = random.randint(1, 6)
    stmts = []
    for _ in range(n):
        stmts.append(gen_statement(0))
    return "\n".join(stmts)

# ── Runner ────────────────────────────────────────────────────────────────────

LUZ_ERRORS = {
    "SyntaxFault", "ParseFault", "ExpressionFault", "OperatorFault",
    "UnexpectedTokenFault", "InvalidTokenFault", "StructureFault",
    "UnexpectedEOFault", "SemanticFault", "TypeClashFault",
    "TypeViolationFault", "CastFault", "UndefinedSymbolFault",
    "DuplicateSymbolFault", "ScopeFault", "FunctionNotFoundFault",
    "ArgumentFault", "ArityFault", "InvalidUsageFault",
    "AttributeNotFoundFault", "InheritanceFault", "FlowControlFault",
    "ReturnFault", "LoopFault", "RuntimeFault", "ExecutionFault",
    "InternalFault", "IllegalOperationFault", "NumericFault",
    "ZeroDivisionFault", "OverflowFault", "MemoryAccessFault",
    "IndexFault", "ModuleNotFoundFault", "ImportFault", "UserFault",
    "LuzError",
}

def is_interpreter_bug(stdout: str, stderr: str) -> tuple[bool, str]:
    """
    Return (is_bug, description).

    main.py catches ALL Python exceptions with `except Exception` and prints them
    to stdout in the format: "[Line N] ExceptionName: message" (no traceback).

    A bug is any exception printed to stdout whose type is NOT a known LuzError.
    We also catch raw Python tracebacks in stderr (defensive).
    """
    # Check for raw Python traceback in stderr (shouldn't normally happen)
    if "Traceback (most recent call last)" in stderr:
        last = stderr.strip().splitlines()[-1]
        is_luz = any(last.startswith(e + ":") for e in LUZ_ERRORS)
        if not is_luz:
            return True, last

    # Check stdout for a Python exception masquerading as a Luz error
    if stdout.strip():
        last = stdout.strip().splitlines()[-1]
        # Strip the "[Line N, Col M] " prefix if present
        import re
        cleaned = re.sub(r'^\[Line \d+(, Col \d+)?\]\s*', '', last)
        # Extract the exception type name
        m = re.match(r'^([A-Za-z][A-Za-z0-9_]*Error|[A-Za-z][A-Za-z0-9_]*Warning|ValueError|TypeError|AttributeError|ZeroDivisionError|OverflowError|RecursionError|KeyError|IndexError|RuntimeError|NotImplementedError|NameError):', cleaned)
        if m:
            exc_type = m.group(1)
            return True, f"{exc_type}: {cleaned[len(exc_type)+1:].strip()}"

    return False, ""

def run_snippet(code: str) -> tuple[str, str, int | None]:
    """Run a Luz snippet. Returns (stdout, stderr, returncode)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.luz', delete=False, encoding='utf-8') as f:
        f.write(code)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, str(REPO / "main.py"), path],
            capture_output=True, text=True, timeout=TIMEOUT,
            cwd=str(REPO),
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", None
    finally:
        os.unlink(path)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Luz fuzzer")
    parser.add_argument("iterations", nargs="?", type=int, default=500)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    CRASHES_DIR.mkdir(parents=True, exist_ok=True)

    crashes = []
    timeouts = 0
    total = args.iterations

    print(f"Fuzzing Luz with {total} random programs (seed={args.seed})...")
    print(f"Crashes will be saved to {CRASHES_DIR}/\n")

    start = time.time()

    for i in range(total):
        code = gen_program()
        stdout, stderr, returncode = run_snippet(code)

        if stderr == "TIMEOUT":
            timeouts += 1
            crash_file = CRASHES_DIR / f"timeout_{i:04d}.luz"
            crash_file.write_text(code, encoding='utf-8')
            print(f"[{i+1}/{total}] TIMEOUT — saved to {crash_file.name}")

        else:
            bug, description = is_interpreter_bug(stdout, stderr)
            if bug:
                crash_file = CRASHES_DIR / f"crash_{i:04d}.luz"
                crash_file.write_text(code, encoding='utf-8')

                report_file = CRASHES_DIR / f"crash_{i:04d}.txt"
                report_file.write_text(
                    f"=== CODE ===\n{code}\n\n=== STDOUT ===\n{stdout}\n=== STDERR ===\n{stderr}",
                    encoding='utf-8'
                )

                crashes.append((crash_file.name, description))
                print(f"[{i+1}/{total}] BUG — {description[:80]}")
                print(f"           saved to {crash_file.name}")

        if (i + 1) % 100 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"[{i+1}/{total}] {rate:.0f} prog/s — {len(crashes)} crashes, {timeouts} timeouts so far")

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"Done. {total} programs in {elapsed:.1f}s ({total/elapsed:.0f} prog/s)")
    print(f"Crashes: {len(crashes)}")
    print(f"Timeouts: {timeouts}")

    if crashes:
        print(f"\nUnique crash types:")
        seen = set()
        for fname, last_line in crashes:
            exc_type = last_line.split(":")[0].strip()
            if exc_type not in seen:
                seen.add(exc_type)
                print(f"  {exc_type}")
        print(f"\nSee {CRASHES_DIR}/ for full details.")


if __name__ == "__main__":
    main()
