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
        scanner = Scanner.Scanner(source)
        tokens = scanner.scan_tokens()
        for token in tokens:
            print(token)

        print("\nAST Construction")
        ast = AST(tokens)
        print(ast.tree)

        print("\nEvaluation Result")
        result = ast.evaluate()
        print(f"Final Result: {result}")

    except SyntaxError as e:
        error(1, f"Syntax Error: {str(e)}")
    except TypeError as e:
        error(1, f"Type Error: {str(e)}")
    except ZeroDivisionError as e:
        error(1, f"Math Error: {str(e)}")
    except OverflowError as e:
        error(1, f"Overflow Error: {str(e)}")
    except Exception as e:
        error(1, f"Unexpected Error: {str(e)}")

def run_prompt() -> None:
    print("\nWelcome!!!")
    print("Type expressions to evaluate, or type 'exit()' to quit.\n")

    while True:
        print("\n>>> ", end="")
        try:
            line = input().strip()
            if not line:
                continue  # Ignore empty input
            if line.lower() == "exit()":
                print("\nExiting interpreter. Goodbye!\n")
                break
            run(line)
        except KeyboardInterrupt:
            print("\n\nExiting interpreter. Goodbye!\n")
            break

if __name__ == "__main__":
    run_prompt()
