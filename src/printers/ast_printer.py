from src.ast_nodes import (
    Assignment,
    BinaryOp,
    If,
    Literal,
    Print,
    Program,
    UnaryOp,
    Variable,
    While,
)


class ASTPrinter:
    """Render AST nodes as an indented tree."""

    def format(self, node):
        return "\n".join(self._format_node(node))

    def _format_node(self, node, indent=0):
        method_name = f"_format_{type(node).__name__}"
        formatter = getattr(self, method_name, self._format_unknown)
        return formatter(node, indent)

    def _line(self, indent, text):
        return f"{'  ' * indent}{text}"

    def _format_unknown(self, node, indent):
        raise TypeError(f"Unsupported AST node: {type(node).__name__}")

    def _format_Program(self, node: Program, indent):
        lines = [self._line(indent, "Program")]
        for statement in node.statements:
            lines.extend(self._format_node(statement, indent + 1))
        return lines

    def _format_Assignment(self, node: Assignment, indent):
        lines = [self._line(indent, f"Assignment(name={node.name})")]
        lines.extend(self._format_node(node.value, indent + 1))
        return lines

    def _format_Print(self, node: Print, indent):
        lines = [self._line(indent, "Print")]
        lines.extend(self._format_node(node.value, indent + 1))
        return lines

    def _format_While(self, node: While, indent):
        lines = [self._line(indent, "While")]
        lines.append(self._line(indent + 1, "Condition"))
        lines.extend(self._format_node(node.condition, indent + 2))
        lines.append(self._line(indent + 1, "Body"))
        for statement in node.body:
            lines.extend(self._format_node(statement, indent + 2))
        return lines

    def _format_If(self, node: If, indent):
        lines = [self._line(indent, "If")]
        lines.append(self._line(indent + 1, "Condition"))
        lines.extend(self._format_node(node.condition, indent + 2))
        lines.append(self._line(indent + 1, "Then"))
        for statement in node.then_body:
            lines.extend(self._format_node(statement, indent + 2))
        if node.else_body is not None:
            lines.append(self._line(indent + 1, "Else"))
            for statement in node.else_body:
                lines.extend(self._format_node(statement, indent + 2))
        return lines

    def _format_BinaryOp(self, node: BinaryOp, indent):
        lines = [self._line(indent, f"BinaryOp(op={node.op})")]
        lines.extend(self._format_node(node.left, indent + 1))
        lines.extend(self._format_node(node.right, indent + 1))
        return lines

    def _format_UnaryOp(self, node: UnaryOp, indent):
        lines = [self._line(indent, f"UnaryOp(op={node.op})")]
        lines.extend(self._format_node(node.operand, indent + 1))
        return lines

    def _format_Literal(self, node: Literal, indent):
        return [self._line(indent, f"Literal(value={repr(node.value)})")]

    def _format_Variable(self, node: Variable, indent):
        return [self._line(indent, f"Variable(name={node.name})")]
