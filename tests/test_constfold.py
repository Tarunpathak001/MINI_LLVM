import unittest
import sys, os


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from optimizations.ssa_constfold import SSAConstFold
from src.ir import Const, BinaryOp

class TestConstFold(unittest.TestCase):

    def optimize(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)
        return SSAConstFold().run(ir)

    def test_simple_fold(self):
        src = """
x = 2
y = 3
z = x + y
"""
        ir = self.optimize(src)
        consts = [i for i in ir.instructions if isinstance(i, Const)]

        # z should be 5.
        # Check if there is a Const target matching 'z' (or z_version) with value 5
        # Since we don't know exact version, check values.
        # x=2, y=3, z=5.
        # Also intermediate temps might be constant.
        
        self.assertTrue(any(c.value == 5 for c in consts), "Did not find expected constant 5")

    def test_no_fold_partial(self):
        src = """
x = 2
y = a + x
"""
        ir = self.optimize(src)
        binops = [i for i in ir.instructions if isinstance(i, BinaryOp)]
        # Should still be a BinaryOp for y because 'a' is unknown (runtime error in semantics actually, but parser/ir allows structure if passed)
        # Actually semantics would fail 'a' access. 
        # But this test skips SemanticAnalyzer().
        # So 'a' is just a Load that returns "a"?
        # IRBuilder: visit_Variable -> returns get_current_def("a") -> "a" (if strict undefined not checked, as per my IRBuilder)
        # So 'a' is in IR as operand "a".
        # "a" is NOT in const_map.
        # So no fold.
        self.assertTrue(len(binops) > 0, "Partial folding reduced instruction incorrectly")

if __name__ == "__main__":
    unittest.main()