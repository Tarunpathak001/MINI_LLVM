import unittest
import sys, os


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from optimizations.ssa_constprop import SSAConstProp
from optimizations.ssa_constfold import SSAConstFold
from optimizations.ssa_branch_simplify import SSABranchSimplify
from src.ir import Branch, Jump

class TestBranchSimplify(unittest.TestCase):

    def optimize(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)

        # Optimization pipeline
        ir = SSAConstProp().run(ir)
        ir = SSAConstFold().run(ir)
        ir = SSABranchSimplify().run(ir)

        return ir

    def test_branch_true(self):
        src = """
x = 1
if True:
    x = 2
else:
    x = 3
print(x)
"""
        ir = self.optimize(src)

        branches = [i for i in ir.instructions if isinstance(i, Branch)]
        jumps = [i for i in ir.instructions if isinstance(i, Jump)]

        # Should have NO branches (converted to Jump)
        self.assertEqual(len(branches), 0, "Branch instruction remained despite constant True condition")
        # Should have Jumps (from if/else structure + the new jump)
        self.assertTrue(len(jumps) > 0)

    def test_branch_false(self):
        src = """
x = 1
if False:
    x = 2
else:
    x = 3
print(x)
"""
        ir = self.optimize(src)

        branches = [i for i in ir.instructions if isinstance(i, Branch)]
        jumps = [i for i in ir.instructions if isinstance(i, Jump)]

        self.assertEqual(len(branches), 0, "Branch instruction remained despite constant False condition")
        self.assertTrue(len(jumps) > 0)

if __name__ == "__main__":
    unittest.main()