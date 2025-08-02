from io import StringIO
from contextlib import redirect_stdout
from ..pylox import Lox


def run_lox_code(code: str) -> str:
    """Run Lox code and capture output."""
    lox = Lox()

    # Capture stdout
    captured_output = StringIO()
    try:
        with redirect_stdout(captured_output):
            lox.run(code)
        return captured_output.getvalue().strip()
    except Exception as e:
        return f"Error: {e}"


def test_variables():
    """Test variable declarations and assignments."""
    print("Testing Variables...")

    code = """
        var a = 1;
        var b = 2;
        print a + b;
    """
    result = run_lox_code(code)
    assert result == "3", f"Expected '3', got '{result}'"
    print("✓ Variable declarations and operations")

    code = """
        var a = "Hello";
        var b = " World";
        print a + b;
    """
    result = run_lox_code(code)
    assert result == "Hello World", f"Expected 'Hello World', got '{result}'"
    print("✓ String variable concatenation")


def test_scoping():
    """Test variable scoping."""
    print("Testing Scoping...")

    code = """
        var a = "global a";
        var b = "global b";
        var c = "global c";
        {
            var a = "outer a";
            var b = "outer b";
            {
                var a = "inner a";
                print a;
                print b;
                print c;
            }
            print a;
            print b;
        }
        print a;
        print b;
    """
    expected = "inner a\nouter b\nglobal c\nouter a\nouter b\nglobal a\nglobal b"
    result = run_lox_code(code)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ Block scoping")


def test_control_flow():
    """Test if statements and loops."""
    print("Testing Control Flow...")

    # If statement
    code = """
        var a = 1;
        if (a == 1) {
            print "a is 1";
        } else {
            print "a is not 1";
        }
    """
    result = run_lox_code(code)
    assert result == "a is 1", f"Expected 'a is 1', got '{result}'"
    print("✓ If statement")

    # While loop
    code = """
        var i = 0;
        while (i < 3) {
            print i;
            i = i + 1;
        }
    """
    result = run_lox_code(code)
    assert result == "0\n1\n2", f"Expected '0\\n1\\n2', got '{result}'"
    print("✓ While loop")

    # For loop
    code = """
        for (var i = 0; i < 3; i = i + 1) {
            print i;
        }
    """
    result = run_lox_code(code)
    assert result == "0\n1\n2", f"Expected '0\\n1\\n2', got '{result}'"
    print("✓ For loop")


def test_functions():
    """Test function declarations and calls."""
    print("Testing Functions...")

    code = """
        fun greet(name) {
            return "Hello, " + name + "!";
        }
        
        print greet("World");
    """
    result = run_lox_code(code)
    assert result == "Hello, World!", f"Expected 'Hello, World!', got '{result}'"
    print("✓ Function declaration and call")

    # Recursion
    code = """
        fun factorial(n) {
            if (n <= 1) return 1;
            return n * factorial(n - 1);
        }
        
        print factorial(5);
    """
    result = run_lox_code(code)
    assert result == "120", f"Expected '120', got '{result}'"
    print("✓ Recursive function")

    # Closures
    code = """
        fun makeCounter() {
            var i = 0;
            fun count() {
                i = i + 1;
                return i;
            }
            return count;
        }
        
        var counter = makeCounter();
        print counter();
        print counter();
    """
    result = run_lox_code(code)
    assert result == "1\n2", f"Expected '1\\n2', got '{result}'"
    print("✓ Closures")


def test_classes():
    """Test class declarations and instances."""
    print("Testing Classes...")

    code = """
        class Bacon {
            eat() {
                print "Crunch crunch crunch!";
            }
        }
        
        Bacon().eat();
    """
    result = run_lox_code(code)
    assert result == "Crunch crunch crunch!", (
        f"Expected 'Crunch crunch crunch!', got '{result}'"
    )
    print("✓ Class declaration and method call")

    # Constructor
    code = """
        class Cake {
            init(flavor) {
                this.flavor = flavor;
            }
            
            taste() {
                return "Mmm, " + this.flavor + " cake!";
            }
        }
        
        var cake = Cake("chocolate");
        print cake.taste();
    """
    result = run_lox_code(code)
    assert result == "Mmm, chocolate cake!", (
        f"Expected 'Mmm, chocolate cake!', got '{result}'"
    )
    print("✓ Class constructor and properties")


def test_inheritance():
    """Test class inheritance."""
    print("Testing Inheritance...")

    code = """
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }
        
        class BostonCream < Doughnut {
            cook() {
                super.cook();
                print "Pipe full of custard and coat with chocolate.";
            }
        }
        
        BostonCream().cook();
    """
    expected = "Fry until golden brown.\nPipe full of custard and coat with chocolate."
    result = run_lox_code(code)
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ Class inheritance and super calls")


def test_built_ins():
    """Test built-in functions."""
    print("Testing Built-ins...")

    code = """
        print clock() > 0;
    """
    result = run_lox_code(code)
    assert result == "true", f"Expected 'true', got '{result}'"
    print("✓ Built-in clock function")


def main():
    """Run all tests."""

    try:
        test_variables()
        print()
        test_scoping()
        print()
        test_control_flow()
        print()
        test_functions()
        print()
        test_classes()
        print()
        test_inheritance()
        print()
        test_built_ins()
        print()
        print("🎉 All comprehensive tests passed!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
