from src.ast_nodes import (
    Program, Assignment, Print, If, While,
    BinaryOp, UnaryOp, Literal, Variable
)

class SemanticAnalyzer:
    def __init__(self):
        # Set of variable names guaranteed to be defined at current point
        self.defined_vars = set()
        # Map of variable names to their static type (int, str, bool, type(None))
        self.var_types = {}

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{type(node).__name__} method")

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Assignment(self, node: Assignment):
        # 1. Analyze value expression first
        val_type = self.visit(node.value)
        
        # 2. Update state
        # Mini-Python allows reassignment to any type.
        self.var_types[node.name] = val_type
        self.defined_vars.add(node.name)

    def visit_Print(self, node: Print):
        self.visit(node.value)
        # print takes any type

    def visit_If(self, node: If):
        # 1. Analyze condition
        cond_type = self.visit(node.condition)
        if cond_type is not bool:
            raise TypeError("if condition must be boolean")

        # 2. Snapshot state before branches
        initial_defined = self.defined_vars.copy()
        initial_types = self.var_types.copy()

        # 3. Visit Then Branch
        for stmt in node.then_body:
            self.visit(stmt)
        
        then_defined = self.defined_vars.copy()
        then_types = self.var_types.copy()

        # 4. Visit Else Branch (if exists)
        if node.else_body:
            self.defined_vars = initial_defined.copy()
            self.var_types = initial_types.copy()
            
            for stmt in node.else_body:
                self.visit(stmt)
            
            else_defined = self.defined_vars.copy()
            else_types = self.var_types.copy()
        else:
            else_defined = initial_defined.copy()
            else_types = initial_types.copy()

        # 5. Merge State
        # Variable defined after if ONLY IF defined in BOTH branches.
        newly_defined_in_both = then_defined.intersection(else_defined)
        self.defined_vars = initial_defined.union(newly_defined_in_both)
        
        # Merge types
        merged_types = {}

        # Preserve initial vars
        for var in initial_defined:
            merged_types[var] = initial_types[var]

        # Add safely merged vars (defined in both branches with matching types)
        for var in newly_defined_in_both:
            t1 = then_types.get(var)
            t2 = else_types.get(var)
            
            if t1 == t2:
                merged_types[var] = t1
            else:
                # Type conflict -> Remove from valid definitions
                if var in self.defined_vars:
                    self.defined_vars.remove(var)
        
        self.var_types = merged_types

    def visit_While(self, node: While):
        cond_type = self.visit(node.condition)
        if cond_type is not bool:
            raise TypeError("while condition must be boolean")
            
        # Snapshot state before loop
        before_vars = self.defined_vars.copy()
        before_types = self.var_types.copy()
        
        # Visit body
        for stmt in node.body:
            self.visit(stmt)
            
        # Restore defined_vars (Strict Rule: No new variables survive loop scope)
        self.defined_vars = before_vars
        
        # Check for type conflicts on pre-existing variables
        for var, initial_type in before_types.items():
            if var in self.var_types:
                new_type = self.var_types[var]
                if new_type != initial_type:
                    if var in self.defined_vars:
                        self.defined_vars.remove(var)
        
        # Restore var_types consistent with defined_vars
        final_types = before_types.copy()
        vars_to_remove = [v for v in final_types if v not in self.defined_vars]
        for v in vars_to_remove:
            del final_types[v]
            
        self.var_types = final_types


    def visit_BinaryOp(self, node: BinaryOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.op

        # 1. Arithmetic (+): int+int or str+str
        if op == '+':
            if left_type is int and right_type is int:
                return int
            if left_type is str and right_type is str:
                return str
            raise TypeError(f"cannot apply '+' to {left_type.__name__} and {right_type.__name__}")

        # 2. Arithmetic (-): int-int only
        if op == '-':
            if left_type is int and right_type is int:
                return int
            raise TypeError(f"cannot apply '-' to {left_type.__name__} and {right_type.__name__}")

        # 3. Comparison (<, >): int vs int, str vs str
        if op in ('<', '>'):
            if left_type is int and right_type is int:
                return bool
            if left_type is str and right_type is str:
                return bool
            raise TypeError(f"cannot apply '{op}' to {left_type.__name__} and {right_type.__name__}")

        # 3. Equality (==, !=): Any types allowed
        if op in ('==', '!='):
            return bool

        raise TypeError(f"Unknown operator {op}")

    def visit_UnaryOp(self, node: UnaryOp):
        operand_type = self.visit(node.operand)
        op = node.op

        if op == '-':
            if operand_type is int:
                return int
            raise TypeError(f"cannot apply '-' to {operand_type.__name__}")
        
        raise TypeError(f"Unknown unary operator {op}")

    def visit_Literal(self, node: Literal):
        if node.value is None:
            return type(None)
        return type(node.value)

    def visit_Variable(self, node: Variable):
        if node.name not in self.defined_vars:
            raise NameError(f"variable '{node.name}' may be used before assignment")
        return self.var_types[node.name]
