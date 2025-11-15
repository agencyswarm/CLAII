from functions.run_python import run_python_file

if __name__ == "__main__":
    # 1. main.py – usage instructions (no args)
    print(run_python_file("calculator", "main.py"))

    # 2. main.py with an expression – should run the calculator
    print(run_python_file("calculator", "main.py", ["3 + 5"]))

    # 3. run the calculator unit tests
    print(run_python_file("calculator", "tests.py"))

    # 4. outside working directory – should error
    print(run_python_file("calculator", "../main.py"))

    # 5. nonexistent file – should error
    print(run_python_file("calculator", "nonexistent.py"))

    # 6. not a Python file – should error
    print(run_python_file("calculator", "lorem.txt"))
