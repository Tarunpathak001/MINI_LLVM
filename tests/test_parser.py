import unittest
import sys
import os

# Add parent directory to path to import modules

from src.lexer import Lexer
from src.parser import Parser
from src.ast_nodes import (
    Program, Assignment, Print, If,
    BinaryOp, UnaryOp, Literal, Variable
)

class TestParser(unittest.TestCase):
    def parse_source(self, source):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()

    def test_assignment(self):
        """Test simple assignment: x = 10"""
        source = "x = 10"
        ast = self.parse_source(source)
        
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.name, "x")
        self.assertIsInstance(stmt.value, Literal)
        self.assertEqual(stmt.value.value, 10)

    def test_print(self):
        """Test print statement: print(x)"""
        source = "print(x)"
        ast = self.parse_source(source)
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, Print)
        self.assertIsInstance(stmt.value, Variable)
        self.assertEqual(stmt.value.name, "x")

    def test_if_else(self):
        """Test if-else structure"""
        source = """
x = 10
if x > 5:
    y = 1
else:
    y = 2
print(y)
"""
        ast = self.parse_source(source)
        
        # Structure: Assign, If, Print
        self.assertEqual(len(ast.statements), 3)
        self.assertIsInstance(ast.statements[0], Assignment)
        self.assertIsInstance(ast.statements[1], If)
        self.assertIsInstance(ast.statements[2], Print)
        
        if_stmt = ast.statements[1]
        # Condition: x > 5
        self.assertIsInstance(if_stmt.condition, BinaryOp)
        self.assertEqual(if_stmt.condition.op, '>')
        
        # Then body: y = 1
        self.assertEqual(len(if_stmt.then_body), 1)
        self.assertIsInstance(if_stmt.then_body[0], Assignment)
        self.assertEqual(if_stmt.then_body[0].value.value, 1)
        
        # Else body: y = 2
        self.assertIsNotNone(if_stmt.else_body)
        self.assertEqual(len(if_stmt.else_body), 1)
        self.assertEqual(if_stmt.else_body[0].value.value, 2)

    def test_nested_if(self):
        """Test strict nested if structure"""
        source = """
if x > 5:
    if x > 8:
        y = 1
    else:
        y = 2
else:
    y = 3
"""
        ast = self.parse_source(source)
        
        self.assertEqual(len(ast.statements), 1)
        outer_if = ast.statements[0]
        self.assertIsInstance(outer_if, If)
        
        # Check nested if in then_body
        nested_if = outer_if.then_body[0]
        self.assertIsInstance(nested_if, If)
        self.assertEqual(nested_if.condition.right.value, 8)
        
        # Check nested else
        self.assertIsNotNone(nested_if.else_body)
        self.assertEqual(nested_if.else_body[0].value.value, 2)
        
        # Check outer else
        self.assertIsNotNone(outer_if.else_body)
        self.assertEqual(outer_if.else_body[0].value.value, 3)

    def test_unary_and_expression(self):
        """Test x = -5; print(x + 3)"""
        source = """
x = -5
print(x + 3)
"""
        ast = self.parse_source(source)
        
        # Assignment: x = -5
        assign = ast.statements[0]
        self.assertIsInstance(assign.value, UnaryOp)
        self.assertEqual(assign.value.op, '-')
        self.assertEqual(assign.value.operand.value, 5)
        
        # Print: x + 3
        prt = ast.statements[1]
        self.assertIsInstance(prt.value, BinaryOp)
        self.assertEqual(prt.value.op, '+')
        self.assertIsInstance(prt.value.left, Variable)
        self.assertIsInstance(prt.value.right, Literal)

if __name__ == '__main__':
    unittest.main()