# Variables

Variables are assigned with `=`. No declaration keyword is needed.

```
x = 10
name = "Luz"
items = [1, 2, 3]
data = {"score": 100}
empty = null
```

## Reassignment

Variables can be reassigned to any type at any time:

```
x = 10
x = "now a string"
x = true
```

## Scope

Variables live in the scope where they are assigned. Functions create their own scope. Inner scopes can read variables from outer scopes (closures), but assigning in an inner scope creates a new local variable — it does not modify the outer one.

```
x = 10

function show() {
    write(x)   # reads outer x → 10
}

function shadow() {
    x = 99     # creates a new local x, does not touch outer x
    write(x)   # 99
}

show()
shadow()
write(x)   # still 10
```

## Typed declarations

A variable can declare its expected type on assignment. The type is checked at runtime — assigning a value of the wrong type raises a `TypeViolationFault`.

```
x: int = 5
name: string = "Alice"
active: bool = true
ratio: float = 0.5
```

The type annotation only applies to that assignment. It does not prevent the variable from being reassigned to a different type later (Luz is still dynamically typed).

Valid type names: `int`, `float`, `number`, `string`, `bool`, `list`, `dict`, `null`, or any class name.

```
attempt {
    x: int = "oops"
} rescue (e) {
    write(e)   # TypeViolationFault: Variable 'x' expects type 'int', got 'string'
}
```

## Compound assignment

Luz supports `+=`, `-=`, `*=`, and `/=`:

```
count += 1
total *= 2
score -= 5
ratio /= 4
```
