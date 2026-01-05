import re
import sys

class TokenType:

    IDENTIFIER = 'IDENTIFIER'
    IF    = 'IF'
    ELSE  = 'ELSE'
    PRINT = 'PRINT'
    TRUE  = 'TRUE'
    FALSE = 'FALSE'
    NONE  = 'NONE'
    WHILE = 'WHILE'
    INTEGER = 'INTEGER'
    STRING  = 'STRING'
    PLUS   = 'PLUS'     # +
    MINUS  = 'MINUS'    # -
    LT     = 'LT'       # <
    GT     = 'GT'       # >
    EQ     = 'EQ'       # ==
    NE     = 'NE'       # !=
    ASSIGN = 'ASSIGN'   # =
    LPAREN = 'LPAREN'   # (
    RPAREN = 'RPAREN'   # )
    COLON  = 'COLON'    # :
    NEWLINE = 'NEWLINE'
    INDENT  = 'INDENT'
    DEDENT  = 'DEDENT'
    EOF     = 'EOF'
class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line:{self.line}, Col:{self.column})"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.line_num = 1
        self.indent_stack = [0] 

        self.KEYWORDS = {
            'if':    TokenType.IF,
            'else':  TokenType.ELSE,
            'print': TokenType.PRINT,
            'True':  TokenType.TRUE,
            'False': TokenType.FALSE,
            'None':  TokenType.NONE,
            'while': TokenType.WHILE,
        }

    def tokenize(self):
        self.tokens = []
        self.line_num = 1
        self.indent_stack = [0]
        
        lines = self.source.split('\n')
        lines = self.source.split('\n')

        for line in lines:
            self._process_line(line)
            self.line_num += 1
        
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line_num, 0))
        
        self.tokens.append(Token(TokenType.EOF, None, self.line_num, 0))
        
        return self.tokens

    def _process_line(self, line):
        stripped = line.strip()
        is_blank_or_comment = (len(stripped) == 0) or (stripped.startswith('#'))
        
        if is_blank_or_comment:
            self.tokens.append(Token(TokenType.NEWLINE, None, self.line_num, 0))
            return

        indent_len = 0
        for char in line:
            if char == ' ':
                indent_len += 1
            elif char == '\t':
                raise IndentationError(f"Tabs are illegal at Line {self.line_num}")
            else:
                break
        current_indent = self.indent_stack[-1]
        
        if indent_len > current_indent:
            self.indent_stack.append(indent_len)
            self.tokens.append(Token(TokenType.INDENT, None, self.line_num, 1))
        elif indent_len < current_indent:
            while indent_len < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, None, self.line_num, 1))
            if indent_len != self.indent_stack[-1]:
                raise IndentationError(f"Unindent does not match any outer indentation level at Line {self.line_num}")
        self._tokenize_content(line, start_col=indent_len)
        self.tokens.append(Token(TokenType.NEWLINE, None, self.line_num, 0))

    def _tokenize_content(self, line, start_col):
        pos = start_col
        length = len(line)
        
        while pos < length:
            char = line[pos]
            if char == ' ':
                pos += 1
                continue
            if char == '#':
                break
            
            current_text = line[pos:]
            
            if char in ('"', "'"):
                match = re.match(r'^("[^"]*"|\'[^\']*\')', current_text)
                if match:
                    val_with_quotes = match.group(0)
                    val_content = val_with_quotes[1:-1]
                    self.tokens.append(Token(TokenType.STRING, val_content, self.line_num, pos + 1))
                    pos += len(val_with_quotes)
                    continue
                else:
                     raise SyntaxError(f"Unterminated string literal at Line {self.line_num}")
            if current_text.startswith('=='):
                self.tokens.append(Token(TokenType.EQ, '==', self.line_num, pos + 1))
                pos += 2
                continue
            if current_text.startswith('!='):
                self.tokens.append(Token(TokenType.NE, '!=', self.line_num, pos + 1))
                pos += 2
                continue
            if char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', self.line_num, pos + 1))
                pos += 1; continue
            if char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', self.line_num, pos + 1))
                pos += 1; continue
            if char == '<':
                self.tokens.append(Token(TokenType.LT, '<', self.line_num, pos + 1))
                pos += 1; continue
            if char == '>':
                self.tokens.append(Token(TokenType.GT, '>', self.line_num, pos + 1))
                pos += 1; continue
            if char == '=':
                self.tokens.append(Token(TokenType.ASSIGN, '=', self.line_num, pos + 1))
                pos += 1; continue
            if char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line_num, pos + 1))
                pos += 1; continue
            if char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line_num, pos + 1))
                pos += 1; continue
            if char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.line_num, pos + 1))
                pos += 1; continue
    
            if char.isalpha() or char == '_':
                match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)', current_text)
                word = match.group(0)
                
                if word in self.KEYWORDS:
                    tk_type = self.KEYWORDS[word]
                    self.tokens.append(Token(tk_type, word, self.line_num, pos + 1))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, word, self.line_num, pos + 1))
                
                pos += len(word)
                continue
                
            if char.isdigit():
                match = re.match(r'^(\d+)', current_text)
                digits = match.group(0)
                self.tokens.append(Token(TokenType.INTEGER, int(digits), self.line_num, pos + 1))
                pos += len(digits)
                continue

            raise SyntaxError(f"Invalid character '{char}' at Line {self.line_num}, Col {pos + 1}")

if __name__ == '__main__':
    source = """
x = 10
if x > 5:
    print("Test")

# Comment line
    print(x)
"""
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        for t in tokens:
            print(t)
    except Exception as e:
        print(f"Error: {e}")
