# Needle

Navigating nested structures easily.

## Description

The idea behind this package is to provide a simple interface allowing to "flatten" nested structures into 
a plain table where each key is represented as a fully qualified name that leads to a certain field in the
structure. It is especially useful when dealing with complex configuration objects that are merged into one
from several files or container, and include very long keys that aren't easily visualized via pretty printing.

## Functionality

The package's goal is to provide a simple interface for navigating configurations right in the terminal while
debugging an executed script. It provides two basic high-level functions:

```python
from needle import search, view

obj = { ... }  # some nested object

# parsing keys (with optional depth limitation)
s = search(obj, max_depth=3)  

print(s.top.flat_keys)   # all keys available on the topmost level
s.subsearch("dataset")   # navigating to the "dataset" subsection
print(s.top.flat_keys)   # now, the "dataset" subsection is on the top of the stack

view(obj)                # starts an interactive mode as showed below 
```

## Showcase

![](docs/quick_example.gif)

## Why?

The author of this package encountered a problem of navigating a deeply nested objects often enough to bother
writing a dedicated package that (in his opinion) should simplify that endeavor.