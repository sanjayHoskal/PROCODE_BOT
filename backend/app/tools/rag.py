import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient

# Load env vars (We assume they are loaded in the main app, but good to be safe)
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "procode_knowledge"

def retrieve_similar_projects(query: str):
    """
    Searches the knowledge base for relevant past projects or policies.
    Useful when the user asks about pricing, similar work, or company rules.
    """
    print(f"RAG Tool called: Searching for '{query}'...")
    try:
        client=QdrantClient(url=QDRANT_URL,api_key=QDRANT_API_KEY)
        embeddings=FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        vector_store=Qdrant(client=client,collection_name=COLLECTION_NAME,
                            embeddings=embeddings)
        docs=vector_store.similarity_search(query,k=3)

        if not docs:
            return "No relavent information found in the knowledge base"
        
        result_text = "\n\n".join([f"--- Snippet from {d.metadata.get('source', 'Unknown')} ---\n{d.page_content}" for d in docs])
        return result_text
    
    except Exception as e:
        raise ValueError(f"Error searching for similar projects: {e}")
    


# Simple test block to run this file directly
if __name__ == "__main__":
    # You can test this by running: python -m backend.app.tools.rag
    # (Make sure .env is loaded before running directly)
    from dotenv import load_dotenv
    load_dotenv()
    print(retrieve_similar_projects("relieving letter"))
    