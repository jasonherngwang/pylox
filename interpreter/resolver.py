from typing import List, Dict
from enum import Enum, auto
from .token_type import Token
from .expressions import Expr, ExprVisitor
from .statements import Stmt, StmtVisitor
from .interpreter import Interpreter


# Functions and classes for resolution context
class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    """Resolves variable scopes and tries to find errors via static analysis, before interpretation."""

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def resolve_statements(self, statements: List[Stmt]) -> None:
        for statement in statements:
            if statement is not None:
                self.resolve_stmt(statement)

    def resolve_stmt(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve_expr(self, expr: Expr) -> None:
        expr.accept(self)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            print(f"Error: Already a variable with name '{name.lexeme}' in this scope.")

        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if not self.scopes:
            return

        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolve_function(
        self, function: Stmt.Function, function_type: FunctionType
    ) -> None:
        enclosing_function = self.current_function
        self.current_function = function_type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve_statements(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt: Stmt.Class) -> None:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if (
            stmt.superclass is not None
            and stmt.name.lexeme == stmt.superclass.name.lexeme
        ):
            print("Error: A class can't inherit from itself.")

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve_expr(stmt.superclass)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass is not None:
            self.end_scope()

        self.current_class = enclosing_class

    def visit_expression_stmt(self, stmt: Stmt.Expression) -> None:
        self.resolve_expr(stmt.expression)

    def visit_function_stmt(self, stmt: Stmt.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: Stmt.If) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)

    def visit_print_stmt(self, stmt: Stmt.Print) -> None:
        self.resolve_expr(stmt.expression)

    def visit_return_stmt(self, stmt: Stmt.Return) -> None:
        if self.current_function == FunctionType.NONE:
            print("Error: Can't return from top-level code.")

        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                print("Error: Can't return a value from an initializer.")

            self.resolve_expr(stmt.value)

    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def visit_while_stmt(self, stmt: Stmt.While) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    # Expression visitors
    def visit_assign_expr(self, expr: Expr.Assign) -> None:
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: Expr.Binary) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_call_expr(self, expr: Expr.Call) -> None:
        self.resolve_expr(expr.callee)

        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_get_expr(self, expr: Expr.Get) -> None:
        self.resolve_expr(expr.object)

    def visit_grouping_expr(self, expr: Expr.Grouping) -> None:
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr: Expr.Literal) -> None:
        pass

    def visit_logical_expr(self, expr: Expr.Logical) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_set_expr(self, expr: Expr.Set) -> None:
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object)

    def visit_super_expr(self, expr: Expr.Super) -> None:
        if self.current_class == ClassType.NONE:
            print("Error: Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            print("Error: Can't use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr: Expr.This) -> None:
        if self.current_class == ClassType.NONE:
            print("Error: Can't use 'this' outside of a class.")
            return

        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: Expr.Unary) -> None:
        self.resolve_expr(expr.right)

    def visit_variable_expr(self, expr: Expr.Variable) -> None:
        if (
            self.scopes
            and expr.name.lexeme in self.scopes[-1]
            and self.scopes[-1][expr.name.lexeme] is False
        ):
            print(
                f"Error: Can't read local variable '{expr.name.lexeme}' in its own initializer."
            )

        self.resolve_local(expr, expr.name)
