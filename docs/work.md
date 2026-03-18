# Project Workflow & Run Instructions

## 📋 Requirements
-   **Python 3.8+**: Correctly installed and added to your system PATH.
-   **Standard Library Only**: No external dependencies (pip install not required).
-   **Operating System**: Cross-platform (Windows, macOS, Linux).

## 🚀 Getting Started

### 1. Clone the Repository
Get the code from GitHub:
```bash
git clone https://github.com/Tarunpathak001/MINI_LLVM.git
cd MINI_LLVM
```

### 2. Install Requirements
Run the setup script to install dependencies (if any) and prepare the environment:
```bash
python requirement.py
```

## 🏃 How to Run
This project is structured as a Python package. You must run commands from the project root directory.

### Running Tests
To verify the entire compiler pipeline:
```bash
# Run all tests
python -m unittest discover -s tests

# (Optional) Run a specific test module
python -m tests.test_branch_simplify  # Verifies Branch Simplification optimization (Branch -> Jump)
python -m tests.test_bytecode         # Tests basic bytecode generation and logic
python -m tests.test_bytecode_while   # Tests while loop bytecode execution in VM
python -m tests.test_cleanup          # Verifies full optimization pipeline final cleanup
python -m tests.test_constfold        # Tests Constant Folding optimization (1+2 -> 3)
python -m tests.test_constprop        # Tests Constant Propagation analysis logic
python -m tests.test_dce              # Verifies Dead Code Elimination optimization
python -m tests.test_ir               # Tests basic SSA IR generation structure
python -m tests.test_ir_loop          # Verifies IR generation for while loops
python -m tests.test_lexer            # Tests tokenization of source code string
python -m tests.test_parser           # Tests AST construction from tokens
python -m tests.test_parser_while     # Tests parsing logic for while loops
python -m tests.test_semantic         # Verifies semantic analysis and scope checks
python -m tests.test_unreachable      # Tests removal of unreachable code blocks
```

### Running the Pretty Printer Verification
To inspect the human-readable compiler views added in Phase 2:
```bash
python verify_printers.py
```

This prints:
- `=== TOKENS ===`
- `=== AST ===`
- `=== IR ===`


### Running the Compiler (Example Usage)
Currently, the compiler is driver-driven via tests. To see the compiler in action on custom code, you can inspect `tests/test_cleanup.py` which runs the full pipeline.

---

## 🛠️ Workflow Steps (How it Works)

### Step 1: Lexical Analysis (Lexer)
**Work**: The `Lexer` reads the raw source code string and breaks it down into a stream of tokens (like `IF`, `IDENTIFIER`, `INTEGER`).
**Gist**:
-   Scans input character by character.
-   Groups characters into meaningful tokens.
-   Handles whitespace and indentation (critical for Python-like syntax).
-   Discards comments and empty lines.
-   Output: List of `Token` objects.

### Step 2: Parsing (Parser)
**Work**: The `Parser` takes the token stream and builds an Abstract Syntax Tree (AST) that represents the grammatical structure.
**Gist**:
-   Recursive descent parser implementation.
-   Validates syntax rules (e.g., `if` must be followed by `condition` and `colon`).
-   Constructs nodes like `IfStmt`, `WhileStmt`, `BinOp`, `Assignment`.
-   Enforces operator precedence (e.g., `*` before `+`).
-   Output: Hierarchical `AST`.

### Step 2.5: Pretty Printing
**Work**: Optional helpers render compiler structures in a human-readable form for debugging and inspection.
**Gist**:
-   `TokenPrinter` formats tokens compactly.
-   `ASTPrinter` renders the parsed tree with indentation.
-   `IRPrinter` renders SSA instructions in readable textual form.
-   Used by `verify_printers.py` and later user-facing tooling.

### Step 3: Semantic Analysis
**Work**: Validates the meaning of the code before compilation, checking for logical errors that syntax ignores.
**Gist**:
-   Traverses the AST to check variable scopes.
-   Ensures variables are defined before use.
-   Checks for redeclarations or invalid operations.
-   Maintains a symbol table for scope tracking.
-   Output: Validated AST (raises error if invalid).

### Step 4: SSA IR Generation (IR Builder)
**Work**: Converts the AST into Static Single Assignment (SSA) Intermediate Representation.
**Gist**:
-   Lowers high-level constructs into linear instructions.
-   Manages control flow via `Jump`, `Branch`, and `Label`.
-   Enforces SSA property: every variable assigned exactly once.
-   Inserts `Phi` nodes at control flow merge points (loop headers, if-exits).
-   Output: `IRProgram` with unoptimized instructions.

### Step 5: SSA Optimizations
**Work**: A multi-pass pipeline to analyze and improve the IR without changing behavior.
**Gist**:
-   **Constant Propagation**: Tracks constant values through variables.
-   **Constant Folding**: Pre-calculates `1 + 2` -> `3`.
-   **Branch Simplification**: Converts `if True` to direct `Jump`.
-   **Dead Code Elimination**: Removes unused instructions.
-   **Unreachable Block Elimination**: Removes dead code blocks (like `else` of `if True`).
-   **CFG Cleanup**: Simplifies Phi nodes and shortcuts Jumps.

### Step 6: Code Generation (Bytecode)
**Work**: lowers the optimized High-Level IR into a low-level stack-based bytecode.
**Gist**:
-   Maps SSA variables to logic.
-   Translates `BinaryOp` to stack commands (`LOAD`, `ADD`, `STORE`).
-   Resolve Labels to instruction indices (or keeps symbolic labels for VM).
-   Prepares the code for execution on the virtual machine.
-   Output: List of Bytecode instructions.

### Step 7: Virtual Machine Execution
**Work**: Executes the bytecode instructions to run the user's program.
**Gist**:
-   Stack-based architecture (Push/Pop).
-   Maintains variable storage (environment).
-   Executes opcodes: `LOAD_CONST`, `ADD`, `PRINT`, `JMP_IF_FALSE`.
-   Handles program flow and output.
-   Result: The actual output of the program (e.g., printed numbers).
