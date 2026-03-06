from typing import List, Dict, Any
from src.ir import (
    IRInstr, IRProgram, Const, BinaryOp, UnaryOp, Phi,
    Label, Jump, Branch, Print, Mov
)
from src.bytecode import (
    BCInstr, Push, Load, Store, Sub,
    Add, Lt, Gt, Eq, Ne, Neg,
    Label as BCLabel, Jump as BCJump, Branch as BCBranch, Print as BCPrint
)

class SSAToBytecode:
    def convert(self, ir_prog: IRProgram) -> List[BCInstr]:
        bytecode: List[BCInstr] = []
        instructions = ir_prog.instructions
        
        # 1. Map Labels to Phis
        phis_at_label: Dict[str, List[Phi]] = {}
        
        for i, instr in enumerate(instructions):
            if isinstance(instr, Label):
                # Search ahead for Phis (guaranteed to be immediately after Label)
                current_phis = []
                j = i + 1
                while j < len(instructions) and isinstance(instructions[j], Phi):
                    current_phis.append(instructions[j])
                    j += 1
                if current_phis:
                    phis_at_label[instr.name] = current_phis

        # 2. Lowering Loop
        current_label = None
        
        for instr in instructions:
            if isinstance(instr, Label):
                current_label = instr.name
                bytecode.append(BCLabel(instr.name))
                continue
            
            if isinstance(instr, Phi):
                continue
                
            if isinstance(instr, Const):
                val_name = self._strip_ssa(instr.target)
                bytecode.append(Push(instr.value))
                bytecode.append(Store(val_name))
                
            elif isinstance(instr, Mov):
                dest = self._strip_ssa(instr.target)
                src = self._strip_ssa(instr.source)
                bytecode.append(Load(src))
                bytecode.append(Store(dest))
                
            elif isinstance(instr, BinaryOp):
                target = self._strip_ssa(instr.target)
                left = self._strip_ssa(instr.left)
                right = self._strip_ssa(instr.right)
                
                bytecode.append(Load(left))
                bytecode.append(Load(right))
                
                ops = {
                    'add': Add(), 'sub': Sub(),
                    'lt': Lt(), 'gt': Gt(), 'eq': Eq(), 'ne': Ne()
                }
                op = ops.get(instr.op)
                if not op:
                    raise ValueError(f"Unknown Op {instr.op}")
                
                bytecode.append(op)
                bytecode.append(Store(target))
                
            elif isinstance(instr, UnaryOp):
                target = self._strip_ssa(instr.target)
                operand = self._strip_ssa(instr.operand)
                
                if instr.op == 'neg':
                    bytecode.append(Load(operand))
                    bytecode.append(Neg())
                    bytecode.append(Store(target))
                else:
                    raise ValueError(f"Unknown UnaryOp {instr.op}")
                    
            elif isinstance(instr, Print):
                val = self._strip_ssa(instr.value)
                bytecode.append(Load(val))
                bytecode.append(BCPrint())
            
            elif isinstance(instr, Jump):
                target_phis = phis_at_label.get(instr.target_label, [])
                self._emit_phi_moves(bytecode, target_phis, current_label)
                bytecode.append(BCJump(instr.target_label))
                
            elif isinstance(instr, Branch):
                cond = self._strip_ssa(instr.condition)
                bytecode.append(Load(cond))
                
                if instr.true_label in phis_at_label or instr.false_label in phis_at_label:
                     raise ValueError("Critical Edge splitting required: Branch target contains Phi nodes")
                
                bytecode.append(BCBranch(instr.true_label, instr.false_label))
                
        return bytecode

    def _emit_phi_moves(self, code: List[BCInstr], phis: List[Phi], from_label: str):
        if not phis:
            return
            
        if from_label is None:
            raise ValueError("Jump encountered before any Label (broken IR?)")
            
        for phi in phis:
            src_val = None
            for ssa_val, blk_lbl in phi.inputs:
                if blk_lbl == from_label:
                    src_val = ssa_val
                    break
            
            if src_val is None:
                raise ValueError(f"Phi at {phi.inputs} missing input from {from_label}")
            
            dest = self._strip_ssa(phi.target)
            src = self._strip_ssa(src_val)
            
            code.append(Load(src))
            code.append(Store(dest))

    def _strip_ssa(self, name: str) -> str:
        # User defined variables (x_1) -> x
        # Temps (t1) -> t1
        
        last_idx = name.rfind('_')
        if last_idx != -1:
            suffix = name[last_idx+1:]
            if suffix.isdigit():
                return name[:last_idx]
        return name
