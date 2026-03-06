"""
compiler_driver.py — Central orchestrator for the Mini-LLVM compiler pipeline.

This module wraps the existing compiler phases without modifying them.
It provides individual stage methods and full pipeline helpers.

Usage Example:
    from src.compiler_driver import CompilerDriver

    source = '''
    x = 10
    y = 20
    print(x + y)
    '''

    driver = CompilerDriver()

    # Full pipeline — returns all intermediate results
    result = driver.compile(source)
    print(result["tokens"])
    print(result["bytecode"])

    # Compile and execute in one call
    driver.run(source)   # prints: 30
"""

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


class CompilerDriver:
    """
    Non-intrusive wrapper that orchestrates the full Mini-LLVM compiler pipeline.

    Each stage can be called individually for inspection, or the full
    pipeline can be invoked via compile() / run().
    """

    # ── Individual Stage Methods ──────────────────────────────────

    def lex(self, source):
        """Phase 1: Source string → list of Tokens."""
        return Lexer(source).tokenize()

    def parse(self, tokens):
        """Phase 2: Token list → AST (Program node)."""
        return Parser(tokens).parse()

    def semantic(self, ast):
        """Phase 3: Validate AST semantics (raises on error). Returns the AST unchanged."""
        SemanticAnalyzer().visit(ast)
        return ast

    def build_ir(self, ast):
        """Phase 4: AST → SSA Intermediate Representation (IRProgram)."""
        return IRBuilder().generate(ast)

    def optimize(self, ir):
        """Phase 5: Apply all SSA optimization passes. Returns optimized IRProgram."""
        ir = SSAConstProp().run(ir)
        ir = SSAConstFold().run(ir)
        ir = SSABranchSimplify().run(ir)
        ir = SSADCE().run(ir)
        ir = SSAUnreachableElim().run(ir)
        ir = SSAPhiSimplify().run(ir)
        ir = SSAJumpThread().run(ir)
        return ir

    def lower(self, ir):
        """Phase 6: SSA IR → stack-based bytecode (list of BCInstr)."""
        return SSAToBytecode().convert(ir)

    def execute(self, bytecode):
        """Phase 7: Execute bytecode on the stack-based VM."""
        VM(bytecode).run()

    # ── Full Pipeline Helpers ─────────────────────────────────────

    def compile(self, source):
        """
        Run the full compilation pipeline (Phases 1–6) and return all
        intermediate results for inspection.

        Returns:
            dict with keys: "tokens", "ast", "ir", "optimized_ir", "bytecode"
        """
        tokens = self.lex(source)
        ast = self.parse(tokens)
        self.semantic(ast)
        ir = self.build_ir(ast)
        optimized_ir = self.optimize(ir)
        bytecode = self.lower(optimized_ir)

        return {
            "tokens": tokens,
            "ast": ast,
            "ir": ir,
            "optimized_ir": optimized_ir,
            "bytecode": bytecode,
        }

    def run(self, source):
        """
        Compile and execute a Mini-Python program end-to-end.
        Equivalent to compile() followed by execute().
        """
        result = self.compile(source)
        self.execute(result["bytecode"])
        return result
