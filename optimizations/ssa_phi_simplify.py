from src.ir import IRProgram, Phi, Mov

class SSAPhiSimplify:
    def run(self, ir: IRProgram) -> IRProgram:
        new_instrs = []

        for instr in ir.instructions:
            if isinstance(instr, Phi):
                # Rule: A Phi with exactly one input is just a Move.
                # Phi(x_2, [(x_1, L1)]) -> Mov(x_2, x_1)
                # This often happens after Unreachable Block Elimination removes other inputs.
                if len(instr.inputs) == 1:
                    val, _ = instr.inputs[0]
                    # We preserve the target name (x_2) and source value (x_1).
                    # This Mov will likely be cleaned up by Register Allocation or Copy Propagation later,
                    # but for now it simplifies the CFG logic.
                    new_instrs.append(Mov(instr.target, val))
                else:
                    new_instrs.append(instr)
            else:
                new_instrs.append(instr)

        return IRProgram(new_instrs)
