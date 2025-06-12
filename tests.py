# tests.py
from functions.run_python import run_python_file

if __name__ == "__main__":
    print("\n–– run calculator/main.py ––")
    print(run_python_file("calculator", "main.py"))

    print("\n–– run calculator/tests.py ––")
    print(run_python_file("calculator", "tests.py"))

    print("\n–– attempt outside (../main.py) ––")
    print(run_python_file("calculator", "../main.py"))

    print("\n–– nonexistent file ––")
    print(run_python_file("calculator", "nonexistent.py"))
