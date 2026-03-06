# Mini-LLVM: Phase Progress & Verification Report

> This document tracks the completion status of every phase in the Mini-LLVM compiler, what was implemented, what is verified, and how.

---

## Progress Summary

| Phase | Name                        | Status       | Tests | Verified |
|:-----:|:----------------------------|:------------:|:-----:|:--------:|
| 0     | Language Specification      | ✅ Complete  | —     | ✅       |
| 1     | Lexer (Tokenizer)           | ✅ Complete  | 7+    | ✅       |
| 2     | Parser & AST                | ✅ Complete  | 8+    | ✅       |
| 3     | Semantic Analysis           | ✅ Complete  | 10+   | ✅       |
| 4     | SSA IR Construction         | ✅ Complete  | 8+    | ✅       |
| 5     | SSA Optimization Passes (7) | ✅ Complete  | 15+   | ✅       |
| 6     | Bytecode Lowering           | ✅ Complete  | 8+    | ✅       |
| 7     | Stack-Based VM Execution    | ✅ Complete  | 8+    | ✅       |

**Total unit tests: 55 (all passing)**  
**Run command:** `python -m unittest discover -s tests`

---

## Phase 0 — Language Specification

**Status:** ✅ Complete

### Work Done
- Defined the Mini-Python language from scratch: types (`int`, `str`, `bool`, `NoneType`), statements (`assignment`, `print`, `if/else`, `while`), operators (`+`, `-`, `<`, `>`, `==`, `!=`), and error model.
- Wrote formal EBNF grammar.
- Documented intentional non-features (no functions, no truthiness, no `and`/`or`/`not`, no `for`, no `float`/`list`/`dict`).

### Verification
- The spec is documented in `docs/language_spec.md`.
- Every subsequent phase is built against this spec, so all tests implicitly verify it.

---

## Phase 1 — Lexer (Tokenizer)

**Status:** ✅ Complete  
**File:** `src/lexer.py`  
**Test file:** `tests/test_lexer.py`

### Work Done
- Hand-written lexer (no lexer generators).
- Tokenizes: keywords, identifiers, integers, strings, operators (`+`, `-`, `<`, `>`, `==`, `!=`, `=`), delimiters (`(`, `)`, `:`).
- Generates synthetic `INDENT`/`DEDENT` tokens from indentation level changes.
- Handles comments (`#`), blank lines, and `EOF`.
- Error handling: `IndentationError` for tabs, `SyntaxError` for unterminated strings and invalid characters.

### How It's Verified
| Test Case                          | What It Checks                                          |
|------------------------------------|---------------------------------------------------------|
| Simple assignment tokenization     | `IDENTIFIER`, `ASSIGN`, `INTEGER` token sequence        |
| If/else tokenization               | `IF`, `ELSE`, `COLON`, `INDENT`, `DEDENT` generation    |
| String literal tokenization        | Both `"double"` and `'single'` quoted strings            |
| Multi-line with indentation        | Correct `INDENT`/`DEDENT` emission across nested blocks  |
| Comment handling                   | `#` comments are stripped, don't produce tokens          |
| Operator tokenization              | Two-char (`==`, `!=`) and single-char (`+`, `-`, `<`, `>`) |
| Error: tabs                        | Raises `IndentationError`                                |

---

## Phase 2 — Parser & AST

**Status:** ✅ Complete  
**Files:** `src/parser.py`, `src/ast_nodes.py`  
**Test files:** `tests/test_parser.py`, `tests/test_parser_while.py`

### Work Done
- Recursive descent parser built from the EBNF grammar.
- Produces AST nodes: `Program`, `Assignment`, `Print`, `If`, `While`, `BinaryOp`, `UnaryOp`, `Literal`, `Variable`.
- Supports operator precedence: relations → addition → unary → primary.
- Block parsing via `INDENT`/`DEDENT` tokens.

### How It's Verified
| Test Case                         | What It Checks                                           |
|-----------------------------------|----------------------------------------------------------|
| Simple assignment parsing         | Produces `Assignment` with `Literal` value               |
| Print statement parsing           | Produces `Print` wrapping an expression                  |
| If/else parsing                   | Produces `If` node with `then_body` and `else_body`      |
| While loop parsing                | Produces `While` node with condition and body             |
| Binary expression parsing         | Correct `BinaryOp` structure, operator precedence        |
| Unary negation parsing            | `UnaryOp('-', ...)` node created                         |
| Nested if inside while            | Deep nesting produces correct tree structure             |
| Syntax errors                     | Invalid token raises `SyntaxError` with line number      |

---

## Phase 3 — Semantic Analysis

**Status:** ✅ Complete  
**File:** `src/semantic.py`  
**Test file:** `tests/test_semantic.py`

### Work Done
- Visitor-pattern traversal over the AST.
- Tracks `defined_vars` (set) and `var_types` (map).
- Enforces: variables defined before use, `if`/`while` condition must be `bool`, type-correct operators.
- Branch merging: variables only survive both branches; type conflicts remove variables.
- While loop: new variables don't survive loop scope.

