# Security Policy

## Supported Versions

Use the latest version of this project to ensure you have the most up-to-date security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |


## Reporting Vulnerabilities

Please do not open public issues for security vulnerabilities.

Instead, report them privately via email:
- pathaktarun431@gmail.com

## Scope

Mini-LLVM is an educational project intended to demonstrate compiler design
and SSA optimization concepts using Python.

It is **not designed for production use** or for running untrusted workloads.

## Security Considerations

The project explores mechanisms such as:
- Recursive descent parsing
- Static Single Assignment (SSA) form
- Optimization passes (DCE, Folding)
- Stack-based virtual machine

These are provided for learning purposes and may be incomplete.

For production compiler needs, use established projects such as:
- LLVM
- GCC
- CPython
- PyPy
