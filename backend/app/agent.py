import os
import sys
import re
from dotenv import load_dotenv

# --- 1. LOAD ENVIRONMENT VARIABLES FIRST ---
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(backend_dir)
env_path = os.path.join(root_dir, ".env")

print(f"🔌 Loading environment from: {env_path}")
load_dotenv(env_path)

# --- 2. IMPORTS ---
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.tools.rag import retrieve_similar_projects
from app.tools.pricing import calculate_project_price
from app.tools.pdf_gen import create_pdf
from app.tools.emailer import send_proposal_email

# Initialize Brain
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)

# --- SYSTEM PROMPT (STRICTER) ---
SYSTEM_PROMPT = """You are ProCode Bot, an expert AI consultant.

*** CRITICAL INSTRUCTION ***
You have the capability to read files. If the user uploads a PDF, the system will extract the text and present it to you inside <ATTACHED_PROJECT_DOCUMENT> tags.
- YOU MUST READ THIS CONTENT.
- Do NOT say "I cannot read files".
- Treat the content inside those tags as the definitive project architecture and requirements.

YOUR PROCESS (FOLLOW STRICTLY):
1. GATHER INFO: Ask about features, user traffic, and platform (Web/Mobile).
2. RESEARCH: If asked about past work/pricing policies, use [LOOKUP: query].
3. ESTIMATE: Once you understand the scope, estimate hours (e.g., Simple=50h, Mid=100h, Complex=300h) and resource level.
4. CALCULATE: Use the tool [CALCULATE: hours, level] to get the exact price.
5. PROPOSE: Present the calculated price to the user.
6. CLOSE: ONLY IF the user accepts the price AND provides an email, use [GENERATE_PROPOSAL].

RULES:
- DO NOT use [CALCULATE] until you have asked about features.
- DO NOT use [GENERATE_PROPOSAL] if you haven't successfully calculated a price yet.
- If a tool fails, tell the user you are having trouble and ask for details again.
"""

# --- NODE 1: REASONING ---
def chatbot_node(state: AgentState):
    messages = state['messages']
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    instructions = """
    TOOLS AVAILABLE:
    - [LOOKUP: search_term] -> Search past projects.
    - [CALCULATE: hours, level] -> e.g., [CALCULATE: 50, junior] or [CALCULATE: 100, senior].
    - [GENERATE_PROPOSAL] -> Generate PDF and email it.
    """
    
    response = llm.invoke(messages + [SystemMessage(content=instructions)])
    
    next_step = "wait_for_user"
    content = response.content
    
    if "[LOOKUP:" in content:
        next_step = "run_rag"
    elif "[CALCULATE:" in content:
        next_step = "run_pricing"
    elif "[GENERATE_PROPOSAL]" in content:
        next_step = "draft_proposal"
        
    return {
        "messages": [response],
        "next_step": next_step
    }

# --- NODE 2: ACTION (ROBUST PARSING) ---
def tool_node(state: AgentState):
    last_message = state['messages'][-1].content
    
    if "run_rag" in state['next_step']:
        try:
            query = last_message.split("[LOOKUP:")[1].split("]")[0].strip()
            data = retrieve_similar_projects(query)
            return {
                "messages": [AIMessage(content=f"RAG RESULT: {data}")], 
                "rag_context": data,
                "next_step": "chatbot"
            }
        except Exception as e:
             return {"messages": [AIMessage(content=f"System Error in RAG: {e}")], "next_step": "chatbot"}

    elif "run_pricing" in state['next_step']:
        try:
            # ROBUST PARSING: Extract numbers using Regex
            params_text = last_message.split("[CALCULATE:")[1].split("]")[0]
            
            # Find the first number in the string (hours)
            import re
            hours_match = re.search(r'\d+', params_text)
            hours = int(hours_match.group()) if hours_match else 50 # Default to 50 if parsing fails
            
            # Find level
            level = "mid"
            if "senior" in params_text.lower(): level = "senior"
            elif "junior" in params_text.lower(): level = "junior"
            elif "expert" in params_text.lower(): level = "expert"

            price = calculate_project_price(hours, level)
            
            result_msg = f"REQUIREMENT: Calculated Cost: ₹{price:,} (for {hours} hours @ {level} level)."
            return {
                "messages": [AIMessage(content=result_msg)],
                "project_price": price,
                "next_step": "chatbot"
            }
        except Exception as e:
            return {"messages": [AIMessage(content=f"Error calculating price. Please ensure you provided hours and level. Details: {e}")], "next_step": "chatbot"}

    return {"next_step": "chatbot"}

