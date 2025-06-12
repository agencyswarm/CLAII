# tests.py  (project root)

from functions.get_files_info import get_files_info

if __name__ == "__main__":
    print("\n--- List root of calculator ---")
    print(get_files_info("calculator", "."))
    print("\n--- List calculator/pkg ---")
    print(get_files_info("calculator", "pkg"))
    print("\n--- Attempt absolute /bin ---")
    print(get_files_info("calculator", "/bin"))
    print("\n--- Attempt outside with ../ ---")
    print(get_files_info("calculator", "../"))
