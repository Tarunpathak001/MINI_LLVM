
from typing import Dict, List, Set, Any
from src.ast_nodes import (
    Program, Assignment, Print, If, While,
    BinaryOp as ASTBinaryOp, UnaryOp as ASTUnaryOp, Literal, Variable
)
from src.ir import (
    IRInstr, IRProgram, Const, BinaryOp, UnaryOp, Phi,
    Label, Jump, Branch, Print as IRPrint, Mov
)

class IRBuilder:
    def __init__(self):
        self.instructions: List[IRInstr] = []
        self.current_defs: Dict[str, str] = {}
        self.var_versions: Dict[str, int] = {}
        
        self.counter_labels = 0
        self.counter_temp = 0

        self.current_label = None

    
    def new_var(self, name: str) -> str:
        """Create a new SSA version for a user variable using per-variable counters."""
        self.var_versions[name] = self.var_versions.get(name, 0) + 1
        ssa_name = f"{name}_{self.var_versions[name]}"
        self.current_defs[name] = ssa_name
        return ssa_name

    def new_temp(self) -> str:
        """Create a new temporary SSA variable (intermediate result)."""
        self.counter_temp += 1
        return f"t{self.counter_temp}"

    def new_label(self, suffix: str) -> str:
        """Create a unique label."""
        self.counter_labels += 1
        return f"L_{suffix}_{self.counter_labels}"

    def get_current_def(self, name: str) -> str:
        """Get the current SSA name for a variable."""
        # For runtime error testing (bypassing semantic checks), we allow undefined vars.
        # In strict compilation, Phase 3 catches this.
        # Here we return the raw name, which lowers to 'Load name', causing VM Runtime Error.
        if name not in self.current_defs:
            return name
        return self.current_defs[name]
    
    def set_current_def(self, name: str, ssa_name: str):
        """Set the current SSA name for a variable."""
        self.current_defs[name] = ssa_name
        
    def emit(self, instr: IRInstr):
        """Emit an IR instruction."""
        self.instructions.append(instr)

    def emit_label(self, label: str):
        """Emit a label instruction and update the current_label."""
        self.emit(Label(label))
        self.current_label = label


    def visit(self, node: Any) -> str:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No IR visit method for {type(node).__name__}")


    def generate(self, node: Program) -> IRProgram:
        self.emit_label("entry")
        
        for stmt in node.statements:
            self.visit(stmt)
        return IRProgram(self.instructions)


    def visit_Assignment(self, node: Assignment):
        val_name = self.visit(node.value)
        lhs_ssa = self.new_var(node.name)
        self.instructions.append(Mov(lhs_ssa, val_name))
        return lhs_ssa

    def visit_Print(self, node: Print):
        val = self.visit(node.value)
        self.instructions.append(IRPrint(val))

    def collect_assigned_vars(self, node_list: List[Any]) -> Set[str]:
        """Helper to find all variables assigned in a list of statements."""
        assigned = set()
        
        def find(node):
            if isinstance(node, Assignment):
                assigned.add(node.name)
            elif isinstance(node, If):
                for s in node.then_body: find(s)
                if node.else_body:
                    for s in node.else_body: find(s)
            elif isinstance(node, While):
                for s in node.body: find(s)
            
        for stmt in node_list:
            find(stmt)
        return assigned

    def visit_While(self, node: While):
        # 1. Setup Labels
        before_defs = self.current_defs.copy()
        L_pre = self.current_label
        L_header = self.new_label("while_header")
        L_body = self.new_label("while_body")
        L_exit = self.new_label("while_exit")
        
        self.emit(Jump(L_header))
        self.emit_label(L_header)
        
        # 2. Insert Phis for loop-carried variables
        modified_in_loop = self.collect_assigned_vars(node.body)
        phi_vars = {}
        phi_nodes = []
        
        vars_to_phi = [v for v in before_defs if v in modified_in_loop]
        
        for var in vars_to_phi:
            phi_name = self.new_var(var)
            phi = Phi(phi_name, []) 
            self.emit(phi)
            
            phi_vars[var] = phi_name
            phi_nodes.append((var, phi))
            self.current_defs[var] = phi_name
            
        # 3. Condition & Body
        cond_val = self.visit(node.condition)
        self.emit(Branch(cond_val, L_body, L_exit))
        
        self.emit_label(L_body)
        for stmt in node.body:
            self.visit(stmt)
        
        after_body_defs = self.current_defs.copy()
        L_body_end = self.current_label
        
        # 4. Backedge
        self.emit(Jump(L_header))
        
        # 5. Patch Phis
        for var, phi in phi_nodes:
            val_pre = before_defs[var]
            val_body = after_body_defs.get(var, phi_vars[var])
            phi.inputs = [
                (val_pre, L_pre),
                (val_body, L_body_end)
            ]
            
        self.emit_label(L_exit)
        
        # 6. Exit State
        final_defs = before_defs.copy()
        for var, phi_name in phi_vars.items():
            final_defs[var] = phi_name
        self.current_defs = final_defs

    def visit_If(self, node: If):
        cond_val = self.visit(node.condition)
        
        l_then = self.new_label("then")
        l_else = self.new_label("else")
        l_merge = self.new_label("merge")
        
        self.instructions.append(Branch(cond_val, l_then, l_else))
        initial_defs = self.current_defs.copy()
        
        # --- Then ---
        self.emit_label(l_then) 
        for stmt in node.then_body:
            self.visit(stmt)
        then_defs = self.current_defs.copy()
        pred_then = self.current_label
        self.instructions.append(Jump(l_merge))
        
        # --- Else ---
        self.emit_label(l_else)
        self.current_defs = initial_defs.copy()
        
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        else_defs = self.current_defs.copy()
        pred_else = self.current_label
        self.instructions.append(Jump(l_merge))
        
        # --- Merge ---
        self.emit_label(l_merge)
        
        modified = (
            set(then_defs.keys()) - set(initial_defs.keys())
        ) | (
            set(else_defs.keys()) - set(initial_defs.keys())
        )
        
        phis_to_emit = []
        merge_defs = initial_defs.copy() 
        
        for var in modified:
            val_then = then_defs.get(var)
            val_else = else_defs.get(var)
            
            if val_then and val_else:
                if val_then != val_else:
                    phi_target = self.new_var(var)
                    phi_instr = Phi(phi_target, inputs=[(val_then, pred_then), (val_else, pred_else)])
                    phis_to_emit.append(phi_instr)
                    merge_defs[var] = phi_target
                else:
                    merge_defs[var] = val_then
            else:
                if var in merge_defs:
                    del merge_defs[var]

        for phi in phis_to_emit:
            self.instructions.append(phi)
            
        self.current_defs = merge_defs


    def visit_BinaryOp(self, node: ASTBinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        target = self.new_temp()
        
        OP_MAP = {
            '+': 'add', 
            '<': 'lt', '>': 'gt', '==': 'eq', '!=': 'ne'
        }
        
        ir_op = OP_MAP.get(node.op, node.op)
        self.instructions.append(BinaryOp(ir_op, target, left, right))
        return target

    def visit_UnaryOp(self, node: ASTUnaryOp):
        operand = self.visit(node.operand)
        target = self.new_temp()
        
        if node.op == '-':
            self.instructions.append(UnaryOp('neg', target, operand))
        else:
            raise ValueError(f"Unknown unary op {node.op}")
            
        return target

    def visit_Literal(self, node: Literal):
        target = self.new_temp()
        self.instructions.append(Const(target, node.value))
        return target

    def visit_Variable(self, node: Variable):
        return self.get_current_def(node.name)
