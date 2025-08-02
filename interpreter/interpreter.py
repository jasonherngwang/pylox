from typing import Any, List, Dict, Optional
import time
from .token_type import Token, TokenType
from .expressions import Expr, ExprVisitor
from .statements import Stmt, StmtVisitor
from .environment import Environment


class LoxCallable:
    def arity(self) -> int:
        """Number of args accepted."""
        raise NotImplementedError

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        """Call the callable with the args."""
        raise NotImplementedError


class ClockFunction(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"


class LoxFunction(LoxCallable):
    """Used for both functions and methods"""

    def __init__(
        self,
        declaration: Stmt.Function,
        closure: Environment,
        is_initializer: bool = False,
    ):
        self.declaration = declaration
        # Lexical scoping: Reference to the active environment when the function was CREATED
        # So we can look up variables in that environment
        self.closure = closure
        self.is_initializer = is_initializer

    # Only used for methods - which are just funcs bound to a class instance
    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        environment = Environment(self.closure)

        # Parameters are stored in the env, as local variables
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            # Special case for constructors
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: str,
        superclass: Optional["LoxClass"],
        methods: Dict[str, LoxFunction],
    ):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

        return None

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def __str__(self) -> str:
        return f"<class {self.name}>"


class LoxInstance:
    """Instance of a Lox class."""

    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: Dict[str, Any] = {}

    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"<{self.klass.name} instance>"


class RuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class ReturnException(Exception):
    """
    Not actually an exception; used for flow control.
    All `return` statements throw this, unwinding the stack, exiting deeply-nested logic.
    We catch it higher in the stack and then return that thrown value.
    """

    def __init__(self, value: Any):
        super().__init__()
        self.value = value


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals: Dict[Expr, int] = {}

        # Define built-in functions
        self.globals.define("clock", ClockFunction())

    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                if statement is not None:
                    self.execute(statement)
        except RuntimeError as error:
            print(f"Runtime error at line {error.token.line}: {error}")

    def resolve(self, expr: Expr, depth: int) -> None:
        """Resolve a variable reference to a specific environment depth."""
        self.locals[expr] = depth

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                if statement is not None:
                    self.execute(statement)
        finally:
            self.environment = previous

    def visit_literal_expr(self, expr: Expr.Literal) -> Any:
        return expr.value

    def visit_grouping_expr(self, expr: Expr.Grouping) -> Any:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Expr.Unary) -> Any:
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)

        # Unreachable
        return None

    def visit_binary_expr(self, expr: Expr.Binary) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        operator_type = expr.operator.type

        # Math
        if operator_type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif operator_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) or isinstance(right, str):
                # If either operand is a string, convert both to strings and concatenate
                return self.stringify(left) + self.stringify(right)
            else:
                raise RuntimeError(
                    expr.operator,
                    "Operands must be two numbers or at least one string.",
                )
        elif operator_type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if float(right) == 0:
                raise RuntimeError(expr.operator, "Division by zero.")
            return float(left) / float(right)
        elif operator_type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        # Comparison
        elif operator_type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif operator_type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif operator_type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif operator_type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)

        # Equality
        elif operator_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif operator_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        return None

    def check_number_operand(self, operator: Token, operand: Any) -> None:
        if not isinstance(operand, float):
            raise RuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if not isinstance(left, float) or not isinstance(right, float):
            raise RuntimeError(operator, "Operands must be numbers.")

    def is_truthy(self, obj: Any) -> bool:
        """Truthiness: Like Ruby, nil and false are falsy."""
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, bool):
            return str(obj).lower()

        if isinstance(obj, float):
            text = str(obj)
            # Remove trailing .0 for whole numbers
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(obj)

    # Statement visitors
    def visit_block_stmt(self, stmt: Stmt.Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_class_stmt(self, stmt: Stmt.Class) -> None:
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(
                method, self.environment, method.name.lexeme == "init"
            )
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)

    def visit_expression_stmt(self, stmt: Stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Stmt.Function) -> None:
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: Stmt.If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Stmt.Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt: Stmt.Return) -> None:
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise ReturnException(value)

    def visit_var_stmt(self, stmt: Stmt.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: Stmt.While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expr: Expr.Assign) -> Any:
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_variable_expr(self, expr: Expr.Variable) -> Any:
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name: Token, expr: Expr) -> Any:
        """Look up a variable in the appropriate environment."""
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visit_logical_expr(self, expr: Expr.Logical) -> Any:
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:  # AND
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_call_expr(self, expr: Expr.Call) -> Any:
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise RuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visit_get_expr(self, expr: Expr.Get) -> Any:
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RuntimeError(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr: Expr.Set) -> Any:
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_super_expr(self, expr: Expr.Super) -> Any:
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance, "super")

        # "this" is always one level nearer than "super"
        obj = self.environment.get_at(distance - 1, "this")

        method = superclass.find_method(expr.method.lexeme)

        if method is None:
            raise RuntimeError(
                expr.method, f"Undefined property '{expr.method.lexeme}'."
            )

        return method.bind(obj)

    def visit_this_expr(self, expr: Expr.This) -> Any:
        return self.lookup_variable(expr.keyword, expr)
