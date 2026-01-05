import unittest
import sys
import os


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from optimizations.ssa_constprop import SSAConstProp
from src.ir import BinaryOp, UnaryOp, Const, Mov

class TestConstProp(unittest.TestCase):
    def optimize(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)
        opt = SSAConstProp()
        return opt.run(ir)

    def test_simple_analysis(self):
        """
        x = 2
        y = x + 3
        
        Analysis should find x=2.
        IR should remain safe (no literals in operands).
        """
        src = """
x = 2
y = x + 3
"""
        new_ir = self.optimize(src)
        instrs = new_ir.instructions
        
        # Check that BinaryOp still uses SSA names, not literals
        binops = [i for i in instrs if isinstance(i, BinaryOp)]
        self.assertTrue(len(binops) > 0)
        
        for b in binops:
            if b.op == 'add':
                # Operands should be STRINGS (SSA names)
                self.assertIsInstance(b.left, str, "Operand 'left' must be SSA name string")
                self.assertIsInstance(b.right, str, "Operand 'right' must be SSA name string")
                
                # And NOT literals 2 or 3
                self.assertNotEqual(b.left, 2)
                self.assertNotEqual(b.right, 3)

    def test_no_folding(self):
        """
        Ensure 2 + 3 is NOT folded to 5
        """
        src = """
x = 2
y = x + 3
"""
        new_ir = self.optimize(src)
        instrs = new_ir.instructions
        
        # Should NOT find Const(..., 5)
        for i in instrs:
            if isinstance(i, Const) and i.value == 5:
                self.fail("Premature constant folding detected")

if __name__ == '__main__':
    unittest.main()