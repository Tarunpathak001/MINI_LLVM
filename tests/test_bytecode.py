import unittest
import sys
import os
import io
from contextlib import redirect_stdout


from src.lexer import Lexer
from src.parser import Parser
from src.ir_builder import IRBuilder
from src.ssa_to_bytecode import SSAToBytecode
from src.bytecode_vm import VM

class TestBytecode(unittest.TestCase):
    def run_source(self, source):
        # 1. Pipeline
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        ir = IRBuilder().generate(ast)
        bytecode = SSAToBytecode().convert(ir)
        
        # 2. Execution capture
        vm = VM(bytecode)
        f = io.StringIO()
        with redirect_stdout(f):
            vm.run()
        return f.getvalue().strip()

    def test_simple_exec(self):
        """Test simple assignment and print"""
        src = """
x = 10
print(x)
"""
        out = self.run_source(src)
        self.assertEqual(out, "10")

    def test_branch_true(self):
        """Test 1 from Spec: If True condition"""
        src = """
x = 10
if x > 5:
    y = 1
else:
    y = 2
print(y)
"""
        out = self.run_source(src)
        self.assertEqual(out, "1")

    def test_branch_false(self):
        """Test 2 from Spec: If False condition"""
        src = """
x = 2
if x > 5:
    y = 1
else:
    y = 2
print(y)
"""
        out = self.run_source(src)
        self.assertEqual(out, "2")
        
    def test_nested_branch(self):
        """Test 3 from Spec: Nested If"""
        src = """
x = 10
if x > 5:
    if x > 8:
        y = 1
    else:
        y = 2
else:
    y = 3
print(y)
"""
        out = self.run_source(src)
        self.assertEqual(out, "1")

    def test_arithmetic(self):
        """Test math operations"""
        src = """
x = 10 + 5
print(x)
"""
        out = self.run_source(src)
        self.assertEqual(out, "15")

    def test_negative(self):
        """Test unary negation"""
        src = """
x = 5
y = -x
print(y)
"""
        out = self.run_source(src)
        self.assertEqual(out, "-5")
        
    def test_runtime_name_error(self):
        """Test 4 from Spec: Implicit usage undefined"""
        src = """
x = 10
if x > 5:
    y = 7
print(y)
"""
        out = self.run_source(src)
        self.assertEqual(out, "7")
        
        # Now test failure case: path where y not defined
        src_fail = """
x = 2
if x > 5:
    y = 7
# y undefined here
print(y)
"""
        # Phase 3 'semantic.py' would actually raise NameError STATICALLY before we run.
        # So we can't test runtime error unless we skip semantics.
        # The prompt said "Test 4 (No else)... Expected: Runtime NameError".
        # But per Phase 3 rules, this code is statically rejected!
        # "Phase 4 ... All tests from Phase 3 still pass".
        # If I run the full pipeline, Semantic Analysis runs?
        # My `run_source` helper skips Semantic Analysis (Lexer -> Parser -> IR ...).
        # So yes, we CAN test Runtime NameError because we bypassed static checks.
        
        with self.assertRaises(NameError):
            self.run_source(src_fail)

if __name__ == '__main__':
    unittest.main()