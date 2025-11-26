import os
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient

# Load env vars
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "procode_knowledge"

def retrieve_similar_projects(query:str):
    """
    Searches the knowledge base for relevant past projects or policies.
    """
    print(f"RAG Tool Called: Searching for '{query}'...")
    try:
        #1. Connect to qdrant
        client=QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

        #2. Initialise embeddings model
        embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

        #3. Create Query vector
        query_vector = embeddings.embed_query(query)

        #4. Perform Search (Using new query_points API)
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=3,
        ).points

        if not search_result:
            return f"No results found for {query}"
        
        # 5. Format the Output
        results = []
        for hit in search_result:
            #Safely get content from payload
            content = hit.payload.get("page_content","No content available")
            source=hit.payload.get("metadata",{}).get("source","Unknown")
            results.append(f"--- Snippet from {source} ---\n{content}")

        return "\n\n".join(results)
    except Exception as e:
        print(f"RAG Error: {e}")
        return f"Error retrieving similar projects: {str(e)}"
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    #Fix path to load .env correctly for testing
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
    print(retrieve_similar_projects('Project pricing'))