⚠️ Internal design notes. Not intended as user documentation.

# Mini-Python Language Specification

**Version:** 1.0  
**Status:** Phase 0 (Specification ONLY)

Mini-Python is a minimal, Python-like language designed for compiler construction. It is dynamically typed at runtime but statically checked for obvious semantic errors. It explicitly removes Python conveniences such as truthiness and boolean operators to simplify specific compilation phases.

---

## 1. Program Structure

A program is a sequence of statements executed top-to-bottom.
- **Functions:** None.
- **Loops:** None.
- **Scope:** Single global scope.
- **Blocks:** Defined by indentation (strict).

---

## 2. Statements

The language supports ONLY the following three statement types.

### 2.1. Assignment
Assigns an expression's value to a global variable. Variables are created on first assignment.

**Syntax:**
```text
identifier = expression
```

**Rules:**
- All variables are global.
- Reassignment to any type is allowed.

### 2.2. Print Statement
Outputs a value to standard output.

**Syntax:**
```text
print(expression)
```

**Rules:**
- Takes exactly ONE argument.
- No formatting or multi-argument support.

### 2.3. If / Else Statement
Conditional branching based on boolean values.

**Syntax:**
```python
if expression:
    statement
    ...
else:
    statement
    ...
```

**Rules:**
- `else` block is optional.
- The condition expression **MUST** evaluate to a `bool` type.
- **Truthiness is NOT allowed** (e.g., `if 1:` is a TypeError).
- Bodies must contain at least one statement.

---

## 3. Expressions

### 3.1. Literals
| Type | Examples | Notes |
|------|----------|-------|
| `int` | `10`, `-5` | Signed integers. |
| `string` | `"hello"`, `'abc'` | Single or double quotes. |
| `bool` | `True`, `False` | Boolean literals. |
| `NoneType` | `None` | The None singleton. |

### 3.2. Variables
- Must be defined (assigned) before reference.
- Referencing an undefined variable raises `NameError`.

### 3.3. Binary Operators

| Operator | Function | Operand Types | Result Type | Error Condition |
|:--------:|----------|---------------|:-----------:|-----------------|
| `+` | Add / Concat | `int` + `int` | `int` | `TypeError` if mixed |
| | | `string` + `string` | `string` | |
| `<` | Less Than | `int` < `int` | `bool` | `TypeError` if mixed |
| | | `string` < `string` | `bool` | |
| `>` | Greater Than | `int` > `int` | `bool` | `TypeError` if mixed |
| | | `string` > `string` | `bool` | |
| `==` | Equality | Any | `bool` | Never (false if types differ) |
| `!=` | Inequality | Any | `bool` | Never (true if types differ) |

### Chained Comparisons
Chained comparisons (e.g., `a < b < c`) are **NOT supported**. Each comparison produces a boolean value, and comparisons cannot be chained.

### 3.4. Unary Operators
- **Negation (`-`)**: 
    - Syntax: `-expression`
    - Operand must be `int`.
    - Returns `int`.

---

## 4. Scoping Rules

- **Global Scope Only**: All variables live in a single global namespace.
- **Control Flow Leaking**: Variables assigned inside `if` or `else` blocks remain visible globally after the block exits (if the block was executed).
- **Potential Errors**: It is valid to define a variable only in an `if` block, but accessing it later will cause a Runtime `NameError` if that branch wasn't taken.

**Example:**
```python
if True:
    x = 10
print(x)  # Valid, output: 10
```

### If without else

If an `if` statement has no `else` block, variables assigned inside the `if` are considered conditionally defined.

Accessing such a variable after the `if` statement is allowed by the language, but may raise a Runtime `NameError` if the condition evaluated to `False`.


---

## 5. Error Model

### 5.1. Syntax Errors (Compile-Time)
Detected during parsing.
- Invalid indentation.
- Missing colons.
- Malformed expressions or statements.

### 5.2. Static Semantic Errors (Pre-Execution Analysis)
Detected after parsing but before running.
- **NameError**: Variable used on generic path before guaranteed assignment (simplified for this specific spec as "used before assignment"). 
    - *Note: While the prompt mentions strictly determining this might be hard with dynamic control flow, the compiler should catch obvious cases or defer to runtime as specified.*
- **TypeError (Static checks where possible)**: 
    - `if` condition is not a boolean.
    - Invalid operand types for operators (e.g., `"a" - 1`).

### 5.3. Runtime Errors
- **NameError**: Reading a variable that was never assigned (e.g., defined in an unexecuted `else` block).
- **TypeError**: Operations on mismatched dynamic types (if not caught statically).

---

## 6. Formal Grammar (EBNF)

```ebnf
program         ::= { statement }

statement       ::= assignment_stmt | print_stmt | if_stmt

assignment_stmt ::= identifier "=" expression
print_stmt      ::= "print" "(" expression ")"
if_stmt         ::= "if" expression ":" block [ "else" ":" block ]

block           ::= INDENT statement { statement } DEDENT

expression      ::= relation
relation        ::= addition [ ( "<" | ">" | "==" | "!=" ) addition ]
addition        ::= term { "+" term }
term            ::= unary
unary           ::= [ "-" ] primary
primary         ::= integer | string | boolean | "None" | identifier | "(" expression ")"

boolean         ::= "True" | "False"
integer         ::= digit { digit }
identifier      ::= letter { letter | digit | "_" }
string          ::= '"' { char } '"' | "'" { char } "'"
```
*(Note check: `INDENT` and `DEDENT` are lexical tokens generated by indentation changes)*

---

## 7. Intentional Non-Features

The following are **EXPLICITLY EXCLUDED**:
- `while`, `for` loops
- functions (`def`, `return`)
- Boolean operators (`and`, `or`, `not`)
- Truthiness (implicit conversion to bool)
- `break`, `continue`
- `float`, `list`, `dict` classes

---

## 8. Examples

### Valid Program
```python
x = 10
y = 20
if x < y:
    print("x is smaller")
    res = x + y
    print(res)
else:
    print("x is not smaller")
```

### Invalid Program: Type Error
```python
x = 10
if x:  # Error: condition must be strictly bool, no truthiness
    print("error")
```

### Invalid Program: Name Error
```python
if False:
    z = 1
print(z) # Runtime Semantic Error: z is not defined
```
