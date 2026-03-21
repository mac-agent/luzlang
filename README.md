# Luz Programming Language

**Luz** is a lightweight, interpreted programming language written in Python. It is designed to be simple, readable, and easy to learn — making it a great starting point for understanding how programming languages work under the hood.

```
name = listen("What is your name? ")
write($"Hello {name}!")

for i = 1 to 5 {
    if even(i) {
        write($"{i} is even")
    } else {
        write($"{i} is odd")
    }
}
```

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Language Reference](#language-reference)
  - [Types](#types)
  - [Variables](#variables)
  - [Operators](#operators)
  - [Control Flow](#control-flow)
  - [Functions](#functions)
  - [Lambdas](#lambdas)
  - [Collections](#collections)
  - [Object-Oriented Programming](#object-oriented-programming)
  - [Error Handling](#error-handling)
  - [Modules](#modules)
  - [Built-in Functions](#built-in-functions)
- [Architecture](#architecture)
- [Running Tests](#running-tests)

---

## Features

- **Dynamic typing** — integers, floats, strings, booleans, lists, dictionaries, `null`
- **Arithmetic operators** — `+`, `-`, `*`, `/`, `//`, `%`, `**`
- **Format strings** — `$"Hello {name}, you are {age} years old!"`
- **String operations** — indexing, escape sequences, and 11 built-in string functions
- **Control flow** — `if / elif / else`, `while`, `for` (range and for-each), `break`, `continue`, `pass`
- **Functions** — user-defined functions with closures and return values
- **Lambdas** — `fn(x) => x * 2` and `fn(x) { body }` as first-class values
- **Object-oriented programming** — classes, instances, inheritance (`extends`), method overriding, and `super`
- **Polymorphism** — duck typing, `typeof()`, and `instanceof()`
- **Math built-ins** — `abs`, `sqrt`, `floor`, `ceil`, `round`, `clamp`, `max`, `min`, `sign`, `odd`, `even`
- **Error handling** — `attempt / rescue` blocks and `alert`
- **Modules** — `import` other `.luz` files
- **Helpful errors** — every error message includes the line number
- **REPL** — interactive shell for quick experimentation
- **VS Code extension** — syntax highlighting included

---

## Installation

Luz requires **Python 3.8+** and has no external dependencies.

```bash
git clone https://github.com/Elabsurdo984/luz-lang.git
cd luz-lang
```

That's it.

---

## Usage

### Interactive REPL

```bash
python main.py
```

```
Luz Interpreter v1.1 - Type 'exit' to terminate
Luz > x = 10
Luz > write(x * 2)
20
Luz > exit
```

### Run a file

```bash
python main.py program.luz
```

### VS Code syntax highlighting

Install the extension from the `vscode-luz/` folder:
1. Copy the folder to `~/.vscode/extensions/`
2. Restart VS Code

---

## Language Reference

### Types

| Type | Example | Notes |
|---|---|---|
| Integer | `42`, `-7` | Whole numbers |
| Float | `3.14`, `-0.5` | Decimal numbers |
| String | `"hello"` | Double quotes, supports escape sequences |
| Boolean | `true`, `false` | Lowercase |
| Null | `null` | Absence of a value |
| List | `[1, "two", 3.0]` | Mixed types allowed |
| Dictionary | `{"key": value}` | String or number keys |

**Escape sequences inside strings:**

| Sequence | Result |
|---|---|
| `\n` | Newline |
| `\t` | Tab |
| `\r` | Carriage return |
| `\\` | Literal backslash |
| `\"` | Literal double quote |

---

### Variables

Variables are assigned with `=`. No declaration keyword needed.

```
x = 10
name = "Luz"
items = [1, 2, 3]
data = {"score": 100}
empty = null
```

---

### Operators

**Arithmetic**

| Operator | Description | Example |
|---|---|---|
| `+` | Addition / string concat | `3 + 2` → `5` |
| `-` | Subtraction | `10 - 4` → `6` |
| `*` | Multiplication / string repeat | `"ab" * 3` → `"ababab"` |
| `/` | Division (always float) | `7 / 2` → `3.5` |
| `//` | Integer division | `7 // 2` → `3` |
| `%` | Modulo | `10 % 3` → `1` |
| `**` | Power (right-associative) | `2 ** 8` → `256` |

**Comparison**

| Operator | Description |
|---|---|
| `==` | Equal |
| `!=` | Not equal |
| `<`, `>` | Less / greater than |
| `<=`, `>=` | Less / greater than or equal |

**Logical**

| Operator | Description |
|---|---|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

**Operator precedence** (highest to lowest):

```
**
* / // %
+ -
== != < > <= >=
not
and
or
```

---

### Control Flow

**if / elif / else**

```
x = 15

if x > 20 {
    write("big")
} elif x > 10 {
    write("medium")
} else {
    write("small")
}
```

**while**

```
i = 0
while i < 5 {
    write(i)
    i = i + 1
}
```

**for — range loop**

Iterates from `start` to `end` (inclusive), incrementing by 1.

```
for i = 1 to 10 {
    write(i)
}
```

**for — for-each loop**

Iterates over a list, string (character by character), or dict (by key).

```
fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
    write(fruit)
}

for ch in "hello" {
    write(ch)
}

for key in {"a": 1, "b": 2} {
    write(key)
}
```

**break / continue / pass**

```
for i = 1 to 10 {
    if i == 3 { continue }   # skip 3
    if i == 7 { break }      # stop at 7
    write(i)
}

if true {
    pass   # placeholder for empty blocks
}
```

---

### Format Strings

Prefix a string with `$` to embed expressions inside `{ }`:

```
name = "Alice"
age = 30
write($"Hello {name}, you are {age} years old!")
write($"2 + 2 = {2 + 2}")
write($"uppercase: {uppercase(name)}")
write($"null value: {null}")
```

Any valid Luz expression works inside `{ }`.

---

### Functions

```
function greet(name) {
    return "Hello, " + name + "!"
}

write(greet("world"))   # Hello, world!
```

Functions capture their surrounding scope (closures):

```
function make_counter() {
    count = 0
    function increment() {
        count = count + 1
        return count
    }
    return increment
}
```

---

### Lambdas

Lambdas are anonymous functions that can be stored in variables, passed as arguments, or returned from other functions.

**Short form** — evaluates a single expression:

```
double = fn(x) => x * 2
write(double(5))   # 10

add = fn(a, b) => a + b
write(add(3, 4))   # 7
```

**Long form** — runs a block with multiple statements:

```
greet = fn(name) {
    msg = "Hello, " + name + "!"
    return msg
}

write(greet("Luz"))   # Hello, Luz!
```

**No parameters:**

```
say_hi = fn() => "hi!"
write(say_hi())   # hi!
```

**Passing as arguments:**

```
function apply(f, value) {
    return f(value)
}

write(apply(fn(x) => x * x, 6))   # 36
```

**Storing in lists:**

```
ops = [fn(x) => x + 1, fn(x) => x * 2, fn(x) => x - 3]
for op in ops {
    write(op(10))
}
# 11, 20, 7
```

**Closures** — lambdas capture variables from the surrounding scope:

```
function make_adder(n) {
    return fn(x) => x + n
}

add5 = make_adder(5)
write(add5(3))    # 8
write(add5(10))   # 15
```

---

### Collections

**Lists**

```
fruits = ["apple", "banana", "cherry"]

write(fruits[0])          # apple
fruits[1] = "mango"
append(fruits, "grape")
write(len(fruits))        # 4

for fruit in fruits {
    write(fruit)
}
```

**Dictionaries**

```
person = {"name": "Alice", "age": 30}

write(person["name"])     # Alice
person["age"] = 31

write(keys(person))       # ["name", "age"]
write(values(person))     # ["Alice", 31]

for key in person {
    write($"{key}: {person[key]}")
}
```

---

### Object-Oriented Programming

**Defining a class**

```
class Animal {
    function init(self, name) {
        self.name = name
    }
    function speak(self) {
        write($"{self.name} makes a sound")
    }
}

a = Animal("Leo")
a.speak()
write(a.name)
```

**Inheritance**

Use `extends` to inherit from a parent class. Child classes inherit all parent methods automatically.

```
class Dog extends Animal {
    function init(self, name, breed) {
        super.init(name)
        self.breed = breed
    }
    function speak(self) {
        super.speak()
        write("(woof!)")
    }
}

d = Dog("Rex", "Labrador")
d.speak()
```

**Method overriding**

Defining a method with the same name in a child class replaces the parent's version.

**Polymorphism**

Because Luz is dynamically typed, any object that has the right methods can be used interchangeably:

```
class Circle extends Shape {
    function init(self, r) { self.r = r }
    function area(self) { return self.r * self.r * 3 }
}

class Rectangle extends Shape {
    function init(self, w, h) { self.w = w   self.h = h }
    function area(self) { return self.w * self.h }
}

shapes = [Circle(5), Rectangle(4, 6)]
for shape in shapes {
    write(shape.area())
}
```

**Type inspection**

```
write(typeof(42))             # int
write(typeof("hello"))        # string
write(typeof(null))           # null
write(typeof(d))              # Dog

write(instanceof(d, Dog))     # true
write(instanceof(d, Animal))  # true  (walks the hierarchy)
write(instanceof(d, Circle))  # false
```

---

### Error Handling

```
attempt {
    x = 10 / 0
} rescue (error) {
    write("Caught:", error)
}
```

Raise a custom error with `alert`:

```
function divide(a, b) {
    if b == 0 {
        alert "Cannot divide by zero"
    }
    return a / b
}

attempt {
    divide(5, 0)
} rescue (e) {
    write(e)
}
```

---

### Modules

```
import "utils.luz"

result = my_function(42)
```

- Imports run in the global scope
- Circular imports are automatically prevented

---

### Built-in Functions

**I/O**

| Function | Description |
|---|---|
| `write(...)` | Print values to stdout |
| `listen(prompt)` | Read user input. Auto-converts numbers |

**Type inspection**

| Function | Description | Example |
|---|---|---|
| `typeof(value)` | Returns the type name as a string | `typeof(42)` → `"int"` |
| `instanceof(obj, Class)` | True if obj is an instance of Class or subclass | `instanceof(d, Animal)` → `true` |

**Type casting**

| Function | Description |
|---|---|
| `to_int(v)` | Convert to integer |
| `to_float(v)` | Convert to float |
| `to_str(v)` | Convert to string |
| `to_bool(v)` | Convert to boolean |
| `to_num(v)` | Convert to int or float (auto-detect) |

**Math**

| Function | Description | Example |
|---|---|---|
| `abs(x)` | Absolute value | `abs(-7)` → `7` |
| `sqrt(x)` | Square root | `sqrt(16)` → `4.0` |
| `floor(x)` | Round down to integer | `floor(3.9)` → `3` |
| `ceil(x)` | Round up to integer | `ceil(3.1)` → `4` |
| `round(x, digits?)` | Round to N decimal places | `round(3.567, 2)` → `3.57` |
| `clamp(x, low, high)` | Force x into range [low, high] | `clamp(15, 0, 10)` → `10` |
| `max(a, b, ...)` | Maximum of values or a list | `max(3, 8, 2)` → `8` |
| `min(a, b, ...)` | Minimum of values or a list | `min([5, 1, 9])` → `1` |
| `sign(x)` | Returns -1, 0, or 1 | `sign(-5)` → `-1` |
| `odd(x)` | True if x is odd | `odd(3)` → `true` |
| `even(x)` | True if x is even | `even(4)` → `true` |

**Lists**

| Function | Description |
|---|---|
| `len(list)` | Number of elements |
| `append(list, value)` | Add element to end |
| `pop(list)` | Remove and return last element |
| `pop(list, index)` | Remove and return element at index |

**Dictionaries**

| Function | Description |
|---|---|
| `len(dict)` | Number of key-value pairs |
| `keys(dict)` | Returns list of keys |
| `values(dict)` | Returns list of values |
| `remove(dict, key)` | Remove key and return its value |

**Strings**

| Function | Description | Example |
|---|---|---|
| `len(s)` | String length | `len("hi")` → `2` |
| `trim(s)` | Remove surrounding whitespace | `trim("  hi  ")` → `"hi"` |
| `uppercase(s)` | Convert to uppercase | `uppercase("hi")` → `"HI"` |
| `lowercase(s)` | Convert to lowercase | `lowercase("HI")` → `"hi"` |
| `swap(s, old, new)` | Replace all occurrences | `swap("aXb", "X", "-")` → `"a-b"` |
| `split(s, sep?)` | Split into list | `split("a,b", ",")` → `["a","b"]` |
| `join(sep, list)` | Join list into string | `join("-", ["a","b"])` → `"a-b"` |
| `contains(s, sub)` | Check if substring exists | `contains("hello", "ell")` → `true` |
| `begins(s, prefix)` | Check prefix | `begins("hello", "he")` → `true` |
| `ends(s, suffix)` | Check suffix | `ends("hello", "lo")` → `true` |
| `find(s, sub)` | Index of first occurrence, -1 if not found | `find("hello", "ll")` → `2` |
| `count(s, sub)` | Count occurrences | `count("banana", "a")` → `3` |

---

## Architecture

Luz follows a classic three-stage interpreter pipeline:

```
Source code (text)
      |
   [Lexer]         luz/lexer.py
      |
 Token stream
      |
   [Parser]        luz/parser.py
      |
  AST (tree)
      |
 [Interpreter]     luz/interpreter.py
      |
   Result
```

### Lexer (`luz/lexer.py`)

Converts raw source text into a flat list of tokens. Handles numbers, strings (with escape sequences), format strings, identifiers, keywords, and operators. Tracks line numbers for every token to enable helpful error messages.

### Parser (`luz/parser.py`)

Consumes the token stream and builds an **Abstract Syntax Tree (AST)** using a **recursive descent parser**. Operator precedence is enforced through nested parsing functions — each level calls the next higher-precedence level:

```
logical_or → logical_and → logical_not → comparison
          → arithmetic → term → power → factor
```

Each node type (e.g. `BinOpNode`, `IfNode`, `CallNode`, `ClassDefNode`) is a plain Python class defined at the top of the file.

### Interpreter (`luz/interpreter.py`)

Walks the AST using the **Visitor pattern**: `visit(node)` dynamically dispatches to `visit_IfNode`, `visit_BinOpNode`, etc.

Scope is managed through a chain of `Environment` objects — each block or function call creates a new environment linked to its parent, enabling proper variable scoping and closures.

OOP is implemented through `LuzClass`, `LuzInstance`, and `LuzSuperProxy` objects. Method calls automatically inject `self` and `super` into the method's local scope.

Control flow signals (`return`, `break`, `continue`) are implemented as Python exceptions that propagate up the call stack and are caught at the appropriate level.

### Error system (`luz/exceptions.py`)

All errors inherit from `LuzError` and are grouped into four categories:

```
LuzError
├── SyntaxFault       (lexer / parser errors)
├── SemanticFault     (type errors, undefined variables, wrong arg count...)
├── RuntimeFault      (division by zero, index out of bounds...)
└── UserFault         (raised by the alert keyword)
```

Every error carries a `line` attribute that is attached automatically when the error propagates through `visit()`.

### File overview

```
luz-lang/
├── main.py               # Entry point: REPL and file execution
├── luz/
│   ├── tokens.py         # TokenType enum and Token class
│   ├── lexer.py          # Lexer: text → tokens
│   ├── parser.py         # Parser: tokens → AST + all AST node classes
│   ├── interpreter.py    # Interpreter: executes the AST
│   └── exceptions.py     # Full error class hierarchy
├── tests/
│   └── test_suite.py     # Test suite
├── vscode-luz/           # VS Code syntax highlighting extension
└── examples/             # Example programs
```

---

## Running Tests

```bash
python tests/test_suite.py
```

---

## Contributing

Contributions are welcome. If you want to add a feature, fix a bug, or improve the docs:

1. Fork the repository
2. Create a branch for your change
3. Make sure the tests pass
4. Open a pull request

If you're looking for ideas, check the open issues or consider:
- First-class functions (passing functions as values)
- Negative index support for lists
- More test coverage, especially for OOP and format strings

---

## License

MIT License — see [LICENSE](LICENSE) for details.
