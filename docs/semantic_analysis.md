# Semantic Analysis | Mini-LLVM

The semantic analyzer ensures static correctness before code generation. It tracks variable definitions and types across control flow.

## 1. Scope Rules

- **Global Scope Only**: All variables are global.
- **Definition Rule**: A variable must be assigned before use.
- **Control Flow Merging**:
    - `if/else`: A variable is defined after the block if it was defined before OR defined in **both** branches.
    - `while`: A variable is defined after the loop ONLY if it was defined **before** the loop.
    - **Note**: Variables defined strictly inside a `while` loop (or `if` without `else`) are NOT guaranteed to exist after the block.

## 2. Type System

- **Static Constraints**:
    - `if` / `while` conditions must be `bool`.
    - `+`: `int + int` or `str + str`.
    - `-`: `int` (unary or binary).
    - `<`, `>`: `int` vs `int` or `str` vs `str`.
    - `==`, `!=`: Any types.

- **Type Changes**:
    - Variables can be reassigned to different types.
    - **Conflict Rule**: If a variable has different types on different control flow paths (e.g. `int` in `then`, `str` in `else`, or `int` before loop and `str` inside loop), it is removed from the set of defined variables (treated as unsafe/undefined).

## 3. Error Model

- `NameError`: Variable used but not guaranteed defined.
- `TypeError`: Invalid operation or type mismatch.
