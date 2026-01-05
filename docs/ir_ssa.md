⚠️ Internal design notes. Not intended as user documentation.

# Mini-Python SSA IR (Phase 6.3)

Top-level documentation for the Intermediate Representation.

## IR Structure
- **Global Function**: `main` contains the instruction list.
- **SSA Form**: Every variable assignment creates a new version (`x_1`, `x_2`).
- **Explicit Control Flow**: Uses `Label`, `Jump`, `Branch`.

## Instructions
- `Const(target, val)`
- `BinaryOp(op, target, left, right)`
- `UnaryOp(op, target, operand)`
- `Mov(target, source)`
- `Phi(target, [(val1, label1), (val2, label2)])`
- `Label(name)`
- `Jump(target_label)`
- `Branch(cond, true_label, false_label)`
- `Print(val)`

## Control Flow construction

### If/Else
- Merges control flow with `Phi` nodes.
- Only variables modified in branches get Phi nodes.

### While Loops (Phase 6.3)
- **Header**: Contains `Phi` nodes for **all** loop-carried variables.
- **Body**: Executes if condition is true. Ends with `Jump` to Header.
- **Exit**: Target when condition is false.
- **Backedge**: The connection from Body end to Header.

## Example (While Loop)
```python
x = 0
while x < 5:
    x = x + 1
```

**SSA IR:**
```
L_while_header_1:
    x_2 = phi [(x_1, L_pre), (x_3, L_while_body_1)]
    t1 = lt x_2 5
    branch t1 L_while_body_1 L_while_exit_1
L_while_body_1:
    t2 = add x_2 1
    x_3 = mov t2
    jump L_while_header_1
L_while_exit_1:
```
