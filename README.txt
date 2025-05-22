LUMA Language - Interpreter Project
-----------------------------------

Student ID: 100675725 
Course: Language Design and Implementation (6CC509)  
Year: 2024–2025  

======================================
How to Run the Luma Interpreter
======================================

Requirements:
- Python 3.8 or higher
- No external libraries required (pure Python)

To run a Luma program:

1. Open terminal or command prompt.
2. Navigate to the folder where 'luma.py' is located.
3. Run the interpreter with:
   python luma.py Tests/program.luma

Example:
   python luma.py Tests/Game.luma
   (all the running commands for the included tests i have implemnded in the tests folder are including in the testRunningCommands.txt)
To enter REPL mode (interactive shell):
   python luma.py

======================================
Language Features
======================================

✅ Arithmetic expressions (+, -, *, /, %, **)  
✅ Boolean logic (==, !=, <, <=, >, >=, and, or, !)  
✅ Strings (single or double quotes supported)  
✅ Input via: ask  
✅ Output via: print  
✅ Global and local variables  
✅ Control Flow:
   - if / elsif / else
   - while loops
✅ Functions:
   - Defined with 'fun'
   - Support for parameters
   - Optional return statement
✅ Lists:
   - Literals: [1, 2, 3]
   - Index access: myList[0]
✅ Block syntax with braces: {}

✅ Built-in Conversion Functions:
   - float(value): Converts value to float
   - string(value): Converts value to string

======================================
🔄 Variable Scope (Global vs Local)
======================================

- Variables declared **outside any block or function** are global.
- Variables declared **inside a function** are local to that function.
- In `for` loops, only the loop variable is local — all other variables used inside the loop are global unless shadowed.

Examples:
---------
x = 5             # global
fun test() {
  x = 10          # local (does not affect global x)
  print x
}
test()
print x           # still 5

======================================
Luma Syntax Examples
======================================

Variables:
----------
x = 10
name = "Fanis"

Printing and Input:
-------------------
print "Hello World"
username = ask "Enter your name: "

Arithmetic:
-----------
a = 5 + 3 * 2

Conditionals:
-------------
if (x > 5) {
  print "x is greater than 5"
} elsif (x == 5) {
  print "x is equal to 5"
} else {
  print "x is less than 5"
}

Loops:
------
i = 0
while (i < 5) {
  print i
  i = i + 1
}

Functions:
----------
fun greet(name) {
  print "Hello " + name
}

greet("Fanis")

fun add(a, b) {
  return a + b
}

result = add(2, 3)
print result

Type Conversion:
----------------
value = "3.14"
num = float(value)     # converts string to float
print num              # prints 3.14

age = 25
message = "Age: " + string(age)
print message          # prints Age: 25

Lists:
------
myList = [10, 20, 30]
print myList[1]        # prints 20

======================================
📁 File Structure (example)
======================================

luma.py
Scanner.py
Token.py
AST.py
Expression.py
Environment.py
Tests/
  └── test.luma
readme.txt

