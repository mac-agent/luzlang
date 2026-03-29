# Changelog

All notable changes to Luz are documented here.
Format: `## [version] - YYYY-MM-DD` followed by categorized entries.

---

## [1.17.0] - 2026-03-29

### Added
- Slice syntax for lists and strings: `list[start:end]`, `list[start:end:step]`, `string[start:end]`
- Typed variable declarations: `x: int = 5` — type is enforced at assignment
- Type annotations on function parameters and return values now respect class inheritance — a subclass instance satisfies a parent type annotation
- `insert(list, index, value)` builtin — inserts an element at a position, shifting elements right
- Dict dot method syntax: `dict.keys()`, `dict.values()`, `dict.len()`, `dict.contains(key)`, `dict.remove(key)`
- `luz-types` standard library — type predicates (`is_int`, `is_float`, `is_number`, etc.), safe casting (`safe_int`, `safe_float`, `safe_str`, `safe_bool`), and schema validation (`validate`)

### Fixed
- `exp(x)` was calling `math.log(x)` internally — now correctly calls `math.exp(x)`
- `swap()`, `append()`, `contains()`, `join()`, `remove()` and `insert()` dot methods now raise `ArityFault` on missing arguments instead of crashing with a Python `IndexError`
- `0 ** negative` now raises `ZeroDivisionFault` instead of leaking a raw Python `ZeroDivisionError`
- `string // int` and `round(x, non-int)` now raise proper Luz faults instead of leaking a raw Python `ValueError`
- `int in string` now raises `TypeClashFault` instead of leaking a raw Python `TypeError`
- `split(s, "")` now raises `ArgumentFault` instead of leaking a raw Python `ValueError`
- `finally` block no longer silently discards an exception that was already pending from the `rescue` block — the original error is preserved
- `from "x" import a, b` is now atomic — if any name doesn't exist, nothing is imported into scope

---

## [1.16.0] - 2026-03-24

### Added
- Bound methods: retrieving a method from an instance (`m = obj.method`) now returns a bound method that carries `self` automatically — calling `m()` no longer requires passing the instance manually
- String dot method syntax: `str.uppercase()`, `str.lowercase()`, `str.trim()`, `str.swap(old, new)`, `str.split(sep)`
- List dot method syntax: `list.append(x)`, `list.pop()`, `list.len()`, `list.contains(x)`, `list.join(sep)`
- Versioning policy documentation (`docs/versioning.md`)
- Automated release notes: tagging `vX.Y.Z` now extracts the matching changelog entry and sets it as the GitHub release body

### Fixed
- `self.attr[i]` now correctly indexes into instance attributes — previously the index was silently ignored and the full attribute was returned
- Lists, dicts, booleans, and `null` now print in Luz syntax (`"hello"`, `true`, `null`) instead of Python syntax (`'hello'`, `True`, `None`)

---

## [1.15.0] - 2026-03-22

### Added
- Pylint to CI pipeline with a minimum score of 9.0/10
- `.pylintrc` configuration silencing false positives from intentional design decisions
- Lint instructions to `CONTRIBUTING.md`

---

## [1.14.0] - 2026-03-15

### Added
- `from "module" import name` syntax for selective imports
- `import "module" as alias` syntax for aliased imports
- `finally` block in `attempt / rescue`
- `rescue` now accepts an optional error variable (can be omitted)
- Unicode escape sequences (`\uXXXX`, `\UXXXXXXXX`) in string literals
- Scientific notation support for numeric literals (`1.5e10`, `3e-4`)

### Fixed
- `for` loop now validates step direction (errors if step sign contradicts range direction)
- Recursion error messages now report the function name

---

## [1.13.0] - 2026-03-01

### Added
- Block scope for `if` and `while` — variables declared inside do not leak out
- Default function arguments now evaluate in caller scope, not closure scope
- CI test matrix across Python 3.10, 3.11, and 3.12
- 72-test pytest suite organized in 9 classes

### Fixed
- `typeof` module resolution no longer errors on built-in type names
- Scope leak: assigning to a variable no longer creates it in the wrong scope
- Circular inheritance no longer causes infinite recursion (raises `InheritanceFault`)
- Failed imports are properly deregistered so re-importing works correctly
- `len()` no longer uses a bare `except` clause

---

## [1.12.0] - 2026-02-15

### Added
- `switch / case` statement
- `match` expression with multiple value patterns per case
- Compound assignment operators: `+=`, `-=`, `*=`, `/=`
- Negative indexing for lists and strings (`list[-1]`)
- Destructuring assignment: `x, y = func()`

---

## [1.11.0] - 2026-02-01

### Added
- Multiple return values from functions
- Variadic arguments (`...args`)
- Named arguments at call sites
- Lambda expressions: `fn(x) => x * 2` and `fn(x) { body }`

---

## [1.10.0] - 2026-01-15

### Added
- Object-oriented programming: `class`, `extends`, method overriding, `super`
- `attempt / rescue` error handling and `alert` to raise errors
- Module system: `import "path"`
- Ray package manager

---