### How It's Verified
| Test Case                              | What It Checks                                        |
|----------------------------------------|-------------------------------------------------------|
| Valid assignment + print               | No error raised                                       |
| Undefined variable use                 | Raises `NameError`                                    |
| `if` condition not boolean             | Raises `TypeError` (e.g., `if 1:`)                    |
| `+` with mixed types (int + str)       | Raises `TypeError`                                    |
| `<` with mixed types                   | Raises `TypeError`                                    |
| Variable defined in both branches      | Variable survives `if/else` merge                     |
| Variable defined in only one branch    | Variable does NOT survive merge                       |
| Variable reassigned to different type  | Type conflict removes variable from defined set       |
| Unary `-` on string                    | Raises `TypeError`                                    |
| While loop new variable visibility     | Variables inside loop don't leak out                  |

---

## Phase 4 — SSA IR Construction

**Status:** ✅ Complete  
**Files:** `src/ir.py`, `src/ir_builder.py`  
**Test files:** `tests/test_ir.py`, `tests/test_ir_loop.py`

### Work Done
- AST → SSA IR conversion using visitor pattern.
- SSA naming: per-variable version counters (`x_1`, `x_2`, ...).
- Temporaries for expression results (`t1`, `t2`, ...).
- Phi node insertion at `if/else` merge points and `while` loop headers.
- Control flow: `Label`, `Jump`, `Branch` instructions.
- Handles: linear code, `if/else`, nested `if`, `while` loops with backedges.

### How It's Verified
| Test Case                            | What It Checks                                         |
|--------------------------------------|--------------------------------------------------------|
| Linear code IR                       | `Const`, `Mov`, `BinaryOp`, `Print` emitted correctly  |
| SSA renaming (`x = 1; x = 2`)       | Produces `x_1` and `x_2` (unique names)                |
| If/else Phi structure                | Single `Phi` at `L_merge` with 2 inputs from branches  |
| No Phi for unmodified variables      | If `x` isn't changed in branches, no Phi emitted       |
| While loop IR                        | Loop header has Phi, body has backedge `Jump`           |
| While loop with reassignment         | Phi correctly merges pre-loop and body-end values       |
| Nested control flow                  | Correct Label/Jump/Branch structure                     |
| Entry label                          | First instruction is always `Label("entry")`            |

---

## Phase 5 — SSA Optimization Passes

**Status:** ✅ Complete (all 7 passes)  
**Directory:** `optimizations/`  
**Test files:** `tests/test_constprop.py`, `tests/test_constfold.py`, `tests/test_branch_simplify.py`, `tests/test_dce.py`, `tests/test_unreachable.py`, `tests/test_cleanup.py`

### 5.1 Constant Propagation (`ssa_constprop.py`)
**Verified in:** `tests/test_constprop.py`
| Test | Verification |
|------|-------------|
| Const tracking     | `const_map` records constants from `Const` instructions |
| Mov propagation    | Constants flow through `Mov` chains |
| Phi constant merge | Phi with all-equal constant inputs → target becomes constant |
| Non-constant Phi   | Phi with different inputs → target NOT marked constant |

### 5.2 Constant Folding (`ssa_constfold.py`)
**Verified in:** `tests/test_constfold.py`
| Test | Verification |
|------|-------------|
| `1 + 2` → `Const(3)`      | `BinaryOp` replaced with `Const` |
| `5 > 3` → `Const(True)`   | Comparison folded to boolean constant |
| `-5` folded                | `UnaryOp` on constant replaced with `Const` |
| Non-constant operands      | Instruction left unchanged |

### 5.3 Branch Simplification (`ssa_branch_simplify.py`)
**Verified in:** `tests/test_branch_simplify.py`
| Test | Verification |
|------|-------------|
| `if True:` → `Jump(then)`     | `Branch` replaced with `Jump` to true label |
| `if False:` → `Jump(else)`    | `Branch` replaced with `Jump` to false label |
| Non-constant condition         | `Branch` left unchanged |

### 5.4 Dead Code Elimination (`ssa_dce.py`)
**Verified in:** `tests/test_dce.py`
| Test | Verification |
|------|-------------|
| Unused `Const` removed         | `Const` with no readers is eliminated |
| Unused `BinaryOp` removed      | Computation result never used → removed |
| Used instructions kept          | `Print`, `Branch`, `Jump` always survive |
| Transitive liveness             | If `t2` uses `t1`, and `Print` uses `t2`, both survive |
| Phi node liveness               | Dead Phi removed, live Phi kept |

### 5.5 Unreachable Block Elimination (`ssa_unreachable_elim.py`)
**Verified in:** `tests/test_unreachable.py`
| Test | Verification |
|------|-------------|
| Reachable blocks kept           | Entry and connected blocks survive |
| Unreachable else removed        | `if True:` makes else block unreachable → removed |
| Phi inputs cleaned              | Phi inputs from deleted blocks are removed |
| CFG construction                | Correct successors for `Jump` and `Branch` |
| BFS reachability                | Only entry-reachable blocks survive |

