import os
import asyncio
from dotenv import load_dotenv
from llama_parse import LlamaParse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient, models
from langchain_core.documents import Document

# Load environment variables
# --- FIX: Dynamic Path Resolution ---
# 1. Get the path of the current script (backend/scripts/ingest.py)
current_script = os.path.abspath(__file__)

# 2. Go up two levels to find the project root (procode_bot/)
backend_dir = os.path.dirname(os.path.dirname(current_script))
project_root = os.path.dirname(backend_dir)

# 3. Define the path to .env
env_path = os.path.join(project_root, ".env")

# 4. Load it and print status
print(f" Loading .env from: {env_path}")
if load_dotenv(env_path):
    print(" .env loaded successfully.")
else:
    print(" Failed to load .env. Check if the file exists at the path above.")

# Verify Keys specifically
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Redefine logic for data directory relative to backend
DATA_DIR = os.path.join(backend_dir, "knowledge_base")
COLLECTION_NAME = "procode_knowledge"

async def ingest_data():
    print(f" Loading documents from {DATA_DIR}...")

    # 1. Initialize Parser
    parser = LlamaParse(
        api_key=LLAMA_CLOUD_API_KEY,
        result_type="markdown",
        verbose=True,
    )

    # 2. Find Files
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
    if not files:
        print(" No PDF files found.")
        return

    documents = []
    
    # 3. Parse Files
    for file in files:
        file_path = os.path.join(DATA_DIR, file)
        print(f" Parsing {file}...")
        try:
            parsed = await parser.aload_data(file_path) # efficient async loading
            text = "\n".join([doc.text for doc in parsed])
            documents.append(Document(page_content=text, metadata={"source": file}))
            print(f" Successfully parsed {file}")
        except Exception as e:
            print(f" Error reading {file}: {e}")

    if not documents:
        print("No documents to process.")
        return

    # 4. Split Text
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    final_docs = splitter.split_documents(documents)
    print(f" Total text chunks created: {len(final_docs)}")

    # 5. Initialize Embeddings & Client
    # BAAI/bge-small-en-v1.5 produces vectors of size 384
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5") 
    
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # 6. Check/Create Collection Explicitly (The Fix)
    # We do this manually to avoid the 'init_from' error in LangChain
    if not client.collection_exists(COLLECTION_NAME):
        print(f" Collection '{COLLECTION_NAME}' does not exist. Creating it...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384,  # Matches FastEmbed BGE-small
                distance=models.Distance.COSINE
            )
        )
        print(" Collection created.")
    else:
        print(f" Collection '{COLLECTION_NAME}' already exists. Appending data...")

    # 7. Upload to Qdrant
    try:
        # We use the instance wrapper instead of class method 'from_documents'
        vector_store = Qdrant(
            client=client,
            collection_name=COLLECTION_NAME,
            embeddings=embeddings,
        )
        
        vector_store.add_documents(final_docs)
        print(f" SUCCESS: Uploaded {len(final_docs)} vectors to Qdrant!")
    except Exception as e:
        print(f" ERROR uploading to Qdrant: {e}")

# -----------------------
# RUN THE SCRIPT
# -----------------------
if __name__ == "__main__":
    if not QDRANT_API_KEY:
        print(" Missing QDRANT_API_KEY in .env")
    elif not LLAMA_CLOUD_API_KEY:
        print(" Missing LLAMA_CLOUD_API_KEY in .env")
    else:
        asyncio.run(ingest_data())