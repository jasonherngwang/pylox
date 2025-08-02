// PyLox code examples demonstrating different language features
const ExamplesModule = (function () {
  const examples = {
    math: `// Arithmetic expressions with operator precedence
print "Basic arithmetic:";
print 2 + 3 * 4;           // 14 (multiplication first)
print (2 + 3) * 4;         // 20 (parentheses override)
print 10 / 2 - 3;          // 2 (left-to-right for same precedence)

print "Comparisons:";
print 5 > 3;               // true
print 10 == 5 * 2;         // true
print 7 != 8;              // true

print "String operations:";
print "Hello" + " " + "World!";
print "The answer is " + 42;`,

    variables: `// Variable declarations and scoping
print "Global variables:";
var global = "I'm global";
var x = 10;

print "Block scoping:";
{
    var local = "I'm local";
    var x = 20;  // Shadows global x
    print "Inside block: x = " + x + ", local = " + local;
}

print "Outside block: x = " + x;
// print local;  // Would error - local is out of scope

print "Variable assignment:";
var counter = 0;
counter = counter + 1;
print "Counter: " + counter;`,

    control: `// Control flow: if/else and loops
print "If/else statements:";
var age = 25;
if (age >= 18) {
    print "You are an adult";
} else {
    print "You are a minor";
}

print "While loop:";
var i = 1;
while (i <= 3) {
    print "While iteration: " + i;
    i = i + 1;
}

print "For loop:";
for (var j = 1; j <= 3; j = j + 1) {
    print "For iteration: " + j;
}

print "Nested control flow:";
for (var x = 1; x <= 3; x = x + 1) {
    if (x == 2) {
        print "Found the number 2!";
    }
}`,

    functions: `// Function declarations, calls, and recursion
print "Basic function:";
fun greet(name) {
    return "Hello, " + name + "!";
}
print greet("PyLox");

print "Function with multiple parameters:";
fun add(a, b) {
    return a + b;
}
print "5 + 3 = " + add(5, 3);

print "Recursive function:";
fun factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
print "5! = " + factorial(5);

print "Fibonacci sequence:";
fun fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
for (var i = 0; i < 8; i = i + 1) {
    print "fib(" + i + ") = " + fibonacci(i);
}`,

    closures: `// Closures: functions that capture their environment
print "Counter using closures:";
fun makeCounter() {
    var count = 0;
    fun increment() {
        count = count + 1;
        return count;
    }
    return increment;
}

var counter1 = makeCounter();
var counter2 = makeCounter();

print "Counter1: " + counter1();  // 1
print "Counter1: " + counter1();  // 2
print "Counter2: " + counter2();  // 1 (independent)
print "Counter1: " + counter1();  // 3

print "Adder factory:";
fun makeAdder(x) {
    fun addX(y) {
        return x + y;
    }
    return addX;
}

var add5 = makeAdder(5);
var add10 = makeAdder(10);
print "add5(3) = " + add5(3);     // 8
print "add10(7) = " + add10(7);   // 17`,

    classes: `// Classes with methods and constructors
print "Basic class definition:";
class Person {
    init(name, age) {
        this.name = name;
        this.age = age;
    }
    
    introduce() {
        return "Hi, I'm " + this.name + " and I'm " + 
               this.age + " years old.";
    }
    
    birthday() {
        this.age = this.age + 1;
        print this.name + " is now " + this.age + "!";
    }
}

var alice = Person("Alice", 30);
print alice.introduce();
alice.birthday();

print "Multiple instances:";
var bob = Person("Bob", 25);
print bob.introduce();

print "Instance fields:";
alice.hobby = "reading";
print alice.name + " likes " + alice.hobby;`,

    inheritance: `// Class inheritance with super calls
print "Inheritance example:";

class Animal {
    init(name, species) {
        this.name = name;
        this.species = species;
    }
    
    speak() {
        return this.name + " makes a sound";
    }
    
    info() {
        return this.name + " is a " + this.species;
    }
}

class Dog < Animal {
    init(name, breed) {
        super.init(name, "dog");
        this.breed = breed;
    }
    
    speak() {
        return this.name + " barks!";
    }
    
    info() {
        return super.info() + " (" + this.breed + ")";
    }
    
    wagTail() {
        return this.name + " wags tail happily";
    }
}

var buddy = Dog("Buddy", "Golden Retriever");
print buddy.speak();
print buddy.info();
print buddy.wagTail();

print "Polymorphism:";
var animal = buddy;  // Dog instance treated as Animal
print animal.speak();  // Calls Dog's speak method`,

    functional: `// First-class functions: functions as values
print "Functions as values:";
fun add(a, b) { return a + b; }
fun multiply(a, b) { return a * b; }

var operation = add;  // Function stored in variable
print "Using stored function: " + operation(5, 3);

print "Higher-order functions:";
fun applyOperation(x, y, op) {
    return op(x, y);
}

print "Apply add: " + applyOperation(10, 5, add);
print "Apply multiply: " + applyOperation(10, 5, multiply);

print "Function that returns function:";
fun createMultiplier(factor) {
    fun multiplier(x) {
        return x * factor;
    }
    return multiplier;
}

var double = createMultiplier(2);
var triple = createMultiplier(3);
print "Double 7: " + double(7);
print "Triple 4: " + triple(4);

print "Using functions with higher-order functions:";
fun twice(f, x) {
    return f(f(x));
}

fun increment(n) {
    return n + 1;
}

// Using named function instead of anonymous
var result = twice(increment, 5);
print "Increment 5 twice: " + result;  // 7

print "Function arrays (using variables):";
var operations = add;  // Start with one function
print "First operation 3,4: " + operations(3, 4);
operations = multiply;  // Switch to different function
print "Second operation 3,4: " + operations(3, 4);`,
  };

  return {
    getExample: (type) => examples[type],
    getAllExamples: () => Object.keys(examples),
    hasExample: (type) => type in examples,
  };
})();

window.ExamplesModule = ExamplesModule;
