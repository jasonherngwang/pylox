"""
Expression AST nodes with Visitor Pattern

From https://github.com/munificent/craftinginterpreters/blob/master/java/com/craftinginterpreters/lox/Expr.java
This Python implementation is a bit different from the original Java:
- ABC and abstractmethod instead of Java abstract class and interface
- Uses Python's form of generics - TypeVar
- Simulates inner classes

Visitor Pattern

We have many expression classes with unique implementations of behavior, such as evaluation and scope analysis.
Additional behaviors relevant to all these classes may be added in the future.
Problem: When a new behavior is added, we then have to update all those classes.

The Visitor Pattern is a way of organizing those methods differently. We consolidate all of them
into a single class, and organize the methods by context.

So instead of 10 different classes each with its own method (Binary.evaluate, Literal.evaluate, ...)
We have 1 contextual class "Intepreter" which has 10 different methods (Interpreter.visit_binary, Interpreter.visit_literal)

The logic is the same; just "grouped-by" in a different way. This makes it easy to add new behavior without touching all 10 classes.
The tradeoff is that when we add a new expression class, its behavior needs to be update in all the contextual classes.

This file is just the scaffolding for setting up the Visitor pattern; the actual logic is in the interpreter, resolver, etc.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Generic, TypeVar
from .token_type import Token

T = TypeVar("T")


class ExprVisitor(ABC, Generic[T]):
    @abstractmethod
    def visit_assign_expr(self, expr: "Assign") -> T:
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: "Binary") -> T:
        pass

    @abstractmethod
    def visit_call_expr(self, expr: "Call") -> T:
        pass

    @abstractmethod
    def visit_get_expr(self, expr: "Get") -> T:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: "Grouping") -> T:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: "Literal") -> T:
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: "Logical") -> T:
        pass

    @abstractmethod
    def visit_set_expr(self, expr: "Set") -> T:
        pass

    @abstractmethod
    def visit_super_expr(self, expr: "Super") -> T:
        pass

    @abstractmethod
    def visit_this_expr(self, expr: "This") -> T:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: "Unary") -> T:
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: "Variable") -> T:
        pass


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor[T]) -> T:
        pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_literal_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_variable_expr(self)


class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_assign_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_logical_expr(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_call_expr(self)


class Get(Expr):
    def __init__(self, obj: Expr, name: Token):
        self.object = obj
        self.name = name

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_get_expr(self)


class Set(Expr):
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.object = obj
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_set_expr(self)


class This(Expr):
    def __init__(self, keyword: Token):
        self.keyword = keyword

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_this_expr(self)


class Super(Expr):
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def accept(self, visitor: ExprVisitor[T]) -> T:
        return visitor.visit_super_expr(self)


Expr.Assign = Assign
Expr.Binary = Binary
Expr.Call = Call
Expr.Get = Get
Expr.Grouping = Grouping
Expr.Literal = Literal
Expr.Logical = Logical
Expr.Set = Set
Expr.Super = Super
Expr.This = This
Expr.Unary = Unary
Expr.Variable = Variable