# --- NODE 3: DRAFTING ---
# ... (Imports remain the same) ...

# --- NODE 3: DRAFTING (Updated) ---
def proposal_node(state: AgentState):
    # Fallbacks
    price = state.get("project_price", 0) # Default to integer 0
    reqs = "Client Project"
    if len(state['messages']) > 2:
        reqs = state['messages'][-2].content

    # Extract email
    recipient = "sanjuhoskal@gmail.com" 
    for m in reversed(state['messages']):
        if "@" in m.content and "ProCode" not in m.content:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', m.content)
            if email_match:
                recipient = email_match.group(0)
            break

    # --- HTML TEMPLATE WITH LOGO AND FOOTER ---
    # Note: price:, formats number with commas (e.g. 40,000)
    prompt = f"""
    Write a clean HTML proposal.
    - Requirements Summary: {reqs}
    - Total Price: INR {price:,}
    - Notes: {state.get('rag_context', 'Standard terms apply.')}
    
    REQUIRED HTML STRUCTURE (Do strictly):
    
    <div class="header-container">
        <div class="company-name">ProCode Bot</div>
        <img src="file:///D:/ML%20Projects/Procode_Prod_Projects/procode_bot/backend/knowledge_base/procode_image.png" class="logo" alt="Company Logo">
    </div>

    <h1>Project Proposal</h1>
    <p>Dear Customer,</p>
    
    [...Insert specific project details, timeline, and scope here based on requirements...]

    <h2>Commercials</h2>
    <div class="price-box">
        Total Estimated Cost: ₹{price:,}
    </div>

    <div class="footer">
        <b>ProCodeHub Pvt Ltd</b><br>
        123 Kalikaparameshwari complex,Durgigudi,Shivamogga, Karnataka - 577201<br>
        Contact: +91 98765 43210 | Email:procodehub@gmail.com
    </div>
    """
    
    # Run LLM
    html_response = llm.invoke([HumanMessage(content=prompt)])
    html_content = html_response.content
    
    # Strip Markdown if present
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0]

    # Generate PDF
    pdf_path = create_pdf(html_content)
    
    # Send Email
    email_status = send_proposal_email(pdf_path, recipient)
    
    final_msg = f"Proposal generated for ₹{price:,} and sent to {recipient}!"
    
    return {
        "messages": [AIMessage(content=final_msg)],
        "pdf_path": pdf_path,
        "next_step": "end"
    }

# --- GRAPH SETUP ---
def route_step(state: AgentState):
    step = state.get("next_step")
    if step in ["run_rag", "run_pricing"]: return "tools"
    elif step == "draft_proposal": return "proposal"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", tool_node)
workflow.add_node("proposal", proposal_node)

workflow.set_entry_point("chatbot")
workflow.add_conditional_edges("chatbot", route_step, {"tools": "tools", "proposal": "proposal", END: END})
workflow.add_edge("tools", "chatbot")
workflow.add_edge("proposal", END)

app = workflow.compile()

if __name__ == "__main__":
    print("🤖 ProCode Bot is online! (Type 'quit' to exit)")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]: break
            result = app.invoke({"messages": [HumanMessage(content=user_input)]})
            print(f"Bot: {result['messages'][-1].content}\n")
        except Exception as e:
            print(f"Error: {e}")