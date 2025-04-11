import sys
from Token import Token
from AST import AST
import Scanner
from Expression import Print

#Define a function named error which takes the line number 
#where the error happened and the error message and print it
def error(line: int, message: str) -> None:
    print(f"\nError on line {line}: {message}\n")


#This is the core function that takes a string of Luma code and runs it
#it accepts:
  #source: the user's code as a string
  #env: the enviroment (dictionary that olds variables)
  #verbose: if True, it prints debug info at each stage(tokenization, AST, evaluation)
def run(source: str, env: dict, verbose: bool = True) -> None:

    #This checks if the code is empty and if so a warning is printed
    if not source.strip():
        print("\nError: Empty input. Please enter a valid expression.\n")
        return
   
    try:
        if verbose:
            print("\nTokenization Process")

        # Create a Scanner object to tokenize the user's code
        scanner = Scanner.Scanner(source)

        # Call scan_tokens() to break the input into a list of tokens
        tokens = scanner.scan_tokens()

        
        # if verbose is True Print the tokenized output to validate it is working
        if verbose:
            for token in tokens:
                print(token)

        if verbose:
            print("\nAST Construction")

        # Pass the tokens to AST, which constructs an Abstract Syntax Tree
        ast = AST(tokens)
       

        
        if verbose:
            print(ast.tree) # Print the AST for debugging

        if verbose:
            print("\nEvaluation Result")

        #This is where the program is actually executed. It evaluates the tree using the enviroment
        result = ast.evaluate(env, verbose=verbose)

        # Only print final result if it's not a Print expression
        # If it's not a print statement, output the result
        if verbose and result is not None:
            print(result)
                
            

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

    # Join all lines into a single source string
    full_script = "\n".join(lines)

    # Parse and run it as one source
    run(full_script, env, verbose=False)

# Run file input from a .txt script
def run_file(filename: str):
    env = {}
    try:
        with open(filename, 'r') as file:
            source = file.read()
            run(source, env, verbose=False)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not filename.endswith(".luma"):
            print("Error: Only .luma files are allowed.")
            sys.exit(1)
        run_file(filename)

    else:
        run_prompt()  # Handle interactive one-line prompt
