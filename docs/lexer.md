⚠️ Internal design notes. Not intended as user documentation.

# Mini-Python Lexer (Phase 1)

**Status:** Completed & Audited  
**Source File:** `lexer.py`

This lexer provides a deterministic stream of tokens for the Mini-Python language. It strictly separates indentation logic from content tokenization and ensures a 1-to-1 mapping of physical lines to `NEWLINE` tokens.

---

## 1. Token Definitions

| Token Type | Pattern / Example | Notes |
|------------|-------------------|-------|
| `IDENTIFIER` | `[a-zA-Z_][a-zA-Z0-9_]*` | |
| `INTEGER` | `\d+` | Unsigned. Negative handled by parser. |
| `STRING` | `"..."` or `'...'` | Quotes are stripped in the token value. |
| **Keywords** | | |
| `IF`, `ELSE` | `if`, `else` | |
| `PRINT` | `print` | |
| `TRUE`, `FALSE` | `True`, `False` | |
| `NONE` | `None` | |
| **Operators** | | |
| `PLUS`, `MINUS` | `+`, `-` | |
| `LT`, `GT` | `<`, `>` | Strictly less/greater than. |
| `EQ`, `NE` | `==`, `!=` | Equality checks. |
| `ASSIGN` | `=` | Assignment. |
| **Delimiters** | | |
| `LPAREN`, `RPAREN` | `(`, `)` | |
| `COLON` | `:` | |
| **Structure** | | |
| `NEWLINE` | `\n` | Emitted for **every** physical line. |
| `INDENT` | | Emitted when indentation increases. |
| `DEDENT` | | Emitted when indentation decreases to match stack. |
| `EOF` | | End of Token stream. |

---

## 2. Indentation & Line Processing Rules

The lexer processes source code line-by-line.

1. **Blank/Comment Lines**:
   - Lines containing only whitespace or starting with `#` are treated as "blank".
   - **Action**: Emit `NEWLINE`. 
   - **Indentation**: Ignored. Stack is **not** touched.

2. **Content Lines**:
   - **Indentation**:
     - Leading spaces are counted.
     - Compared against the indentation stack.
     - `INDENT` or `DEDENT` tokens are emitted to reconcile the level.
   - **Content**:
     - Remaining characters are tokenized.
   - **Termination**:
     - `NEWLINE` is emitted at the end of the line.

3. **End of File**:
   - Remaining deduction levels on the stack are popped with `DEDENT` tokens.
   - `EOF` is emitted.

---

## 3. Usage

```python
from lexer import Lexer, TokenType

source = """
x = 1
if x:
    print(x)
"""

lexer = Lexer(source)
tokens = lexer.tokenize()
```

## 4. Error Handling

- **`SyntaxError`**: Unknown characters or malformed strings.
- **`IndentationError`**: Tabs, or dedenting to a level not present on the stack.
