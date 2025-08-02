from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar, Optional
from .token_type import Token
from .expressions import Expr

T = TypeVar("T")


class StmtVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> T:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> T:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> T:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> T:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> T:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> T:
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt: "Function") -> T:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: "Return") -> T:
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: "Class") -> T:
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor[T]) -> T:
        pass


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_block_stmt(self)


class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_if_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_while_stmt(self)


class Function(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_function_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: Optional[Expr]):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_return_stmt(self)


class Class(Stmt):
    def __init__(
        self, name: Token, superclass: Optional[Expr], methods: List[Function]
    ):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor: StmtVisitor[T]) -> T:
        return visitor.visit_class_stmt(self)


Stmt.Expression = Expression
Stmt.Print = Print
Stmt.Var = Var
Stmt.Block = Block
Stmt.If = If
Stmt.While = While
Stmt.Function = Function
Stmt.Return = Return
Stmt.Class = Class
