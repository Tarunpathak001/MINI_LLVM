from dataclasses import dataclass
from typing import List, Tuple, Union

class IRInstr:
    pass



@dataclass
class Const(IRInstr):
    target: str
    value: object  

@dataclass
class BinaryOp(IRInstr):
    op: str  
    target: str
    left: str
    right: str

@dataclass
class UnaryOp(IRInstr):
    op: str
    target: str
    operand: str

@dataclass
class Mov(IRInstr):
    target: str
    source: str

@dataclass
class Phi(IRInstr):
    target: str
    inputs: List[Tuple[str, str]]


@dataclass
class Label(IRInstr):
    name: str

@dataclass
class Jump(IRInstr):
    target_label: str

@dataclass
class Branch(IRInstr):
    condition: str
    true_label: str
    false_label: str


@dataclass
class Print(IRInstr):
    value: str


@dataclass
class IRProgram:
    instructions: List[IRInstr]
