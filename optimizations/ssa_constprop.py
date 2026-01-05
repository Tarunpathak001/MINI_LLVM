from src.ir import (
    IRProgram, Const, BinaryOp, UnaryOp, Mov, Phi
)

class SSAConstProp:
    def run(self, ir: IRProgram) -> IRProgram:
        """
        Returns a NEW IRProgram with constants propagated.
        Does NOT mutate the original.
        """
        const_map = {}   # ssa_name -> constant value
        new_instrs = []

        instr_list = ir.instructions
        
        for instr in instr_list:
            # --- Const ---
            if isinstance(instr, Const):
                const_map[instr.target] = instr.value
                new_instrs.append(instr)

            # --- Mov ---
            elif isinstance(instr, Mov):
                src = instr.source
                if src in const_map:
                    const_map[instr.target] = const_map[src]
                new_instrs.append(instr)

            # --- BinaryOp ---
            elif isinstance(instr, BinaryOp):
                # Analysis only: we can lookup operands in const_map
                # but we DO NOT inject values into the IR instructions.
                # Operands must remain SSA variable names (strings).
                new_instrs.append(instr)

            # --- UnaryOp ---
            elif isinstance(instr, UnaryOp):
                new_instrs.append(instr)

            # --- Phi ---
            elif isinstance(instr, Phi):
                # Propagate only if ALL inputs are known constants AND equal
                values = set()
                possible = True
                
                for val, _ in instr.inputs:
                    if val in const_map:
                        values.add(const_map[val])
                    else:
                        possible = False
                        break
                
                if possible and len(values) == 1:
                    # All inputs are the same constant
                    const_map[instr.target] = values.pop()
                    # We still emit the Phi because this phase just analyzes.
                    # Dead code elimination will remove it later.
                    
                new_instrs.append(instr)

            else:
                new_instrs.append(instr)

        return IRProgram(new_instrs)
