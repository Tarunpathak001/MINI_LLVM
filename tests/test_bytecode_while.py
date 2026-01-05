import unittest
import sys, os, io
from contextlib import redirect_stdout


from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.ir_builder import IRBuilder
from src.ssa_to_bytecode import SSAToBytecode
from src.bytecode_vm import VM

class TestBytecodeWhile(unittest.TestCase):

    def run_src(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().visit(ast)
        ir = IRBuilder().generate(ast)
        bc = SSAToBytecode().convert(ir)
        vm = VM(bc)
        f = io.StringIO()
        with redirect_stdout(f):
            vm.run()
        return f.getvalue().strip()

    def test_simple_while(self):
        src = """
x = 0
while x < 3:
    x = x + 1
print(x)
"""
        self.assertEqual(self.run_src(src), "3")

    def test_nested_while(self):
        src = """
x = 0
y = 0
while x < 2:
    y = 0
    while y < 2:
        y = y + 1
    x = x + 1
print(x)
print(y)
"""
        out = self.run_src(src).splitlines()
        self.assertEqual(out, ["2", "2"])

    def test_while_not_entered(self):
        src = """
x = 5
while x < 3:
    x = x + 1
print(x)
"""
        self.assertEqual(self.run_src(src), "5")

if __name__ == "__main__":
    unittest.main()