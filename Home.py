from utils.llamaindex import llamaindex_base, iPdfRAG
import streamlit as st
import base64

#function to display the PDF of a given file 
def displayPDF(file:str):
    # Opening file from file path. this is used to open the file from a website rather than local
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def displayImageinPDF(node):
    img_byte = imageFromPdf(
                            node.metadata['file_path'], 
                            node.metadata['page_number'], 
                            node.metadata['coordinates'],
                            node.metadata['page_width'],
                            node.metadata['page_height']
                            )
    st.image(img_byte, caption=f"{node.metadata['filename']}, Page {node.metadata['page_number']}")
    

import fitz  # Install with: pip install pymupdf
import io
from PIL import Image, ImageDraw

def imageFromPdf(pdf_path, page_number, coord_string, page_width, page_height):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    # Get the specified page
    page = pdf_document[page_number - 1]  # Page numbers start at 0
    
    # Get page dimensions
    page_rect = page.rect
    
    # Calculate scaling factors
    x_scale = page_rect.width / page_width
    y_scale = page_rect.height / page_height
    scale = min(x_scale, y_scale)
    
    # Create a rectangle from the coordinates
    coordinates = eval(coord_string)
    # Scale coordinates
    scaled_coords = [(x * scale, y * scale) for x, y in coordinates]
    x0, y0 = scaled_coords[0]
    x1, y1 = scaled_coords[2]
    rect = fitz.Rect(x0, y0, x1, y1)
    # Draw the rectangle on the page
    page.draw_rect(rect, color=(1, 0, 0), width=2)
    
    # Render page to an image
    mat = fitz.Matrix(300 / 72, 300 / 72)  # Increase resolution to 300 DPI
    pix = page.get_pixmap(matrix=mat)
    # pix = page.get_pixmap()
    
    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

st.set_page_config(page_title="Chat with the Streamlit docs, powered by LlamaIndex", page_icon="🦙", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about the library!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        # pdf_base = llamaindex_base()
        # index = pdf_base.index
        pdf_base = iPdfRAG()
        return pdf_base

pdf_base = load_data()
col1,col2 = st.columns([9, 1])
with col1:
    query = st.text_input("What would you like to ask?",value="I want to develop a product in washing and lye peeling of fruits. provide the composition ingredients and similiar products name")
with col2:
    top_k = st.slider("Top-K", value=3, max_value=100)
# If the 'Submit' button is clicked
if st.button("Search"):
    if not query.strip():
        st.error(f"Please provide the search query.")
    else:
        st.write(f"Question: {query}")
        st.write("Answer:")
        response = pdf_base.vector_query(query, top_k)
        st.success(response)
        if len(response.source_nodes) > 0:
            st.write("For reference:")
            for idx, node in enumerate(response.source_nodes):
                if "filename" in node.metadata:
                    col0, col1, col2 = st.columns([0.1,2,1])
                    with col0:
                        st.write(f"{idx+1}." )
                    with col1:
                        if all(tag in node.get_content() for tag in ['<table>', '<tr>', '<td>']):
                            st.html(node.get_content())
                        else:
                            st.write(node.get_content())
                        st.write(f"Score: {node.score}")
                    with col2:
                        # displayPDF(node.metadata['file_path'])
                        # displayPDF(source_node.metadata['filename'])
                        displayImageinPDF(node)
                        



if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
    st.session_state.chat_engine = pdf_base.vector_index.as_chat_engine(verbose=True)

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
            for idx, node in enumerate(response.source_nodes):
                if "filename" in node.metadata:
                    col0, col1, col2 = st.columns([0.1,2,1])
                    with col0:
                        st.write(f"{idx+1}." )
                    with col1:
                        if all(tag in node.get_content() for tag in ['<table>', '<tr>', '<td>']):
                            st.html(node.get_content())
                        else:
                            st.write(node.get_content())
                        st.write(f"Score: {node.score}")
                    with col2:
                        # displayPDF(node.metadata['file_path'])
                        # displayPDF(source_node.metadata['filename'])
                        displayImageinPDF(node)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history

# st.write("should use CP-2000W agent -> vector tool")
# query_string = "Tell me about the address of CP-2000W"
# st.write(f"Question: {query_string}")
# response = pdf_base.vector_query(query_string)
# st.success(response)
# st.write("For reference:")
# for idx, source_node in enumerate(response.source_nodes):
#     st.write(f"{idx+1}. {source_node.get_content()}")

# st.write("should use CP-2000W agent -> summary tool")
# query_string = "Give me a summary on all the positive aspects of CP-2000W"
# st.write(f"Question: {query_string}")
# response = pdf_base.vector_query(query_string)
# st.success(response)
# st.write("For reference:")
# for idx, source_node in enumerate(response.source_nodes):
#     st.write(f"{idx+1}. {source_node.get_content()}")
