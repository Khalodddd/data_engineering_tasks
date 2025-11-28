# debug_yaml.py
from pathlib import Path

for ds in ["DATA1", "DATA2", "DATA3"]:
    print(f"\n===== {ds} =====")
    f = Path("data") / ds / "books.yaml"
    if f.exists():
        with open(f, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for i, line in enumerate(lines[10:35], start=11):
                print(f"{i:03}: {line.rstrip()}")
    else:
        print("books.yaml not found!")
