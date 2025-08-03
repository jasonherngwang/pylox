from typing import List, Dict, Any
from .token_type import Token, TokenType


class Scanner:
    keywords: Dict[str, TokenType] = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0  # First char in the lexeme
        self.current = 0  # Char we're currently looking at
        self.line = 1  # Line num

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        c = self.consume_and_advance()

        # 1-char
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)

        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == "*":
            self.add_token(TokenType.STAR)

        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)

        # 2-chars
        # We need to look ahead to the next char to see if the 2 chars together form a lexeme
        elif c == "!":
            self.add_token(
                TokenType.BANG_EQUAL if self.consume_if_match("=") else TokenType.BANG
            )
        elif c == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.consume_if_match("=") else TokenType.EQUAL
            )

        elif c == "<":
            self.add_token(
                TokenType.LESS_EQUAL if self.consume_if_match("=") else TokenType.LESS
            )
        elif c == ">":
            self.add_token(
                TokenType.GREATER_EQUAL
                if self.consume_if_match("=")
                else TokenType.GREATER
            )

        elif c == "/":
            if self.consume_if_match("/"):
                # A comment goes until the end of the line
                while self.peek() != "\n" and not self.is_at_end():
                    self.consume_and_advance()
            else:
                self.add_token(TokenType.SLASH)

        # Whitespace
        elif c in [" ", "\r", "\t"]:
            pass  # Ignore whitespace
        elif c == "\n":
            self.line += 1

        # String literals
        elif c == '"':
            self.string_literal()

        # Digits and identifiers (variables)
        else:
            if self.is_digit(c):
                self.number_literal()
            elif self.is_alpha(c):
                self.identifier()
            else:
                print(f"Can't recognize char '{c}' on line {self.line}")

    def consume_and_advance(self) -> str:
        if self.is_at_end():
            return "\0"
        self.current += 1
        return self.source[self.current - 1]

    def consume_if_match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_at_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string_literal(self) -> None:
        # Opening "
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.consume_and_advance()

        if self.is_at_end():
            print(f"Unterminated string at line {self.line}")
            return

        # Closing "
        self.consume_and_advance()

        # Trim off the enclosing "s to get the string only
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number_literal(self) -> None:
        while self.is_digit(self.peek()):
            self.consume_and_advance()

        # Deal with decimals
        if self.peek() == "." and self.is_digit(self.peek_at_next()):
            # Consume decimal
            self.consume_and_advance()

            # No more decimals expected after this; consume til end
            while self.is_digit(self.peek()):
                self.consume_and_advance()

        value = float(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, value)

    # Reserved keywords like `var`
    def identifier(self) -> None:
        while self.is_alphanumeric(self.peek()):
            self.consume_and_advance()

        text = self.source[self.start : self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def is_digit(self, c: str) -> bool:
        return c >= "0" and c <= "9"

    def is_alpha(self, c: str) -> bool:
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    def is_alphanumeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def add_token(self, token_type: TokenType, literal: Any = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
