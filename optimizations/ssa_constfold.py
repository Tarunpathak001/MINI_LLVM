from src.ir import (
    IRProgram, Const, BinaryOp, UnaryOp, Mov, Phi
)

class SSAConstFold:
    def run(self, ir: IRProgram) -> IRProgram:
        const_map = {}   # ssa_name -> constant value
        new_instrs = []

        instr_list = ir.instructions

        for instr in instr_list:

            # ---------- Const ----------
            if isinstance(instr, Const):
                const_map[instr.target] = instr.value
                new_instrs.append(instr)

            # ---------- Mov ----------
            elif isinstance(instr, Mov):
                if instr.source in const_map:
                    const_map[instr.target] = const_map[instr.source]
                new_instrs.append(instr)

            # ---------- BinaryOp ----------
            elif isinstance(instr, BinaryOp):
                l = instr.left
                r = instr.right

                # We can check const_map because we are folding results,
                # NOT rewriting operands (which must remain names if emitted as BinOp).
                # But if we Fold, we replace the BinOp with a Const!
                
                if l in const_map and r in const_map:
                    a = const_map[l]
                    b = const_map[r]

                    if instr.op == 'add':
                        val = a + b
                    elif instr.op == 'lt':
                        val = a < b
                    elif instr.op == 'gt':
                        val = a > b
                    elif instr.op == 'eq':
                        val = a == b
                    elif instr.op == 'ne':
                        val = a != b
                    else:
                        raise ValueError(f"Unknown op {instr.op}")

                    const_map[instr.target] = val
                    # REPLACEMENT: Emit Const instead of BinaryOp
                    new_instrs.append(Const(instr.target, val))
                else:
                    new_instrs.append(instr)

            # ---------- UnaryOp ----------
            elif isinstance(instr, UnaryOp):
                if instr.operand in const_map:
                    val = const_map[instr.operand]

                    if instr.op == 'neg':
                        val = -val
                    else:
                        raise ValueError(f"Unknown unary op {instr.op}")

                    const_map[instr.target] = val
                    new_instrs.append(Const(instr.target, val))
                else:
                    new_instrs.append(instr)

            # ---------- Phi ----------
            elif isinstance(instr, Phi):
                # Phi folding already decided in Phase 7.1
                # Just pass through. If 7.1 didn't fold/propagate it to a Const, we can't do it here easily.
                # Actually 7.1 didn't *rewrite* instructions either.
                # So if 7.1 found a constant Phi, it put it in const_map but emitted Phi.
                # HERE: If we knew Phis were constant, we could emit Const?
                # But instruction says: "Never fold Phi unless Phase 7.1 already proved it constant".
                # And provided code says: "new_instrs.append(instr)".
                # So we stick to minimal changes.
                new_instrs.append(instr)

            # ---------- Other ----------
            else:
                new_instrs.append(instr)

        return IRProgram(new_instrs)
