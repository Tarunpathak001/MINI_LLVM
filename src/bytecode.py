from dataclasses import dataclass
from typing import Any

class BCInstr:
    pass


@dataclass
class Push(BCInstr):
    value: Any      

@dataclass
class Load(BCInstr):
    name: str        

@dataclass
class Store(BCInstr):
    name: str


class Add(BCInstr): pass
class Lt(BCInstr): pass
class Gt(BCInstr): pass
class Eq(BCInstr): pass
class Ne(BCInstr): pass
class Neg(BCInstr): pass

@dataclass
class Label(BCInstr):
    name: str

@dataclass
class Jump(BCInstr):
    target: str

@dataclass
class Branch(BCInstr):
    true_label: str
    false_label: str

class Print(BCInstr): pass
