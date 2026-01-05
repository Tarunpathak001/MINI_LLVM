from dataclasses import dataclass
from typing import List, Optional

class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]



@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode

@dataclass
class Print(ASTNode):
    value: ASTNode

@dataclass
class While(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class If(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]]


@dataclass
class BinaryOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Literal(ASTNode):
    value: object 

@dataclass
class Variable(ASTNode):
    name: str
