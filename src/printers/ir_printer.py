from src.ir import BinaryOp, Branch, Const, Jump, Label, Mov, Phi, Print, UnaryOp


class IRPrinter:
    """Render SSA IR with a lightweight LLVM-style syntax."""

    def format(self, program):
        return "\n".join(self.format_instruction(instr) for instr in program.instructions)

    def format_instruction(self, instr):
        if isinstance(instr, Label):
            return f"{instr.name}:"
        if isinstance(instr, Const):
            return f"  %{instr.target} = const {repr(instr.value)}"
        if isinstance(instr, Mov):
            return f"  %{instr.target} = mov %{instr.source}"
        if isinstance(instr, BinaryOp):
            return f"  %{instr.target} = {instr.op} %{instr.left}, %{instr.right}"
        if isinstance(instr, UnaryOp):
            return f"  %{instr.target} = {instr.op} %{instr.operand}"
        if isinstance(instr, Print):
            return f"  print %{instr.value}"
        if isinstance(instr, Branch):
            return f"  br %{instr.condition}, label %{instr.true_label}, label %{instr.false_label}"
        if isinstance(instr, Jump):
            return f"  jump label %{instr.target_label}"
        if isinstance(instr, Phi):
            inputs = ", ".join(
                f"[ %{value}, %{label} ]" for value, label in instr.inputs
            )
            return f"  %{instr.target} = phi {inputs}"
        return f"  ; UNKNOWN_INSTR({type(instr).__name__})"
