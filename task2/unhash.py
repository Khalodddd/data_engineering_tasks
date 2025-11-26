import hashlib
from pathlib import Path

def sha3_256_file(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha3_256(f.read()).hexdigest()

def hash_sort_key(h):
    prod = 1
    for char in h:
        prod *= (int(char, 16) + 1)
    return prod

# Path to your unzipped folder
folder = r"C:\Users\Blu-Ray\Desktop\vu\Intern\data_engineering_tasks\task2\task2"

# Your email (must be lowercase)
email = "khaledsoliman1599@gmail.com"

# Step 1: compute all file hashes
hashes = [
    sha3_256_file(file)
    for file in Path(folder).iterdir()
    if file.is_file()
]

print("Number of files found:", len(hashes))
assert len(hashes) == 256, f"ERROR: {len(hashes)} files found, expected exactly 256!"

# Step 2: sort hashes using product-of-hex-digits+1
hashes_sorted = sorted(hashes, key=hash_sort_key)

# Step 3: concatenate all hashes (no separators), then add email
final_string = "".join(hashes_sorted) + email

# Step 4: final SHA3-256
final_hash = hashlib.sha3_256(final_string.encode("utf-8")).hexdigest()

print("\nFINAL HASH TO SUBMIT:")
print(final_hash)
