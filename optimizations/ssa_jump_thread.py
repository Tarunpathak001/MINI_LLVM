from src.ir import IRProgram, Jump, Label

class SSAJumpThread:
    def run(self, ir: IRProgram) -> IRProgram:
        # Map label -> jump target (if trivial)
        # Trivial block: specific pattern "Label A; Jump B"
        # We need to scan the linear instruction list to find this pattern.
        jump_map = {}

        instrs = ir.instructions
        
        # Pass 1: Identify trivial blocks (Label -> Jump pattern)
        for i in range(len(instrs) - 1):
            curr = instrs[i]
            next_instr = instrs[i+1]
            
            if isinstance(curr, Label) and isinstance(next_instr, Jump):
                # Guard against self-loop A -> A
                if curr.name != next_instr.target_label:
                    jump_map[curr.name] = next_instr.target_label
        
        # Pass 2: Rewrite Jumps
        new_instrs = []
        for instr in instrs:
            if isinstance(instr, Jump) and instr.target_label in jump_map:
                new_target = jump_map[instr.target_label]
                if new_target != instr.target_label:
                    new_instrs.append(Jump(new_target))
                else:
                    new_instrs.append(instr)
            else:
                new_instrs.append(instr)

        return IRProgram(new_instrs)
