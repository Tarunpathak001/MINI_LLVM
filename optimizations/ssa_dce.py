from src.ir import (
    IRProgram,
    Const, Mov, BinaryOp, UnaryOp, Phi,
    Print, Branch, Jump, Label
)

class SSADCE:
    def run(self, ir: IRProgram) -> IRProgram:
        used = set()
        new_instrs = []

        # Traverse backwards
        for instr in reversed(ir.instructions):

            # ---------- Side-effect instructions (ALWAYS keep) ----------
            if isinstance(instr, (Print, Branch, Jump, Label)):
                self._mark_used(instr, used)
                new_instrs.append(instr)
                continue

            # ---------- Instructions with a target ----------
            target = getattr(instr, 'target', None)

            if target is not None:
                if target in used:
                    # Instruction is live
                    self._mark_used(instr, used)
                    new_instrs.append(instr)
                else:
                    # DEAD → skip
                    continue
            else:
                # Defensive fallback (should not happen if all instrs covered)
                self._mark_used(instr, used)
                new_instrs.append(instr)

        new_instrs.reverse()
        return IRProgram(new_instrs)

    def _mark_used(self, instr, used):
        """
        Add all SSA operands used by instr into `used`
        """
        if isinstance(instr, BinaryOp):
            if isinstance(instr.left, str):
                used.add(instr.left)
            if isinstance(instr.right, str):
                used.add(instr.right)

        elif isinstance(instr, UnaryOp):
            if isinstance(instr.operand, str):
                used.add(instr.operand)

        elif isinstance(instr, Mov):
            if isinstance(instr.source, str):
                used.add(instr.source)

        elif isinstance(instr, Phi):
            for val, _ in instr.inputs:
                if isinstance(val, str):
                    used.add(val)

        elif isinstance(instr, Print):
            if isinstance(instr.value, str):
                used.add(instr.value)

        elif isinstance(instr, Branch):
            if isinstance(instr.condition, str):
                used.add(instr.condition)
