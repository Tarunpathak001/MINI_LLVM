# test_cleanup.py
import unittest
import sys, os
import io
from contextlib import redirect_stdout


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
from src.ir import Mov, Jump, Label, Phi

class TestCleanup(unittest.TestCase):

    def full_optimize(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)

        ir = SSAConstProp().run(ir)
        ir = SSAConstFold().run(ir)
        ir = SSABranchSimplify().run(ir)
        ir = SSADCE().run(ir)
        ir = SSAUnreachableElim().run(ir)
        ir = SSAPhiSimplify().run(ir)
        ir = SSAJumpThread().run(ir)

        return ir

    def run_optimized(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().visit(ast)
        ir = IRBuilder().generate(ast)

        ir = SSAConstProp().run(ir)
        ir = SSAConstFold().run(ir)
        ir = SSABranchSimplify().run(ir)
        ir = SSADCE().run(ir)
        ir = SSAUnreachableElim().run(ir)
        ir = SSAPhiSimplify().run(ir)
        ir = SSAJumpThread().run(ir)

        bc = SSAToBytecode().convert(ir)
        vm = VM(bc)
        out = io.StringIO()
        with redirect_stdout(out):
            vm.run()
        return out.getvalue().strip()

    def test_phi_simplify(self):
        """
        Phi with single input should become Mov.
        Steps:
        1. if True ... else ...
        2. Else unreachable.
        3. Merge Phi loses else input.
        4. Phi has 1 input -> Mov.
        """
        src = """
x = 0
if True:
    x = 1
else:
    x = 2
print(x)
"""
        # IR flow:
        # Phi(x_3, [(x_1, then), (x_2, else)])
        # UnreachableElim removes else block and input.
        # Phi(x_3, [(x_1, then)])
        # PhiSimplify -> Mov(x_3, x_1) (or val 1)
        
        ir = self.full_optimize(src)
        
        # Check NO Phis
        phis = [i for i in ir.instructions if isinstance(i, Phi)]
        self.assertEqual(len(phis), 0)
        
        # Check Mov exists (x_3 = 1 or similar)
        # Depending on ConstProp, x_1 might be 1.
        # So Mov could be Mov(x_3, 1) or Mov(x_3, x_1)
        movs = [i for i in ir.instructions if isinstance(i, Mov)]
        self.assertTrue(len(movs) > 0)

    def test_jump_thread(self):
        """
        Jump threading must not break Phi predecessor labels when a trivial
        forwarding block jumps into a loop header that begins with Phi nodes.
        """
        src = """
x = 2
y = 1
if x > 0:
    while y < 3:
        if y < 2:
            print("inner")
        else:
            print("edge")
        y = y + 1
else:
    print("skip")
"""
        self.assertEqual(self.run_optimized(src).splitlines(), ["inner", "edge"])

if __name__ == "__main__":
    unittest.main()
