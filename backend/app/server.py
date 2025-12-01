import os
import base64
import io
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from pypdf import PdfReader
from typing import Optional

# Import the workflow from your agent
# we use relative import since this file is inside the 'app' package
from app.agent import workflow

# Initialize FastAPI
app=FastAPI(title="ProCode Bot API", version="1.1")

# add CORS (Allows your streamlit frontend to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Memory (So the bot remembers context like "Price is $40k")
memory = MemorySaver()
# we compile the graph HERE with checkpointer
agent_app = workflow.compile(checkpointer=memory)

# Vision and PDF helper
def process_file(file_data: str, file_type: str) -> str:
    try:
        decoded_file = base64.b64decode(file_data)

        # 1. Handle PDF (Architecture/Requirements Docs)
        if "pdf" in file_type.lower():
            pdf_file = io.BytesIO(decoded_file)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""


            # --- LOGIC FIX: Detect Image-Only PDF ---
            # If extracted text is too short, it's likely a scan/screenshot
            if len(text.strip()) < 50:
                return """
                \n[SYSTEM WARNING: The user uploaded a PDF, but it appears to be an image-only file (scanned or screenshot) because no text could be extracted.
                INSTRUCTION: Tell the user: "I noticed you uploaded a PDF that seems to be a screenshot or scanned image. I cannot read text from image-based PDFs. Please upload the original Image file (JPG/PNG) directly so my Vision system can analyze it for you."]
                """
            
            # Formatting: Wrap in tags so the LLM knows what this is
            # We increase the limit to 10k chars to capture full architecture details
            return f"""
            \n<ATTACHED_PROJECT_DOCUMENT>
            {text[:10000]}
            </ATTACHED_PROJECT_DOCUMENT>
            \n[SYSTEM NOTE: The text above is the content of the PDF uploaded by the user. Use this as the primary source for requirements.]
            """

        
        # Handle images (Using Groq vision)
        elif any(x in file_type.lower() for x in ["png","jpg","jpeg"]):
            print(" Analysing Image...")
            vision_llm = ChatGroq(
                api_key = os.getenv("GROQ_API_KEY"),
                model_name = "meta-llama/llama-4-scout-17b-16e-instruct",     #vision model
                temperature=0.1
            )

            # Create a vision message
            msg = HumanMessage(content=[
                {"type":"text", "text": "Describe this UI/Screenshot in technical details for a developer."},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{file_data}"}}
                ])
            response = vision_llm.invoke([msg])
            return f"\n[IMAGE ANALYSIS]: The user uploaded a screenshot. Description:\n{response.content}"
        
        return ""  # If not a supported file type
    except Exception as e:
        return f"\n[SYSTEM ERROR]: Could not process file. Error : {e}"
    


# Define request model
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default_user"   #unique id for each conversation
    file_data: Optional[str] = None              #base64 encoded string of file data
    file_type: Optional[str] = None             #mime type of the file

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
            # Process file if provided
        file_context = ""
        if request.file_data and request.file_type:
            file_context = process_file(request.file_data, request.file_type)
 
        # Combine user messages + file context
            full_input = request.message + file_context

        # Define config with thread_id to maintain state
        config = {"configurable": {"thread_id": request.thread_id}}

        # Prepare the input
        #input_message = HumanMessage(content=request.message)

        # Run the agent and get response
        result = agent_app.invoke(
            {"messages": [HumanMessage(content=full_input)]}, config=config
        )

        # extract the bot's last response
        last_message = result["messages"][-1].content

        # Check for PDF in the state
        pdf_path = result.get("pdf_path", None)

        # Return structured response
        return {
            "response": last_message,
            "pdf_path": pdf_path               # will be None unless a PDF was generated
        }
    
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# 6. Run server (Optional: for debugging purposes only)
if __name__ == "__main__":
    print(" Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)