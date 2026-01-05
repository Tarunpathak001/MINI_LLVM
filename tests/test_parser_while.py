import unittest
import sys
import os


from src.lexer import Lexer
from src.parser import Parser
from src.ast_nodes import While, If, Assignment, BinaryOp, Variable, Literal

class TestParserWhile(unittest.TestCase):
    def parse(self, source):
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()

    def test_simple_while(self):
        """Test simple while loop parsing"""
        src = """
while x < 5:
    x = x + 1
"""
        ast = self.parse(src)
        self.assertEqual(len(ast.statements), 1)
        while_stmt = ast.statements[0]
        self.assertIsInstance(while_stmt, While)
        self.assertIsInstance(while_stmt.condition, BinaryOp)
        self.assertEqual(len(while_stmt.body), 1)
        self.assertIsInstance(while_stmt.body[0], Assignment)

    def test_while_nested_if(self):
        """Test while loop containing if statement"""
        src = """
while True:
    if x > 0:
        x = x + -1
"""
        ast = self.parse(src)
        while_stmt = ast.statements[0]
        self.assertIsInstance(while_stmt, While)
        self.assertIsInstance(while_stmt.body[0], If)

    def test_nested_while(self):
        """Test nested while loops"""
        src = """
while x > 0:
    while y > 0:
        y = y + -1
"""
        ast = self.parse(src)
        outer = ast.statements[0]
        self.assertIsInstance(outer, While)
        inner = outer.body[0]
        self.assertIsInstance(inner, While)

if __name__ == '__main__':
    unittest.main()