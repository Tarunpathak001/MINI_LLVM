import unittest
import sys, os


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from optimizations.ssa_constprop import SSAConstProp
from optimizations.ssa_constfold import SSAConstFold
from optimizations.ssa_branch_simplify import SSABranchSimplify
from optimizations.ssa_dce import SSADCE
from src.ir import Const, BinaryOp, Print

class TestDCE(unittest.TestCase):

    def optimize(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)

        ir = SSAConstProp().run(ir)
        ir = SSAConstFold().run(ir)
        ir = SSABranchSimplify().run(ir)
        ir = SSADCE().run(ir)

        return ir

    def test_remove_unused(self):
        """
        x = 1 (Const) -> Unused? No, used in z.
        y = 2 (Const) -> Unused? No, used in z.
        z = x + y -> target z. z is NEVER used.
        So z is dead.
        If z is dead, x and y might be dead if no other uses.
        Let's trace:
        z = x + y (DEAD). Removed.
        x, y no longer marked used by z.
        y = 2 (DEAD). Removed.
        x = 1 (DEAD). Removed.
        """
        src = """
x = 1
y = 2
z = x + y
"""
        ir = self.optimize(src)
        # Should be empty instructions? Except Entry label?
        # IRBuilder emits "entry" Label. Side-effect -> Kept.
        # But Prints/BinOps should be gone.
        
        # Check no Print
        prints = [i for i in ir.instructions if isinstance(i, Print)]
        self.assertEqual(len(prints), 0)
        
        # Check no BinaryOp
        binops = [i for i in ir.instructions if isinstance(i, BinaryOp)]
        self.assertEqual(len(binops), 0)

    def test_keep_used(self):
        src = """
x = 1
y = 2
z = x + y
print(z)
"""
        ir = self.optimize(src)
        prints = [i for i in ir.instructions if isinstance(i, Print)]
        self.assertEqual(len(prints), 1)
        
        # z is used by print.
        # Constant Folding turned 'z = 1 + 2' into 'z = 3' (Const).
        # So BinaryOp is gone. But Const(3) should be present (and x=1, y=2 might be dead if we track strictly? 
        # Wait, x and y are used by x+y in original, but if x+y became Const(3), x and y are no longer used by it.
        # So x=1 and y=2 should be DEAD and removed!
        # Only z=3 should remain.
        
        consts = [i for i in ir.instructions if isinstance(i, Const)]
        # We expect z=3.
        # Check for value 3.
        vals = [c.value for c in consts]
        self.assertIn(3, vals)
        
        # Verify x=1, y=2 are GONE (DCE working on folded dependencies!)
        self.assertNotIn(1, vals)
        self.assertNotIn(2, vals)

    def test_keep_control_flow(self):
        src = """
x = 1
if True:
    y = 2
print(x)
"""
        ir = self.optimize(src)
        # Entry label kept.
        # x=1 kept (printed).
        # if True -> Jump (by BranchSimplify). Jump kept.
        # y=2 -> dead.
        # print(x) kept.
        
        self.assertTrue(any(isinstance(i, Print) for i in ir.instructions))
        # y=2 should be gone (Const 2, Mov or whatever)
        # Const(2) might be gone.
        # Const(1) should be present.
        
        consts = [i for i in ir.instructions if isinstance(i, Const)]
        vals = [c.value for c in consts]
        self.assertIn(1, vals)
        self.assertNotIn(2, vals)

if __name__ == "__main__":
    unittest.main()