### 5.6 Phi Simplification (`ssa_phi_simplify.py`)
**Verified in:** `tests/test_cleanup.py`
| Test | Verification |
|------|-------------|
| Single-input Phi → Mov          | After unreachable elim, Phi with 1 input becomes `Mov` |
| Multi-input Phi unchanged       | Phi with 2+ inputs left alone |

### 5.7 Jump Threading (`ssa_jump_thread.py`)
**Verified in:** `tests/test_cleanup.py`
| Test | Verification |
|------|-------------|
| Trivial block forwarding         | `Label A; Jump B` → jumps to A rewritten to B |
| Non-trivial blocks unchanged     | Blocks with real instructions not affected |
| Self-loop protection             | `Label A; Jump A` not threaded (infinite loop guard) |

### Full Pipeline Integration
**Verified in:** `tests/test_cleanup.py`
- Runs all 7 passes in sequence on complex programs.
- Verifies that combined optimizations produce correct, minimal IR.
- Checks that Phis become Movs, dead blocks are removed, and jumps are threaded.

---

## Phase 6 — Bytecode Lowering

**Status:** ✅ Complete  
**Files:** `src/bytecode.py`, `src/ssa_to_bytecode.py`  
**Test file:** `tests/test_bytecode.py`, `tests/test_bytecode_while.py`

### Work Done
- Designed 12-instruction stack-based bytecode ISA.
- SSA name stripping: `x_1` → `x`, `t1` → `t1`.
- Phi resolution: before each `Jump`, emit `Load`/`Store` to transfer correct Phi input.
- Error detection: `Branch` targets with Phi nodes require critical edge splitting (raises error).

### How It's Verified
| Test Case                        | What It Checks                                          |
|----------------------------------|---------------------------------------------------------|
| Simple assignment → bytecode     | `Push`, `Store`, `Load`, `Print` sequence correct       |
| If/else → bytecode               | `Branch`, `Label`, `Jump` structure in bytecode         |
| While loop → bytecode            | Loop backedge, Phi moves emitted before jumps           |
| End-to-end print output          | Captured stdout matches expected value                  |
| SSA stripping                    | `x_1` → `x`, `t1` → `t1` in bytecode names            |

---

## Phase 7 — Stack-Based VM Execution

**Status:** ✅ Complete  
**File:** `src/bytecode_vm.py`  
**Test files:** `tests/test_bytecode.py`, `tests/test_bytecode_while.py`

### Work Done
- Stack-based virtual machine with `stack`, `env`, and `ip`.
- Pre-scans labels for O(1) jump resolution.
- Executes all 12 bytecode instructions.
- Runtime error: `NameError` for undefined variables.

### How It's Verified
| Test Case                         | What It Checks                                         |
|-----------------------------------|--------------------------------------------------------|
| `x = 10; print(x)` → outputs `10` | Basic assignment and print work end-to-end            |
| `if x > 5: y = 1 else: y = 2`    | Correct branch taken, correct value printed            |
| Nested if/else                    | Multi-level branching executes correctly               |
| Arithmetic (`10 + 5`)             | Addition, stack operations correct                     |
| Unary negation (`-x`)            | `Neg` instruction works                                |
| While loop countdown              | Loop executes correct number of iterations             |
| While loop accumulation           | Variable accumulates across loop iterations            |
| Runtime NameError                 | Accessing undefined variable raises `NameError`        |

---

## Planned Future Work (Not Yet Started)

| Feature                           | Status       |
|-----------------------------------|:------------:|
| Control-flow graph visualization  | 🔲 Planned   |
| SSA register allocation           | 🔲 Planned   |
| Bytecode-level optimization       | 🔲 Planned   |
| Function definitions & calls      | 🔲 Planned   |
| Source-level debugging support     | 🔲 Planned   |

---

## How to Verify Everything

### Run All Tests
```bash
cd MINI_LLVM
python -m unittest discover -s tests
```
**Expected output:** `Ran 55 tests ... OK`

### Run Individual Phase Tests
```bash
# Phase 1: Lexer
python -m tests.test_lexer

# Phase 2: Parser
python -m tests.test_parser
python -m tests.test_parser_while

# Phase 3: Semantics
python -m tests.test_semantic

# Phase 4: IR Generation
python -m tests.test_ir
python -m tests.test_ir_loop

# Phase 5: Optimizations
python -m tests.test_constprop
python -m tests.test_constfold
python -m tests.test_branch_simplify
python -m tests.test_dce
python -m tests.test_unreachable
python -m tests.test_cleanup          # Full pipeline integration

# Phase 6 & 7: Bytecode + VM
python -m tests.test_bytecode
python -m tests.test_bytecode_while
```

All 55 tests pass as of the latest run.
