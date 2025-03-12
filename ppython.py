import sys
from Token import Token
from AST import AST
import Scanner

def error(line: int, message: str) -> None:
    print(f"\nError on line {line}: {message}\n")

def run(source: str) -> None:
    if not source.strip():
        print("\nError: Empty input. Please enter a valid expression.\n")
        return

    try:
        print("\nTokenization Process")
        # Create a Scanner object
        scanner = Scanner.Scanner(source)

        # Call scan_tokens() to break the input into tokens
        tokens = scanner.scan_tokens()

        # Print the tokenized output to validate it is working
        for token in tokens:
            print(token)

        print("\nAST Construction")
        # Pass the tokens to AST, which constructs an Abstract Syntax Tree
        ast = AST(tokens)

        # Print the AST for debugging
        print(ast.tree)

        print("\nEvaluation Result")
        # Evaluate the AST and print the final result
        result = ast.evaluate()
        print(f"Final Result: {result}")
    
    # Handle different error types dynamically
    except SyntaxError as e:
        error(scanner._line, f"Syntax Error: {str(e)}")  # ✅ Uses scanner’s current line number
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
    print("Type expressions to evaluate, or type 'exit()' to quit.\n")
   
    while True:
        print("\n>>> ", end="")
        try:
            line = input().strip()
            if not line:
                continue  
            # If the user types exit(), terminate the program
            if line.strip().lower() == "exit()":  # ✅ Strips spaces and handles case sensitivity
                print("\nExiting interpreter. Goodbye!\n")
                break
            run(line)
        # If the user presses Ctrl+C, exit the program gracefully
        except KeyboardInterrupt:
            print("\n\nExiting interpreter. Goodbye!\n")
            break

if __name__ == "__main__":
    run_prompt()
