import operator
from typing import Annotated, List, TypedDict, Union
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """The "Clipboard' passed between all nodes in the graph.
    """

    #Conversation history
    #'Operator.add' means: when a node returns a new message, Append it into this list
    # (don't override the old ones)

    messages: Annotated[List[BaseMessage],operator.add]

    #user details extracted from conversation
    user_email : str                
    user_requirements: str

    #Internal data (Hidden from user, used by tools)
    rag_content: str                   #Data found in pdf knowledge base
    project_price: int                 #calculated pricing.py

    #Artifacts
    pdf_path: str                      #path to generated PDF file

    #Control Flags
    next_step: str                     #Tells the graph where to go next

