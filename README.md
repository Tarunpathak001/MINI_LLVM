# Mini-LLVM: A Minimal SSA-Based Compiler for Mini-Python

This project implements a from-scratch compiler pipeline for a Python-like language, designed to deeply understand how modern compilers work internally.

The compiler includes:

-   A hand-written lexer and recursive descent parser
-   Static semantic analysis
-   SSA-based intermediate representation
-   Control-flow handling (if, while)
-   Multiple SSA optimization passes
-   Bytecode lowering and a stack-based virtual machine

This is an educational but production-style compiler project.

## � Workflow and Command for the Project
[🚀 Project Workflow & Run Instructions](docs/work.md)

## �📌 Compiler Pipeline Overview

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

## 📂 Documentation by Phase

Each compiler phase is documented independently for clarity and depth.

### Language & Frontend

*   📘 [Language Specification](docs/language_spec.md)
*   📘 [Lexer Design](docs/lexer.md)
*   📘 [Parser & AST](docs/parser.md)

### Semantic Analysis

*   📘 [Semantic Rules & Type Checking](docs/semantic_analysis.md)

### Intermediate Representation

*   📘 [SSA IR Design](docs/ir_ssa.md)

### Code Generation

*   📘 [Bytecode & Virtual Machine](docs/bytecode_vm.md)

## ⚙️ Implemented Optimizations (SSA)

The compiler includes several SSA-based optimization passes:

*   Constant Propagation
*   Constant Folding
*   Branch Simplification
*   Dead Code Elimination
*   Unreachable Block Elimination
*   Phi Simplification
*   Jump Threading

Each optimization is implemented as a standalone pass and can be composed into a pipeline.

## 🚧 Project Status

**Status:** Initial Working Version (Frontend → SSA → VM complete)

All core compiler stages are implemented and fully tested. The project is structured for future extensions.

## 🔮 Planned Future Work

*   Control-flow graph (CFG) visualization
*   SSA register allocation
*   Bytecode optimization
*   Function definitions & calls
*   Source-level debugging support

## 🧪 Testing

All compiler stages are covered by unit tests located in the `tests/` directory.

## 🏁 Why This Project Exists

This project was built to:

*   Understand SSA form and Phi nodes deeply
*   Learn how control flow is lowered in compilers
*   Practice writing optimization passes
*   Bridge theory (compiler design) with real execution
