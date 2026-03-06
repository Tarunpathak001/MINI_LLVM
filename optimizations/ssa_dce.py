from src.ir import (
    IRProgram,
    Const, Mov, BinaryOp, UnaryOp, Phi,
    Print, Branch, Jump, Label
)

class SSADCE:
    def run(self, ir: IRProgram) -> IRProgram:
        instructions = ir.instructions

        # Phase 1: Build def map (target -> instruction index)
        def_map = {}  # ssa_name -> index of instruction that defines it
        for idx, instr in enumerate(instructions):
            target = getattr(instr, 'target', None)
            if target is not None:
                def_map[target] = idx

        # Phase 2: Seed worklist from side-effect instructions (roots)
        live = set()      # set of instruction indices that are live
        worklist = []     # indices to process

        for idx, instr in enumerate(instructions):
            if isinstance(instr, (Print, Branch, Jump, Label)):
                if idx not in live:
                    live.add(idx)
                    worklist.append(idx)

        # Phase 3: Transitively mark dependencies as live
        while worklist:
            idx = worklist.pop()
            instr = instructions[idx]

            # Get all SSA names used by this instruction
            used_names = self._get_used(instr)

            for name in used_names:
                if name in def_map:
                    def_idx = def_map[name]
                    if def_idx not in live:
                        live.add(def_idx)
                        worklist.append(def_idx)

        # Phase 4: Filter to live instructions only (preserve order)
        new_instrs = [instr for idx, instr in enumerate(instructions) if idx in live]
        return IRProgram(new_instrs)

    def _get_used(self, instr):
        """Return set of SSA names used (read) by an instruction."""
        names = set()

        if isinstance(instr, BinaryOp):
            if isinstance(instr.left, str):
                names.add(instr.left)
            if isinstance(instr.right, str):
                names.add(instr.right)

        elif isinstance(instr, UnaryOp):
            if isinstance(instr.operand, str):
                names.add(instr.operand)

        elif isinstance(instr, Mov):
            if isinstance(instr.source, str):
                names.add(instr.source)

        elif isinstance(instr, Phi):
            for val, _ in instr.inputs:
                if isinstance(val, str):
                    names.add(val)

        elif isinstance(instr, Print):
            if isinstance(instr.value, str):
                names.add(instr.value)

        elif isinstance(instr, Branch):
            if isinstance(instr.condition, str):
                names.add(instr.condition)

        return names

