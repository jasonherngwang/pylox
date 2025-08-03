from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
import sys
import re
from io import StringIO
from interpreter import Lox
from interpreter.scanner import Scanner
from interpreter.parser import Parser, ParseError
from .ast_visualizer import ASTVisualizer


def index(request):
    return render(request, "pylox_web/index.html")


def turbo_stream_update(target, content):
    return f'<turbo-stream action="update" target="{target}"><template>{content}</template></turbo-stream>'


def highlight_error_messages(output):
    lines = output.split("\n")
    highlighted_lines = []

    for i, line in enumerate(lines):
        # Common error patterns
        if re.match(r"^(Parse error|Runtime error|Error)", line):
            # Wrap error lines in red span with background
            highlighted_line = f'<span style="color: #dc2626; font-weight: bold; background-color: #fef2f2; padding: 2px 4px; border-radius: 3px;">⚠️ {line}</span>'
            highlighted_lines.append(highlighted_line)

            # Add separator after error if there's more content
            if i < len(lines) - 1 and lines[i + 1].strip():
                highlighted_lines.append(
                    '<span style="color: #6b7280; margin: 8px 0; display: block;">--- Output ---</span>'
                )
        else:
            highlighted_lines.append(line)

    return "\n".join(highlighted_lines)


def generate_ast_visualization(code: str) -> str:
    try:
        scanner = Scanner(code)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()

        visualizer = ASTVisualizer(max_depth=20, max_nodes=500)
        return visualizer.visualize_statements(statements)

    except ParseError as e:
        return f'<div class="text-red-600 bg-red-50 border border-red-300 rounded-lg p-3 font-mono text-sm my-2">Parse Error: {str(e)}</div>'
    except Exception as e:
        return f'<div class="text-red-600 bg-red-50 border border-red-300 rounded-lg p-3 font-mono text-sm my-2">AST Generation Error: {str(e)}</div>'


def execute(request):
    code = request.POST.get("code", "").strip() if request.method == "POST" else ""

    if not code:
        # Return both empty output and empty AST
        output_content = render_to_string(
            "pylox_web/output.html",
            {"content": "Start typing Lox code to see results..."},
        )
        ast_content = render_to_string(
            "pylox_web/ast.html",
            {
                "ast_html": '<div class="text-gray-500 italic text-center p-5">No code to parse</div>'
            },
        )

        return HttpResponse(
            turbo_stream_update("output", output_content)
            + turbo_stream_update("ast-display", ast_content),
            content_type="text/vnd.turbo-stream.html",
        )

    ast_html = generate_ast_visualization(code)
    ast_content = render_to_string("pylox_web/ast.html", {"ast_html": ast_html})

    try:
        captured_output = StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = sys.stderr = captured_output

        lox = Lox()

        lox.had_error = False
        lox.had_runtime_error = False

        lox.run(code)
        output = captured_output.getvalue().strip()

        sys.stdout = old_stdout
        sys.stderr = old_stderr

        if not output:
            result_content = render_to_string(
                "pylox_web/output.html",
                {"content": "Code executed successfully (no output)"},
            )
        else:
            # Highlight error messages in red
            highlighted_output = highlight_error_messages(output)
            result_content = render_to_string(
                "pylox_web/output.html", {"content": highlighted_output}
            )
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        result_content = render_to_string(
            "pylox_web/output.html", {"content": f"Error: {str(e)}"}
        )

    # Return both execution output and AST visualization
    return HttpResponse(
        turbo_stream_update("output", result_content)
        + turbo_stream_update("ast-display", ast_content),
        content_type="text/vnd.turbo-stream.html",
    )
