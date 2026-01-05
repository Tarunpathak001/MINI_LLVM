from src.lexer import TokenType
from src.ast_nodes import (
    Program, Assignment, Print, If, While,
    BinaryOp, UnaryOp, Literal, Variable
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        tok = self.current()
        if tok.type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {tok.type} at line {tok.line}"
            )
        self.advance()
        return tok

    def skip_newlines(self):
        while self.current().type == TokenType.NEWLINE:
            self.advance()


    def parse(self):
        statements = []
        self.skip_newlines()

        while self.current().type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()

        return Program(statements)


    def parse_statement(self):
        tok = self.current()

        if tok.type == TokenType.IDENTIFIER:
            return self.parse_assignment()
        elif tok.type == TokenType.PRINT:
            return self.parse_print()
        elif tok.type == TokenType.IF:
            return self.parse_if()
        elif tok.type == TokenType.WHILE:
            return self.parse_while()
        else:
            raise SyntaxError(f"Unexpected token {tok.type} at line {tok.line}")

    def parse_assignment(self):
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        expr = self.parse_expression()
        self.expect(TokenType.NEWLINE)
        return Assignment(name, expr)

    def parse_print(self):
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        expr = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.NEWLINE)
        return Print(expr)

    def parse_if(self):
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        then_body = self.parse_block()

        else_body = None
        if self.current().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.COLON)
            self.expect(TokenType.NEWLINE)
            else_body = self.parse_block()

        return If(condition, then_body, else_body)

    def parse_while(self):
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.expect(TokenType.NEWLINE)
        body = self.parse_block()
        return While(condition, body)

    def parse_block(self):
        self.expect(TokenType.INDENT)
        statements = []

        while self.current().type != TokenType.DEDENT:
            if self.current().type == TokenType.NEWLINE:
                self.advance()
                continue
            statements.append(self.parse_statement())

        self.expect(TokenType.DEDENT)
        return statements


    def parse_expression(self):
        return self.parse_relation()

    def parse_relation(self):
        left = self.parse_addition()
        tok = self.current()

        if tok.type in (TokenType.LT, TokenType.GT, TokenType.EQ, TokenType.NE):
            op = tok.value
            self.advance()
            right = self.parse_addition()
            return BinaryOp(op, left, right)

        return left

    def parse_addition(self):
        node = self.parse_unary()

        while self.current().type == TokenType.PLUS:
            op = self.current().value
            self.advance()
            right = self.parse_unary()
            node = BinaryOp(op, node, right)

        return node

    def parse_unary(self):
        if self.current().type == TokenType.MINUS:
            self.advance()
            operand = self.parse_unary()
            return UnaryOp('-', operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()

        if tok.type == TokenType.INTEGER:
            self.advance()
            return Literal(tok.value)
        if tok.type == TokenType.STRING:
            self.advance()
            return Literal(tok.value)
        if tok.type == TokenType.TRUE:
            self.advance()
            return Literal(True)
        if tok.type == TokenType.FALSE:
            self.advance()
            return Literal(False)
        if tok.type == TokenType.NONE:
            self.advance()
            return Literal(None)
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return Variable(tok.value)
        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Unexpected token {tok.type} at line {tok.line}")
