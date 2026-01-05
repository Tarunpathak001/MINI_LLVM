from src.lexer import Lexer, TokenType

def dump(tokens):
    return [(t.type, t.value) for t in tokens]

def run_test(name, code):
    print(f"\n=== {name} ===")
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    for t in tokens:
        print(t)

# -------------------------------------------------
# TEST 1: Simple assignment
# -------------------------------------------------
run_test(
    "TEST 1: Assignment",
    """
x = 10
"""
)

# Expected:
# IDENTIFIER x
# ASSIGN
# INTEGER 10
# NEWLINE
# EOF

# -------------------------------------------------
# TEST 2: Print statement
# -------------------------------------------------
run_test(
    "TEST 2: Print",
    """
print(5)
"""
)

# -------------------------------------------------
# TEST 3: If block with indentation
# -------------------------------------------------
run_test(
    "TEST 3: If with block",
    """
x = 10
if x > 5:
    print(x)
"""
)

# Expected:
# IF x > 5 :
# NEWLINE
# INDENT
# PRINT ( x )
# NEWLINE
# DEDENT
# EOF

# -------------------------------------------------
# TEST 4: If / Else block
# -------------------------------------------------
run_test(
    "TEST 4: If Else",
    """
x = 3
if x > 5:
    y = 1
else:
    y = 2
print(y)
"""
)

# -------------------------------------------------
# TEST 5: Nested if (CRITICAL)
# -------------------------------------------------
run_test(
    "TEST 5: Nested If",
    """
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
)

# -------------------------------------------------
# TEST 6: Blank lines & comments
# -------------------------------------------------
run_test(
    "TEST 6: Blank lines & comments",
    """
x = 1

# this is a comment

if x > 0:
    print(x)
"""
)

# -------------------------------------------------
# TEST 7: Strings and comparison
# -------------------------------------------------
run_test(
    "TEST 7: Strings",
    """
x = "b"
if x > "a":
    print("yes")
else:
    print("no")
"""
)

# -------------------------------------------------
# TEST 8: Unary minus (parser will handle logic)
# -------------------------------------------------
run_test(
    "TEST 8: Unary minus",
    """
x = -5
print(x)
"""
)

print("\nALL LEXER TESTS COMPLETED")