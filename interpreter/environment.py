from typing import Any, Dict, Optional
from .token_type import Token


class RuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class Environment:
    """
    Vars are store in a hash map.
    Environments can be chained in a hierarchy.
    """

    def __init__(self, enclosing: Optional["Environment"] = None):
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        # Lexical scoping - when getting or setting we search parent envs until we find it
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str) -> Any:
        """Use when we know how far up the hierarchy a variable lives"""
        return self.ancestor(distance).values[name]

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int) -> "Environment":
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment
