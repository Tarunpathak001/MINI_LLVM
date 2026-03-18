# Parser & AST | Mini-LLVM

**Status:** Completed  
**Source File:** `parser.py`  
**AST File:** `ast_nodes.py`

The parser consumes a stream of tokens (from Phase 1) and produces a strictly typed Abstract Syntax Tree (AST). It uses a **recursive descent** strategy.

---

## 1. Why Recursive Descent?

Recursive descent parsers map grammar rules directly to Python methods (e.g., `parse_if` corresponds to the `if` grammar rule). This makes the parser:
- **Readable:** The code structure mirrors the grammar.
- **Debuggable:** Logic flow is easy to trace.
- **Flexible:** Custom logic (like checking `INDENT`/`DEDENT` depth) is easier to implement than with parser generators.

## 2. AST Structure

The AST is defined in `ast_nodes.py` using Python `dataclasses`.

- **Root:** `Program(statements=[...])`
- **Statements:** 
    - `Assignment(name, value)`
    - `Print(value)`
    - `If(condition, then_body, else_body)`
- **Expressions:**
    - `BinaryOp(op, left, right)`
    - `UnaryOp(op, operand)`
    - `Literal(value)`
    - `Variable(name)`

## 3. Parsing Logic

### 3.1. Leading Newlines
The parser **skips** any number of `NEWLINE` tokens at the beginning of the file (handling "blank lines" at the top).

### 3.2. Block Parsing
Blocks are mandatory for `if` statements.
- **Trigger:** A `:` token followed by a `NEWLINE`.
- **Start:** An `INDENT` token.
- **Body:** One or more statements. Blank lines (`NEWLINE`s) inside blocks are skipped.
- **End:** A `DEDENT` token.

### 3.3. Operator Precedence
Precedence is encoded in the call stack depth:
1. `parse_expression` calling `parse_relation` (Lowest precedence: `==`, `<`, `>`).
2. `parse_relation` calling `parse_addition` (Medium precedence: `+`).
3. `parse_addition` calling `parse_unary` (High precedence: `-`).
4. `parse_unary` calling `parse_primary` (Highest precedence: `()`, literals).

## 4. Example

### Source
```python
x = 10
if x > 5:
    print(x)
```

### AST (Simplified Representation)
```python
Program([
    Assignment(name='x', value=Literal(10)),
    If(
        condition=BinaryOp('>', Variable('x'), Literal(5)),
        then_body=[
            Print(value=Variable('x'))
        ],
        else_body=None
    )
])
```
