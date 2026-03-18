# Bytecode & Virtual Machine | Mini-LLVM

**Status:** Completed  
**Lowering:** `ssa_to_bytecode.py`  
**VM:** `bytecode_vm.py`  
**Definitions:** `bytecode.py`

This phase lowers the SSA IR into a stack-based bytecode and executes it.

---

## 1. Stack Machine Model

- **Stack:** Used for operands and results.
    - `Add`: Pops `b`, `a`. Pushes `a+b`.
- **Environment:** Dictionary `env` stores variables by name (SSA indices removed).
- **Control Flow:** `Jump` and `Branch` modify the Instruction Pointer (`ip`).

## 2. SSA Lowering (Phi Elimination)

SSA names (`x_1`) are stripped to base names (`x`).
Phi nodes are removed by emitting `Store` instructions in the predecessor blocks.

**Example:**
IR:
```
L_then: ... jump L_merge
L_merge: x_3 = phi(x_1, L_then)...
```

Bytecode:
```
L_then:
  Load x (value of x_1)
  Store x (value of x_3)
  Jump L_merge
```

## 3. Instruction Set

| Op | Semantics |
|---|---|
| `Push v` | Push literal `v` |
| `Load n` | Push `env[n]` |
| `Store n` | Pop `v`, `env[n] = v` |
| `Add` | Pop `b, a`, Push `a+b` |
| `Lt/Gt` | Compare top two items |
| `Neg` | Negate top item |
| `Jump T` | `ip = labels[T]` |
| `Branch T F`| Pop `c`. If `c`: `ip=T` else: `ip=F` |
| `Print` | Pop `v`, print(v) |
