# Mini-LLVM: A Minimal SSA-Based Compiler for Mini-Python

This project implements a from-scratch compiler pipeline for a Python-like language, designed to deeply understand how modern compilers work internally.

The compiler includes:

-   A hand-written lexer and recursive descent parser
-   Static semantic analysis with type checking
-   SSA-based intermediate representation with Phi nodes
-   Pretty printers for tokens, AST, and SSA IR
-   Control-flow handling (`if/else`, `while`)
-   Multiple SSA optimization passes
-   Bytecode lowering and a stack-based virtual machine
-   A central compiler driver for pipeline orchestration

This is an educational but production-style compiler project.

## 🚀 Quick Start

```bash
git clone https://github.com/Tarunpathak001/MINI_LLVM.git
cd MINI_LLVM
python requirement.py
python -m unittest discover -s tests
```

For full workflow and detailed run instructions, see [📋 Project Workflow & Run Instructions](docs/work.md).

## 📌 Compiler Pipeline Overview

```
Source Code
   ↓
Lexer (tokens)
   ↓
Parser (AST)
   ↓
Semantic Analysis
   ↓
SSA IR Construction
   ↓
SSA Optimizations
   ↓
Bytecode Lowering
   ↓
Stack-Based Virtual Machine
```

## 💻 Usage Example

```python
from src.compiler_driver import CompilerDriver

source = """
x = 5
y = 10
if x < y:
    print(x + y)
else:
    print(0)
"""

driver = CompilerDriver()
driver.run(source)  # Output: 15
```

## Pretty Printers

Phase 2 adds human-readable printers for:

-   Tokens
-   AST
-   SSA IR

Run the printer verification script with:

```bash
python verify_printers.py
```

Expected output sections:

-   `=== TOKENS ===`
-   `=== AST ===`
-   `=== IR ===`

## 📂 Documentation

Each compiler phase is documented independently for clarity and depth.

### Language & Frontend

| Phase | Document | Description |
|:-----:|----------|-------------|
| 0 | [Language Specification](docs/language_spec.md) | Types, operators, grammar, scoping rules, error model |
| 1 | [Lexer Design](docs/lexer.md) | Tokenization, indentation handling, INDENT/DEDENT tokens |
| 2 | [Parser & AST](docs/parser.md) | Recursive descent parsing, operator precedence, AST nodes |

### Analysis & IR

| Phase | Document | Description |
|:-----:|----------|-------------|
| 3 | [Semantic Analysis](docs/semantic_analysis.md) | Type checking, scope validation, branch merging rules |
| 4 | [SSA IR Design](docs/ir_ssa.md) | SSA form, Phi nodes, control-flow lowering |

### Backend

| Phase | Document | Description |
|:-----:|----------|-------------|
| 5-6 | [Bytecode & Virtual Machine](docs/bytecode_vm.md) | Bytecode ISA, SSA lowering, stack-based VM execution |

### Project

| Document | Description |
|----------|-------------|
| [Workflow & Run Instructions](docs/work.md) | Setup, running tests, how each phase works end-to-end |

## ⚙️ Implemented Optimizations (SSA)

The compiler includes seven SSA-based optimization passes:

| Pass | What It Does |
|------|-------------|
| Constant Propagation | Tracks constant values through SSA variables and Phi nodes |
| Constant Folding | Pre-evaluates constant expressions (`1 + 2` → `3`) |
| Branch Simplification | Converts `if True` / `if False` to unconditional `Jump` |
| Dead Code Elimination | Worklist-based liveness analysis, removes unused instructions |
| Unreachable Block Elimination | BFS reachability from entry, removes dead blocks, cleans Phi inputs |
| Phi Simplification | Converts single-input Phi nodes to `Mov` |
| Jump Threading | Shortcuts trivial forwarding blocks (`Label A → Jump B`) |

Each optimization is implemented as a standalone pass and can be composed into a pipeline.

## 📁 Project Structure

```
MINI_LLVM/
├── src/                          # Core compiler
│   ├── lexer.py                  # Tokenizer
│   ├── ast_nodes.py              # AST node definitions
│   ├── parser.py                 # Recursive descent parser
│   ├── semantic.py               # Semantic analyzer
│   ├── ir.py                     # IR instruction definitions
│   ├── ir_builder.py             # AST → SSA IR converter
│   ├── bytecode.py               # Bytecode instruction definitions
│   ├── ssa_to_bytecode.py        # SSA IR → Bytecode lowering
│   ├── bytecode_vm.py            # Stack-based VM
│   └── compiler_driver.py        # Pipeline orchestrator
│
├── optimizations/                # SSA optimization passes
│   ├── ssa_constprop.py
│   ├── ssa_constfold.py
│   ├── ssa_branch_simplify.py
│   ├── ssa_dce.py
│   ├── ssa_unreachable_elim.py
│   ├── ssa_phi_simplify.py
│   └── ssa_jump_thread.py
│
├── tests/                        # Unit tests (55 tests)
├── docs/                         # Phase documentation
├── README.md
├── LICENSE.md
└── SECURITY.md
```

## 🧪 Testing

All compiler stages are covered by **55 unit tests** in the `tests/` directory.

```bash
# Run all tests
python -m unittest discover -s tests

# Run a specific phase
python -m tests.test_lexer
python -m tests.test_parser
python -m tests.test_semantic
python -m tests.test_ir
python -m tests.test_bytecode
python -m tests.test_cleanup    # Full pipeline integration
```

## Phase 2 Completion Checklist

Use these commands to confirm the pretty printer phase is complete:

```bash
python verify_printers.py
python -m unittest discover -s tests
git log --oneline -2
git status --short
```

Expected confirmation signals:

-   `python verify_printers.py` shows `=== TOKENS ===`, `=== AST ===`, and `=== IR ===`
-   `python -m unittest discover -s tests` reports `Ran 55 tests` and `OK`
-   `git log --oneline -2` includes:
    `83b5686 refactor: harden pretty printer edge cases`
    `400e991 feat: add token, AST, and SSA IR pretty printers`
-   `git status --short` prints nothing

## 🚧 Project Status

**Status:** Core Pipeline Complete (Frontend → SSA → Optimizations → VM)

All compiler stages are implemented, optimized, and fully tested. The project is structured for future extensions.

## 🔮 Planned Future Work

-   Control-flow graph (CFG) visualization
-   SSA register allocation
-   Bytecode optimization
-   Function definitions & calls
-   Source-level debugging support

## 🏁 Why This Project Exists

This project was built to:

-   Understand SSA form and Phi nodes deeply
-   Learn how control flow is lowered in compilers
-   Practice writing real optimization passes
-   Bridge theory (compiler design) with real execution


Made in patnership with Adrak wali chai ☕...
