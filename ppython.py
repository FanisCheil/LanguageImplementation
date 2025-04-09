import sys
from Token import Token
from AST import AST
import Scanner
from Expression import Print

def error(line: int, message: str) -> None:
    print(f"\nError on line {line}: {message}\n")

def run(source: str, env: dict, verbose: bool = True) -> None:
    if not source.strip():
        print("\nError: Empty input. Please enter a valid expression.\n")
        return

    try:
        if verbose:
            print("\nTokenization Process")
        # Create a Scanner object
        scanner = Scanner.Scanner(source)

        # Call scan_tokens() to break the input into tokens
        tokens = scanner.scan_tokens()

        # Print the tokenized output to validate it is working
        if verbose:
            for token in tokens:
                print(token)

        if verbose:
            print("\nAST Construction")
        # Pass the tokens to AST, which constructs an Abstract Syntax Tree
        ast = AST(tokens)

        # Print the AST for debugging
        if verbose:
            print(ast.tree)

        if verbose:
            print("\nEvaluation Result")
        # Evaluate the AST and print the final result
        
        result = ast.evaluate(env, verbose=verbose)

        # Only print final result if it's not a Print expression
        # If it's not a print statement, output the result
        if isinstance(ast.tree, Print):
          print(f"{result}")
                
            

    # Handle different error types dynamically
    except SyntaxError as e:
        error(scanner._line, f"Syntax Error: {str(e)}")  
    except TypeError as e:
        error(scanner._line, f"Type Error: {str(e)}")
    except ZeroDivisionError as e:
        error(scanner._line, f"Math Error: {str(e)}")
    except OverflowError as e:
        error(scanner._line, f"Overflow Error: {str(e)}")
    except Exception as e:
        error(scanner._line, f"Unexpected Error: {str(e)}")

# Run a prompt where users can enter expressions
def run_prompt() -> None:
    print("Type expressions to evaluate, or type 'exit()' to quit. Type 'script()' to enter multi-line mode.\n")
    env = {}  # Shared environment for variables

    while True:
        print("\n>>> ", end="")
        try:
            line = input().strip()
            if not line:
                continue

            # If the user types exit(), terminate the program
            if line.lower() == "exit()": 
                print("\nExiting interpreter. Goodbye!\n")
                break

            # If user enters script() to start multiline mode
            if line.lower() == "script()":
                run_script(env)
                continue

            # Use verbose=True for single-line input tests
            run(line, env, verbose=True)

        # If the user presses Ctrl+C, exit the program gracefully
        except KeyboardInterrupt:
            print("\n\nExiting interpreter. Goodbye!\n")
            break

# Run script mode for multiple lines until 'end()'
def run_script(env: dict) -> None:
    print("\nEnter your program. Type 'end()' to finish:\n")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() == "end()":
                break
            if line.strip():
                lines.append(line)
        except KeyboardInterrupt:
            print("\n\nScript input cancelled.")
            return

    for line in lines:
        # Pass verbose=False when handling script mode
        run(line, env, verbose=False)

# Run file input from a .txt script
def run_file(filename: str):
    env = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    # Pass verbose=False when handling file input
                    run(line, env, verbose=False)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_file(sys.argv[1])  # Handle .txt file input
    else:
        run_prompt()  # Handle interactive one-line prompt
