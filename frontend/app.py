import streamlit as st
import requests
import os
import uuid
import base64

# CONFIGURATION
API_URL = "http://127.0.0.1:8000/chat"
st.set_page_config(page_title="ProCode Bot", page_icon="🤖", layout="wide")

# SESSION STATE INITIALIZATION
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

with st.sidebar:
    st.header(" Projects Controls")
    st.markdown(" Attachments")

        #5.1 UI Layout: File Uploader
        # Note: Currently, the backend focuses on text, but this UI element is ready
        # for when we add image analytics logic later

    uploaded_file = st.file_uploader("Upload Project Screenshot/Docs", type=["png", "jpg", "pdf"])
    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' attached (Visual only for now).")

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# --- MAIN CHAT INTERFACE ---

st.title("ProCode Project Consultant")
st.markdown("Describe your projec idea, and I'll help you estimate and propose a solution")

#Display chat history
# [NEW CODE]
# 1. Display Chat History
# We use 'enumerate' to get a unique index 'i' for every message
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If a past message had a PDF, show the button again
        if message.get("pdf_path"):
             if os.path.exists(message["pdf_path"]):
                 with open(message["pdf_path"], "rb") as f:
                    st.download_button(
                        label="Download Proposal PDF",
                        data=f,
                        file_name="ProCode_Proposal.pdf",
                        mime="application/pdf",
                        key=f"history_btn_{i}" # <--- FIX: Unique Key based on Index
                    )
             else:
                 st.warning("PDF file no longer exists locally.")

#Handle user input
if prompt := st.chat_input("Type your requirements here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    #Api integration
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # NEW: Handle file upload
                file_payload =  None
                file_type = None

                # Check if a file sits in sidebar uploader
                if uploaded_file is not None:
                    uploaded_file.seek(0)
                    bytes_data = uploaded_file.getvalue()
                    file_payload = base64.b64encode(bytes_data).decode('utf-8')
                    file_type = uploaded_file.type

                payload = {
                    "message": prompt,
                    "thread_id": st.session_state.thread_id,
                    "file_data": file_payload,
                    "file_type": file_type
                }
                #send POST request to API
                response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    bot_text = data.get("response", "No response received.")
                    pdf_path = data.get("pdf_path")  #Extract PDF path if exists
                    st.markdown(bot_text)

                    #Display results and download button
                    if pdf_path and os.path.exists(pdf_path):
                        st.success("Proposal generated successfully!")
                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="Download Proposal PDF",
                                data=f,
                                file_name="Procode_Proposal.pdf",
                                mime='application/pdf',
                        )
                        #add to history with the pdf path
                        st.session_state.messages.append({"role": "assistant", "content": bot_text, "pdf_path": pdf_path})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": bot_text})
                else:
                    st.error(f"API Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the server.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
        
