import unittest
import sys
import os


from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer

class TestSemantic(unittest.TestCase):
    def check(self, source):
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)

    def test_valid_assignment(self):
        self.check("x = 10\nprint(x)")

    def test_name_error_simple(self):
        with self.assertRaises(NameError):
            self.check("print(x)")

    def test_name_error_conditional(self):
        """Variable defined only in if, not guaranteed"""
        src = """
if True:
    x = 10
print(x)
"""
        with self.assertRaises(NameError):
            self.check(src)

    def test_valid_conditional_merge(self):
        """Variable defined in both branches"""
        src = """
if True:
    x = 10
else:
    x = 20
print(x)
"""
        self.check(src)

    def test_valid_conditional_merge_types(self):
        """Variable with consistent type in both branches"""
        src = """
if True:
    x = 10
else:
    x = 20
# x is int
z = x + 5
"""
        self.check(src)

    def test_invalid_merge_types(self):
        """Variable with inconsistent types -> NameError on use"""
        # Because we treat conflicted merges as 'undefined' for safety
        src = """
if True:
    x = 10
else:
    x = "hello"
print(x) 
"""
        with self.assertRaises(NameError):
            self.check(src)

    def test_type_error_binary(self):
        with self.assertRaises(TypeError):
            self.check("x = 'a' + 1")

    def test_type_error_unary(self):
        with self.assertRaises(TypeError):
            self.check("x = -'a'")
            
    def test_type_error_if_condition(self):
        with self.assertRaises(TypeError):
            self.check("if 10:\n    x=1")

    def test_nested_scope_valid(self):
        src = """
x = 1
if 1 < 2:
    if 3 < 4:
        y = 1
    else:
        y = 2
    # y is guaranteed here
    z = y + x
"""
        self.check(src)

    def test_pre_if_vars_survive(self):
        """Test that variables defined before if block survive the merge"""
        src = """
x = 10
if True:
    y = 1
else:
    y = 2
print(x)
"""
        self.check(src)

    def test_if_without_else_keeps_prior_vars(self):
        """Test that if-without-else doesn't destroy prior scope"""
        src = """
x = 1
if True:
    y = 2
print(x)
"""
        self.check(src)

    def test_while_loop_var_not_guaranteed(self):
        """Test 1: Variable defined in loop is not guaranteed after"""
        src = """
while x < 5:
    y = 1
print(y)
"""
        # x is undefined, so check specific NameError first?
        # No, let's define x first to isolate y's error.
        src_fixed = """
x = 0
while x < 5:
    y = 1
print(y)
"""
        with self.assertRaises(NameError) as cm:
            self.check(src_fixed)
        self.assertIn("variable 'y' may be used before assignment", str(cm.exception))

    def test_while_loop_existing_var_ok(self):
        """Test 2: Existing variable updated in loop is OK"""
        src = """
x = 0
y = 0
while x < 5:
    y = y + 1
print(y)
"""
        self.check(src) # Should pass

    def test_while_loop_nested_if_var_not_guaranteed(self):
        """Test 3: Variable in nested if in while is not guaranteed"""
        src = """
x = 0
while x < 5:
    if x > 2:
        z = x
print(z)
"""
        with self.assertRaises(NameError):
            self.check(src)
            
    def test_while_condition_must_be_bool(self):
        """Test 4: While condition type check"""
        src = """
while 1:
    x = 1
"""
        # 1 is int, not bool.
        with self.assertRaises(TypeError):
            self.check(src)

if __name__ == '__main__':
    unittest.main()