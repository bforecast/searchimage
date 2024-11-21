import streamlit as st
import fitz  # Install with: pip install pymupdf
import io
from PIL import Image
from utils.llamaindex import iPdfRAG
from utils.global_functions import load_data

def displayImageinPDF(node):
    img_byte = imageFromPdf(
                            node.metadata['file_path'], 
                            node.metadata['page_number'], 
                            node.metadata['coordinates'],
                            node.metadata['page_width'],
                            node.metadata['page_height']
                            )
    st.image(img_byte, caption=f"{node.metadata['filename']}, Page {node.metadata['page_number']}")

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

pdf_base = load_data()
##Query-Search Mode
col1,col2 = st.columns([9, 1])
with col1:
    query = st.text_input("What would you like to ask?",value="I want to develop a product in washing and lye peeling of fruits. provide the composition ingredients and similiar products name")
with col2:
    top_k = st.slider("Top-K", value=3, max_value=100)
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

##Chat-Bot Mode
# if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
#     st.session_state.chat_engine = pdf_base.vector_index.as_chat_engine(verbose=False, )

# if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})

# for message in st.session_state.messages: # Display the prior chat messages
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# # If last message is not from assistant, generate a new response
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             response = st.session_state.chat_engine.chat(prompt)
#             st.write(response.response)
#             st.write("reference:")
#             for idx, node in enumerate(response.source_nodes):
#                 if "filename" in node.metadata:
#                     col0, col1, col2 = st.columns([0.1,2,1])
#                     with col0:
#                         st.write(f"{idx+1}." )
#                     with col1:
#                         if all(tag in node.get_content() for tag in ['<table>', '<tr>', '<td>']):
#                             st.html(node.get_content())
#                         else:
#                             st.write(node.get_content())
#                         st.write(f"Score: {node.score}")
#                     with col2:
#                         displayImageinPDF(node)
#             message = {"role": "assistant", "content": response.response}
#             st.session_state.messages.append(message) # Add response to message history