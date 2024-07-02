from utils.llamaindex import llamaindex_base
import streamlit as st
import base64

#function to display the PDF of a given file 
def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about the library!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        pdf_base = llamaindex_base()
        # index = pdf_base.index
        return pdf_base

pdf_base = load_data()

# query = st.text_input("What would you like to ask?", value= "List all the product numbers")
# # If the 'Submit' button is clicked
# if st.button("Submit"):
#     if not query.strip():
#         st.error(f"Please provide the search query.")
#     else:
#         st.write(query)
#         response = pdf_base.query(query)
#         st.success(response)
#         for node in response.source_nodes:
#             col1, col2 = st.columns([1,1])
#             with col1:
#                 st.write(node)
#             with col2:
#                 displayPDF(node.metadata['file_path'])


if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
    st.session_state.chat_engine = pdf_base.index.as_chat_engine(verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            st.write("reference:")
            for i, node in enumerate(response.source_nodes):
                st.write(f"{i+1}. {node.metadata['file_name']},      Score: {node.score}")
                displayPDF(node.metadata['file_path'])
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history