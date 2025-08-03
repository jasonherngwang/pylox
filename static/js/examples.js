// PyLox code examples demonstrating different language features
const ExamplesModule = (function () {
  const examples = {
    math: `// Math expressions with operator precedence
print "Basic math:";
print 2 + 3 * 4;           // 14 (multiplication first)
print (2 + 3) * 4;         // 20 (parentheses override)
print 10 / 2 - 3;          // 2 (left-to-right for same precedence)

print "Comparisons:";
print 5 > 3;               // true
print 10 == 5 * 2;         // true
print 7 == 8;              // false

print "String operations:";
print "🐍 Lox" + " " + "Bagel!";
print "I can eat " + 42 + "pizzas";`,

    variables: `// Variable declarations and scoping
var x = 10;
print "Outside block: x = " + x;

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
var cat_count = 25;
if (cat_count >= 10) {
    print "You are an extreme cat lady 😻";
} else {
    print "You are a regular cat lady 🐈‍⬛";
}

print "For loop:";
for (var j = 1; j <= 3; j = j + 1) {
    print "Iteration: " + j;
}`,

    functions: `// Function declarations, calls, and recursion
print "Basic function:";
fun chow(food) {
    return "Nom " + food + "!";
}
print chow("bao");

print "Function with multiple params:";
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
class Animal {
    init(name, species, favorite_food) {
        this.name = name;
        this.species = species;
        this.favorite_food = favorite_food;
        this.belly = 0;
    }
    
    introduce() {
        return "Hi, I'm " + this.name + " the " + this.species + 
               " and I love " + this.favorite_food;
    }
    
    eat(food) {
        if (food == this.favorite_food) {
            this.belly = this.belly + 2;
            print this.name + " devours " + food + "";
        } else {
            this.belly = this.belly + 1;
            print this.name + " reluctantly eats " + food + "...";
        }
        print this.name + "'s belly is now " + this.belly + "/10 full!";
    }
    
    burp() {
        if (this.belly > 5) {
            print "*burp*";
            this.belly = this.belly - 1;
        } else {
            print this.name + " is still hungry...";
        }
    }
}

var shelly = Animal("Shelly", "armadillo", "catfish");
print shelly.introduce();
shelly.eat("catfish");
shelly.eat("bubblegum");
shelly.burp();

print "Multiple instances:";
var chubbs = Animal("Chubbs", "crocodile", "key lime pie");
print chubbs.introduce();
chubbs.eat("steak");
chubbs.eat("key lime pie");
chubbs.burp();

print "Instance fields:";
shelly.nap_spot = "sunny window";
print shelly.name + " loves napping on the " + shelly.nap_spot;`,

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

class Flamingo < Animal {
    init(name, breed) {
        super.init(name, "flamingo");
        this.breed = breed;
    }
    
    speak() {
        return this.name + " squawks!";
    }
    
    info() {
        return super.info() + " (" + this.breed + ")";
    }
    
    flapWings() {
        return this.name + " flaps wings";
    }
}

var palmer = Flamingo("Palmer", "Flamingo");
print palmer.speak();
print palmer.info();
print palmer.flapWings();`,

    functional: `// First-class functions
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
print "Triple 4: " + triple(4);`,
  };

  return {
    getExample: (type) => examples[type],
    getAllExamples: () => Object.keys(examples),
    hasExample: (type) => type in examples,
  };
})();

window.ExamplesModule = ExamplesModule;
