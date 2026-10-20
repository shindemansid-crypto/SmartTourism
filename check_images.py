import os
import hashlib
from collections import defaultdict

IMAGE_FOLDER = "static/images"

groups = defaultdict(list)

for filename in os.listdir(IMAGE_FOLDER):
    if filename.lower().startswith("dest-") and filename.lower().endswith((".jpg", ".jpeg", ".png")):

        path = os.path.join(IMAGE_FOLDER, filename)

        with open(path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        groups[file_hash].append(filename)

print("\nDESTINATION IMAGE CHECK\n")

total = 0

for files in groups.values():
    total += len(files)

    if len(files) > 1:
        print("DUPLICATE:")
        for file in files:
            print("   ", file)
        print()

print("Total destination images:", total)

unique = len(groups)

print("Unique photographs:", unique)
print("Duplicate copies:", total - unique)