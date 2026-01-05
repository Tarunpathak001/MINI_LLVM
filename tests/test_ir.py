import unittest
import sys
import os


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from src.ir import (
    Const, BinaryOp, UnaryOp, Phi,
    Label, Jump, Branch, Print, Mov
)

class TestIR(unittest.TestCase):
    def build_ir(self, source):
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        builder = IRBuilder()
        return builder.generate(ast)

    def test_linear_code(self):
        """Test simple assignment and math"""
        src = """
x = 1
y = 2
z = x + y
print(z)
"""
        ir = self.build_ir(src)
        insts = ir.instructions
        
        # Consts for 1 and 2
        # Movs for x and y
        # BinaryOp for +
        # Mov for z
        # Print
        
        movs = [i for i in insts if isinstance(i, Mov)]
        self.assertTrue(len(movs) >= 3) # x=, y=, z=
        
        adds = [i for i in insts if isinstance(i, BinaryOp)]
        self.assertEqual(len(adds), 1)
        self.assertEqual(adds[0].op, 'add')
        
    def test_ssa_renaming_explicit(self):
        """Test explicit SSA renaming (x_1, x_2) using Option A (Mov)"""
        src = """
x = 1
x = 2
print(x)
"""
        ir = self.build_ir(src)
        movs = [i for i in ir.instructions if isinstance(i, Mov)]
        
        # x_1 = ...
        # x_2 = ...
        targets = [m.target for m in movs if m.target.startswith("x_")]
        self.assertTrue(len(targets) >= 2)
        self.assertNotEqual(targets[0], targets[1])
        
        # Check numbering convention
        self.assertTrue(targets[0].endswith("_1"))
        self.assertTrue(targets[1].endswith("_2"))

    def test_if_phi_structure(self):
        """Test Phi node insertion and structure"""
        src = """
if True:
    x = 1
else:
    x = 2
print(x)
"""
        ir = self.build_ir(src)
        phis = [i for i in ir.instructions if isinstance(i, Phi)]
        self.assertEqual(len(phis), 1)
        
        phi = phis[0]
        self.assertEqual(len(phi.inputs), 2)
        
        # Assertion: Phi target is a new version
        self.assertTrue(phi.target.startswith("x_"))
        
        # Assertion: Phi appears immediately after Label
        idx = ir.instructions.index(phi)
        self.assertIsInstance(ir.instructions[idx-1], Label)
        self.assertTrue(ir.instructions[idx-1].name.startswith("L_merge"))

    def test_no_bad_phi(self):
        """Ensure Phi is NOT generated for unmodified variables"""
        src = """
x = 10
if True:
    print(x)
else:
    print(x)
# x is untouched
print(x)
"""
        ir = self.build_ir(src)
        phis = [i for i in ir.instructions if isinstance(i, Phi)]
        self.assertEqual(len(phis), 0)

if __name__ == '__main__':
    unittest.main()