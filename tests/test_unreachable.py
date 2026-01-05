import unittest
import sys, os


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from optimizations.ssa_constprop import SSAConstProp
from optimizations.ssa_constfold import SSAConstFold
from optimizations.ssa_branch_simplify import SSABranchSimplify
from optimizations.ssa_dce import SSADCE
from optimizations.ssa_unreachable_elim import SSAUnreachableElim
from src.ir import Label, Phi, Const

class TestUnreachable(unittest.TestCase):

    def optimize(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)

        ir = SSAConstProp().run(ir)
        ir = SSAConstFold().run(ir)
        ir = SSABranchSimplify().run(ir)
        ir = SSADCE().run(ir)
        ir = SSAUnreachableElim().run(ir)

        return ir

    def test_if_true_else_removed(self):
        """
        if True:
           x = 1
        else:
           x = 2
        print(x)
        """
        src = """
if True:
    x = 1
else:
    x = 2
print(x)
"""
        ir = self.optimize(src)
        
        # Check that the block for 'else' is gone.
        # How to check? Labels.
        # IRBuilder names: L_else_1
        labels = [i.name for i in ir.instructions if isinstance(i, Label)]
        
        # Should have 'entry', 'L_then_1', 'L_merge_1'.
        # 'L_else_1' should be missing.
        
        self.assertTrue(any("else" in l for l in labels) == False, f"Else label found in {labels}")
        self.assertTrue(any("then" in l for l in labels), "Then label missing")

    def test_while_false_body_removed(self):
        """
        while False:
           x = 1
        print(0)
        """
        src = """
while False:
    x = 1
print(0)
"""
        ir = self.optimize(src)
        
        labels = [i.name for i in ir.instructions if isinstance(i, Label)]
        
        # Expect: entry, L_while_exit_1.
        # Missing: L_while_header_1 (maybe?), L_while_body_1.
        # Wait, Loop IR:
        # entry -> Jump Header
        # Header: if False -> Branch Body, Exit.
        # BranchSimplify: if False -> Jump Exit.
        # So Header -> Jump Exit.
        # Body is unreachable. Body removed.
        # Header is reachable from entry.
        # So Header remains.
        
        self.assertTrue(any("body" in l for l in labels) == False, f"Loop body label found in {labels}")
        self.assertTrue(any("header" in l for l in labels), "Loop header should be reachable via Jump from entry")

    def test_phi_cleanup(self):
        """
        if True:
           x = 1
        else:
           x = 2
        
        Original Phi at merge: phi(1 from then, 2 from else)
        After optimization: phi(1 from then) (else input removed)
        """
        src = """
if True:
    x = 1
else:
    x = 2
"""
        # x is not used, might be DCE'd?
        # But Phi might remain if not fully DCE'd or if I print x?
        # Let's print x to keep Phi alive.
        src += "print(x)"
        
        ir = self.optimize(src)
        
        phis = [i for i in ir.instructions if isinstance(i, Phi)]
        self.assertEqual(len(phis), 1)
        
        phi = phis[0]
        # Should have 1 input.
        self.assertEqual(len(phi.inputs), 1)
        
        # The input should be from the 'then' block.
        # We don't know the exact label name, but it shouldn't be 'else'.
        val, pred = phi.inputs[0]
        self.assertIn("then", pred)

if __name__ == "__main__":
    unittest.main()