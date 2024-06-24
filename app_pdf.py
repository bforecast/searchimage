import streamlit as st
# import pymupdf  # import the bindings
import fitz  # PyMuPDF library
from PIL import Image

def main():
    st.title("文件上传与显示")

    uploaded_file = st.file_uploader("请选择文件", type=["jpg", "png", "pdf"])

    if uploaded_file is not None:
        # 获取文件类型
        file_type = uploaded_file.type

        # 显示图片
        if file_type in ["image/jpeg", "image/png"]:
            st.image(uploaded_file)

        # 显示PDF文件并提取第一页图片
        elif file_type == "application/pdf":
            # 打开PDF文件
            doc = fitz.open(uploaded_file)
            for page in doc:  # iterate through the pages
                pixmap = page.get_pixmap()  # render page to an image
                st.write(page)
                st.image(pixmap.tobytes()) 
            doc.close()

if __name__ == "__main__":
    main()