# Mini-LLVM: Complete Project Walkthrough

> **Purpose of this document:** Provide a complete, self-contained explanation of the Mini-LLVM project so that any reader (human or AI like ChatGPT) can fully understand the architecture, every source file, every optimization, every data structure, and how they all fit together.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [What is Mini-Python?](#2-what-is-mini-python)
3. [Compiler Pipeline at a Glance](#3-compiler-pipeline-at-a-glance)
4. [Directory Structure](#4-directory-structure)
5. [Phase 1 — Lexical Analysis (Lexer)](#5-phase-1--lexical-analysis-lexer)
6. [Phase 2 — Parsing (Parser & AST)](#6-phase-2--parsing-parser--ast)
7. [Phase 3 — Semantic Analysis](#7-phase-3--semantic-analysis)
8. [Phase 4 — SSA IR Construction](#8-phase-4--ssa-ir-construction)
9. [Phase 5 — SSA Optimization Passes](#9-phase-5--ssa-optimization-passes)
10. [Phase 6 — Bytecode Lowering](#10-phase-6--bytecode-lowering)
11. [Phase 7 — Stack-Based Virtual Machine](#11-phase-7--stack-based-virtual-machine)
12. [End-to-End Example](#12-end-to-end-example)
13. [Testing](#13-testing)
14. [How to Run](#14-how-to-run)

---

## 1. Project Overview

**Mini-LLVM** is an educational, from-scratch compiler written entirely in Python. It compiles a small Python-like language called **Mini-Python** through a full production-style pipeline:

```
Source Code → Lexer → Parser → Semantic Analysis → SSA IR → Optimizations → Bytecode → VM Execution
```

The project was built to deeply understand:
- How compilers tokenize, parse, and analyze code
- SSA (Static Single Assignment) form and Phi nodes
- How control flow (`if/else`, `while`) is lowered in compilers
- Writing real optimization passes (constant folding, dead code elimination, etc.)
- Code generation to a stack-based bytecode and execution on a virtual machine

**Language:** Python 3.8+  
**Dependencies:** None (standard library only)  
**License:** MIT

---

## 2. What is Mini-Python?

Mini-Python is a deliberately minimal, Python-like language designed for compiler construction. It supports:

### Supported Types
| Type       | Examples            |
|------------|---------------------|
| `int`      | `10`, `-5`          |
| `string`   | `"hello"`, `'abc'`  |
| `bool`     | `True`, `False`     |
| `NoneType` | `None`              |

### Supported Statements
1. **Assignment:** `x = expression`
2. **Print:** `print(expression)`
3. **If/Else:** `if condition:` ... `else:` ...
4. **While loops:** `while condition:` ...

### Supported Operators
- **Arithmetic:** `+` (addition for ints, concatenation for strings)
- **Comparison:** `<`, `>` (int–int or string–string only)
- **Equality:** `==`, `!=` (any types)
- **Unary:** `-` (negation, int only)

### Intentional Non-Features (Excluded by Design)
- Functions (`def`, `return`)
- Boolean operators (`and`, `or`, `not`)
- Truthiness (e.g., `if 1:` is a **TypeError**, not truthy)
- `for` loops, `break`, `continue`
- `float`, `list`, `dict`

### Example Valid Program
```python
x = 10
y = 20
if x < y:
    print("x is smaller")
    res = x + y
    print(res)
else:
    print("x is not smaller")
```

### Example Invalid Program (TypeError)
```python
x = 10
if x:          # ERROR: condition must be bool, no truthiness
    print("no")
```

---

## 3. Compiler Pipeline at a Glance

```
Source Code  (string)
     │
     ▼
┌──────────┐
│  LEXER   │  src/lexer.py
│          │  Converts source string → list of Token objects
└────┬─────┘
     │  List[Token]
     ▼
┌──────────┐
│  PARSER  │  src/parser.py  +  src/ast_nodes.py
│          │  Converts tokens → Abstract Syntax Tree (AST)
└────┬─────┘
     │  AST (Program node)
     ▼
┌──────────────────┐
│ SEMANTIC ANALYSIS│  src/semantic.py
│                  │  Validates types, scopes, variable usage
└────┬─────────────┘
     │  Validated AST (same object, or raises error)
     ▼
┌──────────────┐
│  IR BUILDER  │  src/ir_builder.py  +  src/ir.py
│              │  Converts AST → SSA Intermediate Representation
└────┬─────────┘
     │  IRProgram (list of IR instructions)
     ▼
┌──────────────────────┐
│  OPTIMIZATION PASSES │  optimizations/*.py
│                      │  7 independent passes that improve the IR
└────┬─────────────────┘
     │  Optimized IRProgram
     ▼
┌─────────────────────┐
│  BYTECODE LOWERING  │  src/ssa_to_bytecode.py  +  src/bytecode.py
│                     │  Converts SSA IR → stack-based bytecode
└────┬────────────────┘
     │  List[BCInstr]
     ▼
┌──────────────────┐
│  VIRTUAL MACHINE │  src/bytecode_vm.py
│                  │  Executes bytecode instructions
└──────────────────┘
     │
     ▼
  Program Output (printed values)
```

---

## 4. Directory Structure

```
MINI_LLVM/
│
├── src/                          # Core compiler source code
│   ├── __init__.py
│   ├── lexer.py                  # Phase 1: Tokenizer
│   ├── ast_nodes.py              # AST node definitions (dataclasses)
│   ├── parser.py                 # Phase 2: Recursive descent parser
│   ├── semantic.py               # Phase 3: Semantic analyzer
│   ├── ir.py                     # IR instruction definitions (dataclasses)
│   ├── ir_builder.py             # Phase 4: AST → SSA IR converter
│   ├── bytecode.py               # Bytecode instruction definitions
│   ├── ssa_to_bytecode.py        # Phase 6: SSA IR → Bytecode lowering
│   └── bytecode_vm.py            # Phase 7: Stack-based VM
│
├── optimizations/                # Phase 5: SSA optimization passes
│   ├── __init__.py
│   ├── ssa_constprop.py          # Constant Propagation
│   ├── ssa_constfold.py          # Constant Folding
│   ├── ssa_branch_simplify.py    # Branch Simplification
│   ├── ssa_dce.py                # Dead Code Elimination
│   ├── ssa_unreachable_elim.py   # Unreachable Block Elimination
│   ├── ssa_phi_simplify.py       # Phi Node Simplification
│   └── ssa_jump_thread.py        # Jump Threading
│
├── tests/                        # Unit tests for every phase
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_parser_while.py
│   ├── test_semantic.py
│   ├── test_ir.py
│   ├── test_ir_loop.py
│   ├── test_bytecode.py
│   ├── test_bytecode_while.py
│   ├── test_constfold.py
│   ├── test_constprop.py
│   ├── test_branch_simplify.py
│   ├── test_dce.py
│   ├── test_unreachable.py
│   └── test_cleanup.py          # Full pipeline integration test
│
├── docs/                         # Design documentation
│   ├── language_spec.md
│   ├── lexer.md
│   ├── parser.md
│   ├── semantic_analysis.md
│   ├── ir_ssa.md
│   ├── bytecode_vm.md
│   └── work.md                  # Workflow & run instructions
│
├── README.md
├── LICENSE.md
├── SECURITY.md
├── requirements.txt
└── requirement.py                # Setup script
```

---

## 5. Phase 1 — Lexical Analysis (Lexer)

**File:** `src/lexer.py`

### What It Does
The Lexer reads a raw source code string and converts it into a flat list of **Token** objects. Each token has a type (e.g., `IF`, `INTEGER`, `PLUS`), a value, and its line/column position.

### Key Classes

#### `TokenType` — Enum-like class of all token categories
```
IDENTIFIER, IF, ELSE, PRINT, TRUE, FALSE, NONE, WHILE,
INTEGER, STRING,
PLUS (+), MINUS (-), LT (<), GT (>), EQ (==), NE (!=), ASSIGN (=),
LPAREN, RPAREN, COLON,
NEWLINE, INDENT, DEDENT, EOF
```

#### `Token` — Stores one token
```python
Token(type='INTEGER', value=10, line=1, column=5)
```

#### `Lexer` — The tokenizer
- **Input:** Source code string
- **Output:** `List[Token]`
- **Method:** `lexer.tokenize()`

### How It Works
1. Splits source into lines.
2. For each line:
   - Counts leading spaces to determine indentation level.
   - Compares with an `indent_stack` to emit `INDENT` / `DEDENT` tokens (Python-style significant whitespace).
   - Scans the line content character by character:
     - Strings: matched by regex `"..."` or `'...'`
     - Two-char operators: `==`, `!=`
     - Single-char operators: `+`, `-`, `<`, `>`, `=`, `(`, `)`, `:`
     - Keywords: `if`, `else`, `print`, `True`, `False`, `None`, `while`
     - Identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`
     - Integers: `\d+`
   - Appends a `NEWLINE` token at the end of each line.
3. After all lines: emits remaining `DEDENT` tokens and a final `EOF` token.

### Important Design Decisions
- **Tabs are illegal** — raises `IndentationError`.
- **Comments** (`#`) cause the rest of the line to be skipped.
- **INDENT/DEDENT** tokens are synthetic; they represent indentation changes, not literal characters.

### Example
Input:
```python
x = 10
if x > 5:
    print(x)
```
Output tokens (simplified):
```
IDENTIFIER(x), ASSIGN(=), INTEGER(10), NEWLINE
IF(if), IDENTIFIER(x), GT(>), INTEGER(5), COLON(:), NEWLINE
INDENT, PRINT(print), LPAREN, IDENTIFIER(x), RPAREN, NEWLINE
DEDENT, EOF
```

---

## 6. Phase 2 — Parsing (Parser & AST)

**Files:** `src/parser.py`, `src/ast_nodes.py`

### AST Node Definitions (`ast_nodes.py`)

All nodes are Python `@dataclass` classes inheriting from a base `ASTNode`:

| Node          | Fields                                      | Represents               |
|---------------|----------------------------------------------|--------------------------|
| `Program`     | `statements: List[ASTNode]`                  | The entire program       |
| `Assignment`  | `name: str`, `value: ASTNode`                | `x = expr`               |
| `Print`       | `value: ASTNode`                             | `print(expr)`            |
| `If`          | `condition`, `then_body`, `else_body`         | `if/else` statement      |
| `While`       | `condition`, `body`                           | `while` loop             |
| `BinaryOp`    | `op: str`, `left: ASTNode`, `right: ASTNode` | `a + b`, `a < b`, etc.   |
| `UnaryOp`     | `op: str`, `operand: ASTNode`                | `-expr`                  |
| `Literal`     | `value: object`                              | `10`, `"hi"`, `True`, `None` |
| `Variable`    | `name: str`                                  | Variable reference       |

### Parser (`parser.py`)

A **recursive descent parser** that consumes the token list and builds the AST.

#### Method Hierarchy (Operator Precedence)
```
parse()
 └── parse_statement()
      ├── parse_assignment()      IDENTIFIER = expression NEWLINE
      ├── parse_print()           print ( expression ) NEWLINE
      ├── parse_if()              if expression : NEWLINE block [else : NEWLINE block]
      └── parse_while()           while expression : NEWLINE block

parse_expression()
 └── parse_relation()            left [< | > | == | !=] right
      └── parse_addition()        left { + right }
           └── parse_unary()       [- ] primary
                └── parse_primary() INTEGER | STRING | TRUE | FALSE | NONE | IDENTIFIER | ( expr )
```

#### Block Parsing
`parse_block()` expects:
1. An `INDENT` token
2. One or more statements
3. A `DEDENT` token

This maps directly to Python's indentation-based block structure.

### Formal Grammar (EBNF)
```ebnf
program     ::= { statement }
statement   ::= assignment | print_stmt | if_stmt | while_stmt
assignment  ::= IDENTIFIER "=" expression NEWLINE
print_stmt  ::= "print" "(" expression ")" NEWLINE
if_stmt     ::= "if" expression ":" NEWLINE block ["else" ":" NEWLINE block]
while_stmt  ::= "while" expression ":" NEWLINE block
block       ::= INDENT { statement } DEDENT
expression  ::= relation
relation    ::= addition [("<" | ">" | "==" | "!=") addition]
addition    ::= unary { "+" unary }
unary       ::= ["-"] primary
primary     ::= INTEGER | STRING | "True" | "False" | "None" | IDENTIFIER | "(" expression ")"
```

---

## 7. Phase 3 — Semantic Analysis

**File:** `src/semantic.py`

### What It Does
Walks the AST and enforces semantic rules **before** code generation. It uses the **Visitor Pattern** (`visit_<NodeType>` methods).

### State Tracked
- `defined_vars: set` — variables guaranteed to be defined at the current point.
- `var_types: dict` — maps variable names to their statically-inferred Python type (`int`, `str`, `bool`, `type(None)`).

### Rules Enforced

1. **Variable must be defined before use** — raises `NameError`.
2. **`if`/`while` condition must be `bool`** — raises `TypeError`. No truthiness allowed!
3. **Type checking on operators:**
   - `+` requires both `int` or both `str` — raises `TypeError` otherwise.
   - `<`, `>` requires matching types (`int`/`int` or `str`/`str`).
   - `==`, `!=` accept any types.
   - `-` (unary) requires `int`.

### Branch Merging Logic

#### For `if/else`:
- Snapshots state before branches.
- Visits `then` body, captures its state.
- Resets state, visits `else` body (or uses initial state if no `else`), captures its state.
- **Merge rule:** A variable is defined after `if` only if defined in **both** branches. If types conflict, the variable is removed from the defined set.

#### For `while`:
- Snapshots state before loop.
- Visits body.
- **Strict rule:** No new variables survive loop scope (restores `defined_vars` to pre-loop state).
- If a pre-existing variable changes type inside the loop, it is removed from defined set.

---

## 8. Phase 4 — SSA IR Construction

**Files:** `src/ir.py` (IR instruction definitions), `src/ir_builder.py` (AST → IR converter)

### What is SSA?
**Static Single Assignment** is a property where every variable is assigned **exactly once**. When a variable is reassigned, a new numbered version is created:
```python
x = 1      →  x_1 = 1
x = x + 2  →  x_2 = x_1 + 2
```

When control flow merges (e.g., after `if/else`), a **Phi node** selects the correct version:
```
x_3 = Phi(x_1 from L_then, x_2 from L_else)
```

### IR Instruction Types (`ir.py`)

| Instruction   | Fields                                | Meaning                           |
|---------------|---------------------------------------|-----------------------------------|
| `Const`       | `target`, `value`                     | `target = value` (literal)        |
| `BinaryOp`    | `op`, `target`, `left`, `right`       | `target = left op right`          |
| `UnaryOp`     | `op`, `target`, `operand`             | `target = op(operand)`            |
| `Mov`         | `target`, `source`                    | `target = source` (copy)          |
| `Phi`         | `target`, `inputs: [(val, label)]`    | Merge values from different paths |
| `Label`       | `name`                                | Basic block label                 |
| `Jump`        | `target_label`                        | Unconditional jump                |
| `Branch`      | `condition`, `true_label`, `false_label` | Conditional branch             |
| `Print`       | `value`                               | Print a value                     |
| `IRProgram`   | `instructions: List[IRInstr]`         | The whole program                 |

### IRBuilder (`ir_builder.py`)

Uses the Visitor Pattern to walk the AST and emit IR instructions.

#### Key Internal State
- `current_defs: Dict[str, str]` — Maps user variable names to their current SSA name (e.g., `"x" → "x_2"`)
- `var_versions: Dict[str, int]` — Tracks the next version number for each variable
- `counter_temp: int` — Counter for temporary variables (`t1`, `t2`, ...)
- `counter_labels: int` — Counter for generating unique labels
- `current_label: str` — The label of the basic block currently being populated

#### How Each AST Node is Lowered

**Literal** → `Const(t1, value)`  
**Variable** → Returns the current SSA name from `current_defs`  
**Assignment** (`x = expr`) → Evaluates `expr`, creates a new SSA version `x_N`, emits `Mov(x_N, expr_result)`  
**Print** → Evaluates expr, emits `Print(val)`  
**BinaryOp** → Evaluates left and right, emits `BinaryOp(op, target, left, right)` with IR op names (`add`, `lt`, `gt`, `eq`, `ne`)  
**UnaryOp** → Evaluates operand, emits `UnaryOp('neg', target, operand)`

**If/Else Lowering:**
```
entry:
    ...
    Branch(cond, L_then, L_else)
L_then:
    ... then body ...
    Jump(L_merge)
L_else:
    ... else body (if any) ...
    Jump(L_merge)
L_merge:
    Phi(x_3, [(x_1, L_then), (x_2, L_else)])   # if x was modified in branches
```

**While Loop Lowering:**
```
    Jump(L_header)
L_header:
    Phi(x_2, [(x_1, L_pre), (x_3, L_body_end)])   # loop-carried variable
    cond = evaluate condition
    Branch(cond, L_body, L_exit)
L_body:
    ... body ...
    Jump(L_header)                                  # backedge
L_exit:
    ... (x_2 is available here via Phi) ...
```

The `collect_assigned_vars()` helper recursively finds all variables assigned inside a body, so the builder knows which variables need Phi nodes.

---

## 9. Phase 5 — SSA Optimization Passes

**Directory:** `optimizations/`

Each pass is a standalone class with a `run(ir: IRProgram) -> IRProgram` method. They take an `IRProgram`, produce a **new** `IRProgram`, and can be composed in any order.

### 9.1. Constant Propagation (`ssa_constprop.py`)

**What it does:** Tracks which SSA variables hold known constant values. If all inputs to a Phi are the same constant, the Phi's target is also marked constant. This is an **analysis-only** pass — it doesn't change instructions, it populates a `const_map`.

**How it works:**
- Scans instructions forward.
- `Const(target, value)` → records `const_map[target] = value`.
- `Mov(target, source)` → if `source` is in `const_map`, propagates to `target`.
- `Phi` → if all inputs are known and equal, marks `target` as that constant.
- Other instructions are passed through unchanged.

### 9.2. Constant Folding (`ssa_constfold.py`)

**What it does:** If both operands of a `BinaryOp` (or the operand of a `UnaryOp`) are known constants, it evaluates the operation at compile time and replaces the instruction with a `Const`.

**Example:**
```
Const(t1, 3)           →  Const(t1, 3)
Const(t2, 4)           →  Const(t2, 4)
BinaryOp(add, t3, t1, t2)  →  Const(t3, 7)     # Folded!
```

### 9.3. Branch Simplification (`ssa_branch_simplify.py`)

**What it does:** If the condition of a `Branch` is a known constant (`True` or `False`), replaces the `Branch` with an unconditional `Jump` to the appropriate target.

**Example:**
```
Const(t1, True)                         →  Const(t1, True)
Branch(t1, L_then, L_else)             →  Jump(L_then)     # Simplified!
```

### 9.4. Dead Code Elimination (`ssa_dce.py`)

**What it does:** Removes instructions whose results are never used. Works by scanning instructions **backward** and tracking which SSA names are "used."

**Algorithm:**
1. Start from the end of the instruction list.
2. Side-effect instructions (`Print`, `Branch`, `Jump`, `Label`) are always kept, and their operands are marked as "used."
3. For other instructions (`Const`, `Mov`, `BinaryOp`, `UnaryOp`, `Phi`): keep only if their `target` is in the `used` set. If kept, mark their operands as used too.
4. Reverse the kept list to restore original order.

### 9.5. Unreachable Block Elimination (`ssa_unreachable_elim.py`)

**What it does:** Removes basic blocks that cannot be reached from the `entry` block.

**Algorithm:**
1. **Split** the linear instruction list into basic blocks (each starts at a `Label`).
2. **Build a CFG** (Control Flow Graph): for each block, examine the last instruction (`Jump` → one successor, `Branch` → two successors).
3. **BFS** from `entry` to find all reachable blocks.
4. **Remove** unreachable blocks.
5. **Clean up Phi nodes:** Remove Phi inputs whose predecessor block was deleted.

### 9.6. Phi Simplification (`ssa_phi_simplify.py`)

**What it does:** If a Phi node has only **one** input (e.g., because unreachable block elimination removed the other), it is replaced with a simple `Mov`.

**Example:**
```
Phi(x_3, [(x_1, L_then)])  →  Mov(x_3, x_1)
```

### 9.7. Jump Threading (`ssa_jump_thread.py`)

**What it does:** If a block contains only `Label A` followed by `Jump B` (a trivial forwarding block), then all jumps to `A` are rewritten to jump directly to `B`.

**Algorithm:**
1. **Pass 1:** Scan for `Label` immediately followed by `Jump` (with no instructions between). Record `A → B` mapping (guard against self-loops).
2. **Pass 2:** Rewrite all `Jump` instructions: if target is in the map, replace with the forwarded destination.

### Typical Optimization Pipeline Order
```python
ir = SSAConstProp().run(ir)         # Analyze constants
ir = SSAConstFold().run(ir)         # Fold constant expressions
ir = SSABranchSimplify().run(ir)    # Convert constant branches to jumps
ir = SSADCE().run(ir)               # Remove dead instructions
ir = SSAUnreachableElim().run(ir)   # Remove unreachable blocks
ir = SSAPhiSimplify().run(ir)       # Simplify single-input Phis
ir = SSAJumpThread().run(ir)        # Thread trivial jumps
```

---

## 10. Phase 6 — Bytecode Lowering

**Files:** `src/bytecode.py` (instruction definitions), `src/ssa_to_bytecode.py` (converter)

### Bytecode Instruction Set (`bytecode.py`)

| Instruction | Type         | Description                                |
|-------------|--------------|--------------------------------------------|
| `Push(val)` | Data         | Push a constant value onto the stack       |
| `Load(name)`| Data         | Load variable `name` from env, push to stack|
| `Store(name)`| Data        | Pop top of stack, store into `name`        |
| `Add()`     | Arithmetic   | Pop two values, push their sum             |
| `Lt()`      | Comparison   | Pop two values, push `a < b`               |
| `Gt()`      | Comparison   | Pop two values, push `a > b`               |
| `Eq()`      | Comparison   | Pop two values, push `a == b`              |
| `Ne()`      | Comparison   | Pop two values, push `a != b`              |
| `Neg()`     | Unary        | Pop one value, push `-a`                   |
| `Label(name)`| Control     | A named position in the bytecode           |
| `Jump(target)`| Control    | Unconditional jump to label                |
| `Branch(true, false)`| Control | Pop condition, jump accordingly         |
| `Print()`   | I/O          | Pop top of stack and print it              |

### SSA-to-Bytecode Converter (`ssa_to_bytecode.py`)

**Class:** `SSAToBytecode` with method `convert(ir_prog) -> List[BCInstr]`

#### Key Concepts

1. **SSA Name Stripping:** SSA names like `x_1`, `x_2` are stripped to `x` (the original variable name) using `_strip_ssa()`. This works by removing the last `_N` suffix. Temporaries like `t1` have no underscore suffix and remain as `t1`.

2. **Phi Resolution:** Phi nodes are NOT directly translated. Instead:
   - The converter builds a map: `phis_at_label[label] → list of Phis`.
   - Before each `Jump`, if the target label has Phis, the converter emits `Load`/`Store` pairs to move the correct input value into the Phi target variable (based on which block is jumping).
   - `Branch` targets with Phis are NOT allowed (would require critical edge splitting).

3. **Instruction-by-Instruction Lowering:**
   - `Const(target, val)` → `Push(val)` + `Store(stripped_target)`
   - `Mov(target, source)` → `Load(stripped_source)` + `Store(stripped_target)`
   - `BinaryOp(op, target, left, right)` → `Load(left)` + `Load(right)` + `Op()` + `Store(target)`
   - `UnaryOp('neg', target, operand)` → `Load(operand)` + `Neg()` + `Store(target)`
   - `Print(value)` → `Load(value)` + `Print()`
   - `Jump(label)` → emit Phi moves + `Jump(label)`
   - `Branch(cond, T, F)` → `Load(cond)` + `Branch(T, F)`
   - `Label` → `Label`
   - `Phi` → skipped (handled by Jump/Branch)

---

## 11. Phase 7 — Stack-Based Virtual Machine

**File:** `src/bytecode_vm.py`

### Architecture
- **Stack:** A LIFO stack (`List[Any]`) for intermediate computations.
- **Environment:** A dictionary (`Dict[str, Any]`) mapping variable names to their runtime values.
- **Instruction Pointer (ip):** Points to the next instruction to execute.
- **Labels Map:** Pre-scanned dictionary mapping label names to their instruction index.

### Execution Loop
```python
class VM:
    def run(self):
        while self.ip < len(self.code):
            instr = self.code[self.ip]
            self.ip += 1
            self.execute(instr)
```

### How Each Instruction Executes

| Instruction     | Stack Before      | Stack After           | Effect                              |
|-----------------|-------------------|-----------------------|-------------------------------------|
| `Push(val)`     | `[...]`           | `[..., val]`          | Pushes constant                     |
| `Load(name)`    | `[...]`           | `[..., env[name]]`    | Loads from env (NameError if missing)|
| `Store(name)`   | `[..., val]`      | `[...]`               | `env[name] = val`                   |
| `Add()`         | `[..., a, b]`     | `[..., a+b]`          |                                     |
| `Lt()`          | `[..., a, b]`     | `[..., a<b]`          |                                     |
| `Gt()`          | `[..., a, b]`     | `[..., a>b]`          |                                     |
| `Eq()`          | `[..., a, b]`     | `[..., a==b]`         |                                     |
| `Ne()`          | `[..., a, b]`     | `[..., a!=b]`         |                                     |
| `Neg()`         | `[..., a]`        | `[..., -a]`           |                                     |
| `Label(name)`   | —                 | —                     | No-op (marker only)                 |
| `Jump(target)`  | —                 | —                     | `ip = labels[target]`               |
| `Branch(T, F)`  | `[..., cond]`     | `[...]`               | Jump to T if cond, else F           |
| `Print()`       | `[..., val]`      | `[...]`               | `print(val)` to stdout              |

---

## 12. End-to-End Example

### Source Code
```python
x = 5
y = 10
if x < y:
    print(x + y)
else:
    print(0)
```

### Phase 1: Lexer Output (simplified)
```
IDENTIFIER(x) ASSIGN INTEGER(5) NEWLINE
IDENTIFIER(y) ASSIGN INTEGER(10) NEWLINE
IF IDENTIFIER(x) LT IDENTIFIER(y) COLON NEWLINE
  INDENT PRINT LPAREN IDENTIFIER(x) PLUS IDENTIFIER(y) RPAREN NEWLINE
  DEDENT
ELSE COLON NEWLINE
  INDENT PRINT LPAREN INTEGER(0) RPAREN NEWLINE
  DEDENT
EOF
```

### Phase 2: AST
```
Program([
  Assignment("x", Literal(5)),
  Assignment("y", Literal(10)),
  If(
    condition=BinaryOp("<", Variable("x"), Variable("y")),
    then_body=[Print(BinaryOp("+", Variable("x"), Variable("y")))],
    else_body=[Print(Literal(0))]
  )
])
```

### Phase 3: Semantic Analysis
- `x` assigned type `int`, `y` assigned type `int` ✓
- `x < y` → both `int`, returns `bool` — valid condition ✓
- `x + y` → both `int`, returns `int` ✓
- `0` is `int`, printed ✓

### Phase 4: SSA IR (before optimization)
```
entry:
    Const(t1, 5)
    Mov(x_1, t1)
    Const(t2, 10)
    Mov(y_1, t2)
    BinaryOp(lt, t3, x_1, y_1)
    Branch(t3, L_then_1, L_else_2)
L_then_1:
    BinaryOp(add, t4, x_1, y_1)
    Print(t4)
    Jump(L_merge_3)
L_else_2:
    Const(t5, 0)
    Print(t5)
    Jump(L_merge_3)
L_merge_3:
```

### Phase 5: After Constant Folding + Branch Simplification
Since `x` and `y` are constants (5 and 10), the optimizer can fold `5 < 10` → `True`, simplify the branch to `Jump(L_then_1)`, fold `5 + 10` → `15`, then eliminate the unreachable `else` block:
```
entry:
    Const(t1, 5)
    Mov(x_1, t1)
    Const(t2, 10)
    Mov(y_1, t2)
    Jump(L_then_1)
L_then_1:
    Const(t4, 15)
    Print(t4)
```
(Dead code elimination removes unused instructions, unreachable elimination removes `L_else_2`)

### Phase 6: Bytecode
```
Label(entry)
Push(5), Store(x)
Push(10), Store(y)
Jump(L_then_1)
Label(L_then_1)
Push(15), Store(t4)
Load(t4), Print
```

### Phase 7: VM Execution
```
Output: 15
```

---

## 13. Testing

**Directory:** `tests/`

Each compiler phase has dedicated unit tests:

| Test File                  | What It Tests                                             |
|----------------------------|-----------------------------------------------------------|
| `test_lexer.py`            | Tokenization of various source strings                    |
| `test_parser.py`           | AST construction from token streams                       |
| `test_parser_while.py`     | Parsing of `while` loops                                  |
| `test_semantic.py`         | Semantic analysis: type checking, scope rules, error cases|
| `test_ir.py`               | Basic SSA IR generation (if/else, assignments)            |
| `test_ir_loop.py`          | IR generation for `while` loops with Phi nodes            |
| `test_bytecode.py`         | Basic bytecode generation and VM execution                |
| `test_bytecode_while.py`   | While loop bytecode execution end-to-end                  |
| `test_constfold.py`        | Constant Folding pass                                     |
| `test_constprop.py`        | Constant Propagation pass                                 |
| `test_branch_simplify.py`  | Branch Simplification pass                                |
| `test_dce.py`              | Dead Code Elimination pass                                |
| `test_unreachable.py`      | Unreachable Block Elimination pass                        |
| `test_cleanup.py`          | **Full pipeline integration test** (all phases together)  |

### Running Tests
```bash
# All tests
python -m unittest discover -s tests

# Specific test
python -m tests.test_cleanup
```

---

## 14. How to Run

### Prerequisites
- Python 3.8+
- No external dependencies

### Setup
```bash
git clone https://github.com/Tarunpathak001/MINI_LLVM.git
cd MINI_LLVM
python requirement.py   # Optional: installs any pip dependencies
```

### Running Tests
```bash
python -m unittest discover -s tests
```

### Using the Compiler Programmatically
```python
from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.ir_builder import IRBuilder
from src.ssa_to_bytecode import SSAToBytecode
from src.bytecode_vm import VM
from optimizations.ssa_constprop import SSAConstProp
from optimizations.ssa_constfold import SSAConstFold
from optimizations.ssa_branch_simplify import SSABranchSimplify
from optimizations.ssa_dce import SSADCE
from optimizations.ssa_unreachable_elim import SSAUnreachableElim
from optimizations.ssa_phi_simplify import SSAPhiSimplify
from optimizations.ssa_jump_thread import SSAJumpThread

source = """
x = 10
y = 20
if x < y:
    print(x + y)
else:
    print(0)
"""

# Phase 1: Lex
tokens = Lexer(source).tokenize()

# Phase 2: Parse
ast = Parser(tokens).parse()

# Phase 3: Semantic Analysis
SemanticAnalyzer().visit(ast)

# Phase 4: Generate SSA IR
ir = IRBuilder().generate(ast)

# Phase 5: Optimize
ir = SSAConstProp().run(ir)
ir = SSAConstFold().run(ir)
ir = SSABranchSimplify().run(ir)
ir = SSADCE().run(ir)
ir = SSAUnreachableElim().run(ir)
ir = SSAPhiSimplify().run(ir)
ir = SSAJumpThread().run(ir)

# Phase 6: Lower to Bytecode
bytecode = SSAToBytecode().convert(ir)

# Phase 7: Execute
VM(bytecode).run()
# Output: 30
```

---

## Summary

Mini-LLVM is a **complete, working compiler** that takes Mini-Python source code through 7 distinct phases — from raw text to executed output. It demonstrates real compiler techniques including lexing with indentation tracking, recursive descent parsing, static semantic analysis with branch merging, SSA IR generation with Phi nodes, seven independent optimization passes, bytecode lowering with Phi resolution, and stack-based virtual machine execution. The entire system is tested end-to-end and written in pure Python with no dependencies.
