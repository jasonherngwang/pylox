from enum import Enum, auto
from typing import Any


# auto() gives unique int values for each enum
class TokenType(Enum):
    # Keywords
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    # 1-char tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # 1, possibly 2-char tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    EOF = auto()


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: Any, line: int):
        self.type = token_type  # The category of token
        self.lexeme = lexeme  # The char sequence from the source code
        self.literal = (
            literal  # Char sequence converted to a Python number (float) or string
        )
        self.line = line  # Line num

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal}"

    def __repr__(self) -> str:
        # `!r` calls repr(), so we can see escape sequences
        return f"Token({self.type}, {self.lexeme!r}, {self.literal!r}, {self.line})"
