from src.ir import (
    IRProgram, Const, Mov, BinaryOp, UnaryOp, Phi,
    Branch, Jump, Label, Print
)

class SSABranchSimplify:
    def run(self, ir: IRProgram) -> IRProgram:
        const_map = {}
        new_instrs = []

        for instr in ir.instructions:

            # -------- Track Constants --------
            if isinstance(instr, Const):
                const_map[instr.target] = instr.value
                new_instrs.append(instr)

            elif isinstance(instr, Mov):
                if instr.source in const_map:
                    const_map[instr.target] = const_map[instr.source]
                new_instrs.append(instr)

            # -------- Simplify Branch --------
            elif isinstance(instr, Branch):
                cond = instr.condition

                if cond in const_map:
                    value = const_map[cond]
                    if value is True:
                        new_instrs.append(Jump(instr.true_label))
                    elif value is False:
                        new_instrs.append(Jump(instr.false_label))
                    else:
                        raise ValueError(f"Branch condition {cond} is not boolean: {value}")
                else:
                    new_instrs.append(instr)

            # -------- Pass-through --------
            else:
                new_instrs.append(instr)

        return IRProgram(new_instrs)
