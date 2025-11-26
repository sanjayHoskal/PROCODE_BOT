import os
from qdrant_client import QdrantClient

print("\n--- 1. CHECKING LIBRARY METHODS ---")
# We check the actual list of functions available inside QdrantClient
available_methods = dir(QdrantClient)

if 'query_points' in available_methods:
    print("✅ Your installed QdrantClient HAS 'query_points' (New API).")
else:
    print("❌ Your installed QdrantClient DOES NOT have 'query_points'.")

if 'search' in available_methods:
    print("✅ Your installed QdrantClient HAS 'search' (Old API).")
else:
    print("❌ Your installed QdrantClient DOES NOT have 'search'.")

print("\n--- 2. CHECKING YOUR CODE (rag.py) ---")
file_path = os.path.join("app", "tools", "rag.py")

try:
    with open(file_path, "r") as f:
        content = f.read()
        
    print(f"Reading file: {os.path.abspath(file_path)}")
    
    if "client.query_points" in content:
        print("✅ CODE CHECK: Your file correctly calls 'client.query_points'.")
    elif "client.search" in content:
        print("❌ CODE CHECK: Your file still calls 'client.search'. YOU NEED TO SAVE THE FILE.")
    else:
        print("⚠️ CODE CHECK: Could not find 'search' OR 'query_points' in the file.")
        
except FileNotFoundError:
    print(f"❌ Error: Could not find {file_path}")