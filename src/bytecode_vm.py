from typing import List, Dict, Any
from src.bytecode import (
    BCInstr, Push, Load, Store,
    Add, Lt, Gt, Eq, Ne, Neg,
    Label, Jump, Branch, Print
)

class VM:
    def __init__(self, code: List[BCInstr]):
        self.code = code
        self.stack: List[Any] = []
        self.env: Dict[str, Any] = {}
        self.ip = 0
        self.labels: Dict[str, int] = {}
        
        # Pre-scan labels
        for i, instr in enumerate(code):
            if isinstance(instr, Label):
                self.labels[instr.name] = i

    def run(self):
        while self.ip < len(self.code):
            instr = self.code[self.ip]
            self.ip += 1
            self.execute(instr)

    def execute(self, instr: BCInstr):
        if isinstance(instr, Push):
            self.stack.append(instr.value)
            
        elif isinstance(instr, Load):
            if instr.name not in self.env:
                raise NameError(f"Runtime: Variable '{instr.name}' not defined")
            self.stack.append(self.env[instr.name])
            
        elif isinstance(instr, Store):
            val = self.stack.pop()
            self.env[instr.name] = val
            
        elif isinstance(instr, Add):
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
            
        elif isinstance(instr, Lt):
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a < b)
            
        elif isinstance(instr, Gt):
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a > b)
            
        elif isinstance(instr, Eq):
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a == b)
            
        elif isinstance(instr, Ne):
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a != b)
            
        elif isinstance(instr, Neg):
            a = self.stack.pop()
            self.stack.append(-a)
            
        elif isinstance(instr, Label):
            pass 
            
        elif isinstance(instr, Jump):
            self.ip = self.labels[instr.target]
            
        elif isinstance(instr, Branch):
            cond = self.stack.pop()
            if cond:
                self.ip = self.labels[instr.true_label]
            else:
                self.ip = self.labels[instr.false_label]
                
        elif isinstance(instr, Print):
            val = self.stack.pop()
            print(val)
            
        else:
            raise ValueError(f"Unknown instruction {instr}")
