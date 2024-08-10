# Search text from image using Gemini

   SearchImage is a Streamlit-based application that allows users to search text from Image/PDF file using LLM.
   The App extracts information from uploaded Image/Pdf file and get the data focused by user.


## Features

- **Image/PDF Upload:** Users can upload Images or PDF files.
- **Text Extraction:** Extracts text from uploaded PDF files.Show the data focused by user.


## Getting Started

   **Note:** This project requires Python 3.10 or higher.

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/searchimage.git
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API Key:**
   - Obtain a Google API key and set it in the `.env` file.
   ```bash
   GOOGLE_API_KEY=your_api_key_here
    - Obtain a OpenAI API key and set it in the `.env` file.
   ```bash  
   OPENAI_API_KEY = "sk-
   ```

4. **install mongodb in docker:**
   install_stores.bat
   ```

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `Home.py`: Main application script.
- `.env`: file which will contain your environment variable.
- `requirements.txt`: Python packages required for working of the app.
- `README.md`: Project documentation.

## Dependencies

- PyMuPDF
- Streamlit
- google.generativeai
- dotenv
- unstructured
- unstructured.paddleocr


## Acknowledgments

- [Google Gemini](https://ai.google.com/): For providing the underlying language model.
- [Streamlit](https://streamlit.io/): For the user interface framework.
