from typing import Any, List, Optional
from interpreter.expressions import ExprVisitor
from interpreter.statements import Stmt, StmtVisitor
from interpreter.token_type import Token


class ASTVisualizer(ExprVisitor[str], StmtVisitor[str]):
    """Generates HTML tree representation of AST nodes"""

    def __init__(self, max_depth: int = 15, max_nodes: int = 100):
        self.max_depth = max_depth
        self.max_nodes = max_nodes
        self.node_count = 0
        self.current_depth = 0

    def visualize_statements(self, statements: List[Optional[Stmt]]) -> str:
        if not statements:
            return '<div class="text-gray-500 italic text-center p-5">No statements to visualize</div>'

        self.node_count = 0
        self.current_depth = 0

        html_parts = ['<div class="m-0">']

        for i, stmt in enumerate(statements):
            if stmt is None:
                continue

            if self.node_count >= self.max_nodes:
                html_parts.append(
                    '<div class="text-red-600 italic bg-red-50 p-2 rounded border border-dashed border-red-300 m-1">... (truncated - too many nodes)</div>'
                )
                break

            html_parts.append(f'<div class="mb-3 last:mb-0" data-index="{i}">')
            html_parts.append(stmt.accept(self))
            html_parts.append("</div>")

            # Add separator between statements (but not after the last one)
            if i < len(statements) - 1 and statements[i + 1] is not None:
                html_parts.append('<div class="border-t border-gray-100 my-2"></div>')

        html_parts.append("</div>")
        return "".join(html_parts)

    def _get_node_type_classes(self, node_type: str) -> str:
        """Tailwind classes"""
        type_classes = {
            "Literal": "text-purple-700 bg-purple-100",
            "Variable": "text-green-700 bg-green-100",
            "BinaryExpr": "text-orange-700 bg-orange-100",
            "LogicalExpr": "text-orange-700 bg-orange-100",
            "FunctionStmt": "text-pink-700 bg-pink-100",
            "ClassStmt": "text-blue-700 bg-blue-100",
            "PrintStmt": "text-blue-700 bg-blue-100",
            "VarStmt": "text-blue-700 bg-blue-100",
            "BlockStmt": "text-blue-700 bg-blue-100",
            "IfStmt": "text-blue-700 bg-blue-100",
            "WhileStmt": "text-blue-700 bg-blue-100",
            "ReturnStmt": "text-blue-700 bg-blue-100",
            "ExpressionStmt": "text-blue-700 bg-blue-100",
            "AssignExpr": "text-blue-700 bg-blue-100",
            "UnaryExpr": "text-blue-700 bg-blue-100",
            "GroupingExpr": "text-blue-700 bg-blue-100",
            "CallExpr": "text-blue-700 bg-blue-100",
            "GetExpr": "text-blue-700 bg-blue-100",
            "SetExpr": "text-blue-700 bg-blue-100",
            "This": "text-blue-700 bg-blue-100",
            "Super": "text-blue-700 bg-blue-100",
        }
        return type_classes.get(node_type, "text-blue-700 bg-blue-100")

    def _create_node(
        self, node_type: str, content: str = "", children: List[str] = None
    ) -> str:
        self.node_count += 1

        if self.node_count > self.max_nodes:
            return '<div class="text-red-600 italic bg-red-50 p-2 rounded border border-dashed border-red-300 m-1">...</div>'

        if self.current_depth > self.max_depth:
            return f'<div class="text-red-600 italic bg-red-50 p-2 rounded border border-dashed border-red-300 m-1">... (max depth {self.max_depth} reached)</div>'

        # Base node classes
        base_classes = "m-0.5 p-1 px-2 rounded bg-white"
        type_classes = self._get_node_type_classes(node_type)

        if children:
            children_html = "".join(children)
            return f'''
            <details class="{base_classes}" open>
                <summary class="cursor-pointer py-1 select-none flex items-center gap-2 hover:bg-gray-50 rounded">
                    <span class="font-bold {type_classes} px-1.5 py-0.5 rounded text-xs">{node_type}</span>
                    {f'<span class="text-green-600 font-medium text-xs">{content}</span>' if content else ""}
                </summary>
                <div class="ml-4 pl-3 border-l-2 border-gray-200 mt-1">
                    {children_html}
                </div>
            </details>
            '''
        else:
            return f'''
            <div class="{base_classes}">
                <span class="font-bold {type_classes} px-1.5 py-0.5 rounded text-xs">{node_type}</span>
                {f'<span class="text-green-600 font-medium text-xs">{content}</span>' if content else ""}
            </div>
            '''

    def _format_token(self, token: Token) -> str:
        if token.lexeme != str(token.literal) and token.literal is not None:
            return f'"{token.lexeme}" ({token.literal})'
        elif token.lexeme:
            return f'"{token.lexeme}"'
        else:
            return str(token.token_type).split(".")[-1]

    def _format_value(self, value: Any) -> str:
        if value is None:
            return "nil"
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, str):
            return f'"{value}"'
        else:
            return str(value)

    # Statement visitors
    def visit_expression_stmt(self, stmt) -> str:
        self.current_depth += 1
        child = stmt.expression.accept(self)
        self.current_depth -= 1
        return self._create_node("ExpressionStmt", children=[child])

    def visit_print_stmt(self, stmt) -> str:
        self.current_depth += 1
        child = stmt.expression.accept(self)
        self.current_depth -= 1
        return self._create_node("PrintStmt", children=[child])

    def visit_var_stmt(self, stmt) -> str:
        content = self._format_token(stmt.name)
        children = []

        if stmt.initializer:
            self.current_depth += 1
            children.append(stmt.initializer.accept(self))
            self.current_depth -= 1

        return self._create_node("VarStmt", content, children if children else None)

    def visit_block_stmt(self, stmt) -> str:
        children = []
        self.current_depth += 1

        for statement in stmt.statements:
            if statement:
                children.append(statement.accept(self))

        self.current_depth -= 1
        return self._create_node("BlockStmt", children=children)

    def visit_if_stmt(self, stmt) -> str:
        children = []
        self.current_depth += 1

        # Condition
        children.append(
            '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">condition:</div>'
        )
        children.append(stmt.condition.accept(self))

        # Then branch
        children.append(
            '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">then:</div>'
        )
        children.append(stmt.then_branch.accept(self))

        # Else branch
        if stmt.else_branch:
            children.append(
                '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">else:</div>'
            )
            children.append(stmt.else_branch.accept(self))

        self.current_depth -= 1
        return self._create_node("IfStmt", children=children)

    def visit_while_stmt(self, stmt) -> str:
        children = []
        self.current_depth += 1

        children.append(
            '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">condition:</div>'
        )
        children.append(stmt.condition.accept(self))
        children.append(
            '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">body:</div>'
        )
        children.append(stmt.body.accept(self))

        self.current_depth -= 1
        return self._create_node("WhileStmt", children=children)

    def visit_function_stmt(self, stmt) -> str:
        content = self._format_token(stmt.name)
        if stmt.params:
            params = ", ".join(self._format_token(p) for p in stmt.params)
            content += f" ({params})"

        children = []
        self.current_depth += 1

        for statement in stmt.body:
            if statement:
                children.append(statement.accept(self))

        self.current_depth -= 1
        return self._create_node("FunctionStmt", content, children)

    def visit_return_stmt(self, stmt) -> str:
        children = []
        if stmt.value:
            self.current_depth += 1
            children.append(stmt.value.accept(self))
            self.current_depth -= 1

        return self._create_node("ReturnStmt", children=children if children else None)

    def visit_class_stmt(self, stmt) -> str:
        content = self._format_token(stmt.name)
        if stmt.superclass:
            content += f" < {self._format_token(stmt.superclass.name)}"

        children = []
        self.current_depth += 1

        for method in stmt.methods:
            children.append(method.accept(self))

        self.current_depth -= 1
        return self._create_node("ClassStmt", content, children if children else None)

    # Expression visitors
    def visit_binary_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(expr.left.accept(self))
        children.append(
            f'<div class="bg-yellow-400 text-yellow-800 px-1.5 py-0.5 rounded font-bold inline-block m-0.5 text-xs">{self._format_token(expr.operator)}</div>'
        )
        children.append(expr.right.accept(self))

        self.current_depth -= 1
        return self._create_node("BinaryExpr", children=children)

    def visit_grouping_expr(self, expr) -> str:
        self.current_depth += 1
        child = expr.expression.accept(self)
        self.current_depth -= 1
        return self._create_node("GroupingExpr", children=[child])

    def visit_literal_expr(self, expr) -> str:
        content = self._format_value(expr.value)
        return self._create_node("Literal", content)

    def visit_unary_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(
            f'<div class="bg-yellow-400 text-yellow-800 px-1.5 py-0.5 rounded font-bold inline-block m-0.5 text-xs">{self._format_token(expr.operator)}</div>'
        )
        children.append(expr.right.accept(self))

        self.current_depth -= 1
        return self._create_node("UnaryExpr", children=children)

    def visit_variable_expr(self, expr) -> str:
        content = self._format_token(expr.name)
        return self._create_node("Variable", content)

    def visit_assign_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(
            f'<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">{self._format_token(expr.name)} =</div>'
        )
        children.append(expr.value.accept(self))

        self.current_depth -= 1
        return self._create_node("AssignExpr", children=children)

    def visit_logical_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(expr.left.accept(self))
        children.append(
            f'<div class="bg-yellow-400 text-yellow-800 px-1.5 py-0.5 rounded font-bold inline-block m-0.5 text-xs">{self._format_token(expr.operator)}</div>'
        )
        children.append(expr.right.accept(self))

        self.current_depth -= 1
        return self._create_node("LogicalExpr", children=children)

    def visit_call_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(
            '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">function:</div>'
        )
        children.append(expr.callee.accept(self))

        if expr.arguments:
            children.append(
                '<div class="text-xs text-gray-500 font-semibold my-1 mt-2 tracking-wide">arguments:</div>'
            )
            for arg in expr.arguments:
                children.append(arg.accept(self))

        self.current_depth -= 1
        return self._create_node("CallExpr", children=children)

    def visit_get_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(expr.object.accept(self))
        children.append(
            f'<div class="bg-green-400 text-green-800 px-1.5 py-0.5 rounded font-medium inline-block m-0.5 text-xs">.{self._format_token(expr.name)}</div>'
        )

        self.current_depth -= 1
        return self._create_node("GetExpr", children=children)

    def visit_set_expr(self, expr) -> str:
        children = []
        self.current_depth += 1

        children.append(expr.object.accept(self))
        children.append(
            f'<div class="bg-green-400 text-green-800 px-1.5 py-0.5 rounded font-medium inline-block m-0.5 text-xs">.{self._format_token(expr.name)} =</div>'
        )
        children.append(expr.value.accept(self))

        self.current_depth -= 1
        return self._create_node("SetExpr", children=children)

    def visit_this_expr(self, expr) -> str:
        return self._create_node("This")

    def visit_super_expr(self, expr) -> str:
        content = f"super.{self._format_token(expr.method)}"
        return self._create_node("Super", content)
