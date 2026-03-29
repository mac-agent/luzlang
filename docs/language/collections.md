# Collections

## Lists

A list is an ordered, mutable sequence of values.

```
fruits = ["apple", "banana", "cherry"]
mixed  = [1, "two", 3.0, true, null]
empty  = []
```

### Indexing

Zero-based. Negative indices count from the end:

```
write(fruits[0])    # apple
write(fruits[-1])   # cherry  (last element)
write(fruits[-2])   # banana
```

### Assignment by index

```
fruits[1] = "mango"
```

### Iteration

```
for fruit in fruits {
    write(fruit)
}
```

### Slicing

Extract a sub-list using `[start:end]` or `[start:end:step]`. Indices are end-exclusive. Negative indices count from the end.

```
nums = [10, 20, 30, 40, 50]

write(nums[1:3])     # [20, 30]
write(nums[:3])      # [10, 20, 30]
write(nums[2:])      # [30, 40, 50]
write(nums[::2])     # [10, 30, 50]   (every other element)
write(nums[::-1])    # [50, 40, 30, 20, 10]  (reversed)
```

Slice indices must be integers. A step of `0` raises a `ZeroDivisionFault`.

### List built-ins

| Function | Description |
|---|---|
| `len(list)` | Number of elements |
| `append(list, value)` | Add element to the end |
| `pop(list)` | Remove and return the last element |
| `pop(list, index)` | Remove and return element at index |
| `insert(list, index, value)` | Insert value at index, shifting elements right |

```
nums = [1, 2, 4, 5]
insert(nums, 2, 3)
write(nums)   # [1, 2, 3, 4, 5]
```

### List dot methods

All list operations are also available as dot methods. Calling a method with the wrong number of arguments raises an `ArityFault`.

```
nums = [1, 2, 3]

nums.append(4)          # [1, 2, 3, 4]
last = nums.pop()       # 4  — removes and returns the last element
write(nums.len())       # 3
write(nums.contains(2)) # true
write(nums.contains(9)) # false

words = ["hello", "world"]
write(words.join(", "))  # hello, world
```

| Method | Equivalent built-in |
|---|---|
| `list.append(value)` | `append(list, value)` |
| `list.pop()` | `pop(list)` |
| `list.pop(index)` | `pop(list, index)` |
| `list.len()` | `len(list)` |
| `list.contains(value)` | — |
| `list.join(sep)` | `join(sep, list)` |

---

## Strings

Strings support indexing and negative indices:

```
s = "hello"
write(s[0])    # h
write(s[-1])   # o
```

Strings also support slicing:

```
write(s[1:3])   # el
write(s[:3])    # hel
write(s[1:])    # ello
```

---

## Dictionaries

A dictionary maps keys to values. Keys must be strings or numbers.

```
person = {"name": "Alice", "age": 30}
```

### Access and assignment

```
write(person["name"])   # Alice
person["age"] = 31
person["city"] = "Madrid"
```

### Iteration

Iterating over a dictionary yields its keys:

```
for key in person {
    write($"{key}: {person[key]}")
}
```

### Dictionary built-ins

| Function | Description |
|---|---|
| `len(dict)` | Number of key-value pairs |
| `keys(dict)` | Returns a list of all keys |
| `values(dict)` | Returns a list of all values |
| `remove(dict, key)` | Remove key and return its value |

### Dictionary dot methods

All dictionary operations are also available as dot methods:

```
person = {"name": "Alice", "age": 30}

write(person.keys())          # ["name", "age"]
write(person.values())        # ["Alice", 30]
write(person.len())           # 2
write(person.contains("age")) # true
person.remove("age")
```

| Method | Equivalent built-in |
|---|---|
| `dict.keys()` | `keys(dict)` |
| `dict.values()` | `values(dict)` |
| `dict.len()` | `len(dict)` |
| `dict.contains(key)` | `key in dict` |
| `dict.remove(key)` | `remove(dict, key)` |
