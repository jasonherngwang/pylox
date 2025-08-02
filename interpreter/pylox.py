#!/usr/bin/env python3

import sys
from typing import List

from .scanner import Scanner
from .parser import Parser
from .interpreter import Interpreter
from .resolver import Resolver


class Lox:
    def __init__(self):
        self.interpreter = Interpreter()
        self.had_error = False
        self.had_runtime_error = False

    def main(self, args: List[str]) -> None:
        if len(args) > 1:
            print("Too many args! Try running as file or REPL.", file=sys.stderr)
            sys.exit(64)  # invalid args error code
        elif len(args) == 1:
            print("Running file")
            self.run_file(args[0])
        else:
            print("Running REPL")
            self.run_prompt()

    def run_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as file:
                source = file.read()
            self.run(source)

            if self.had_error:
                sys.exit(65)
            if self.had_runtime_error:
                sys.exit(70)
        except FileNotFoundError:
            print(f"Couldn't find {path}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            sys.exit(1)

    def run_prompt(self) -> None:
        print("pylox REPL; type 'exit()' to quit.")

        while True:
            try:
                line = input("> ")
                if line.strip() == "exit()":
                    break
                self.run(line)
                self.had_error = False
            except (EOFError, KeyboardInterrupt):
                break

    def run(self, source: str) -> None:
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()

        if self.had_error:
            return

        resolver = Resolver(self.interpreter)
        resolver.resolve_statements(statements)

        if self.had_error:
            return

        self.interpreter.interpret(statements)


def main():
    lox = Lox()
    lox.main(sys.argv[1:])


if __name__ == "__main__":
    main()
