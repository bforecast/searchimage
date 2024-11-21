import streamlit as st
from utils.llamaindex import iPdfRAG

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        pdf_base = iPdfRAG()
        return pdf_base