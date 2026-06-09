import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import io
import os
from dotenv import load_dotenv
import re
from fpdf import FPDF
import markdown

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("GEMINI_API_KEY not found in environment variables. Please check your .env file.")

def extract_text_from_pdf(file):
    """Extracts text from an uploaded PDF file."""
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF: {e}"

def extract_text_from_url(url):
    """Extracts main content from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        # Get text
        text = soup.get_text(separator=' ')
        
        # Basic cleanup: remove extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error fetching URL: {e}"

def apply_bionic_reading(text):
    """Applies a simple Bionic Reading effect by bolding the first half of words."""
    def bold_word(match):
        word = match.group(0)
        if len(word) <= 1:
            return word
        mid = (len(word) + 1) // 2
        return f"**{word[:mid]}**{word[mid:]}"
    
    # Match words (including those with apostrophes)
    return re.sub(r'\b\w+\b', bold_word, text)

def process_with_ai(text, target_language, model_name, adhd_friendly=True):
    """Uses Gemini to process text into an ADHD-friendly format and translate it."""
    if not api_key:
        return "API Key missing. Cannot process."
    
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are an expert in making text ADHD-friendly and a professional translator.
        
        TASK:
        1. Rewrite the following text to be ADHD-friendly:
           - Use simple language.
           - Break long sentences into shorter ones.
           - Use bullet points for key takeaways.
           - Use bold text for emphasis on important terms.
           - Keep the original meaning intact but make it highly scannable.
        2. Translate the resulting ADHD-friendly text into {target_language}.
        
        TEXT TO PROCESS:
        {text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during AI processing: {e}. Try selecting a different model (e.g., gemini-pro) in the sidebar."

def generate_pdf(markdown_text):
    """Generates a PDF from markdown text with Unicode and Bold support."""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Paths to Microsoft YaHei (Regular and Bold) for Unicode support
        font_path = "C:\\Windows\\Fonts\\msyh.ttc"
        font_bold_path = "C:\\Windows\\Fonts\\msyhbd.ttc"
        
        # Load fonts if they exist to support bolding and international characters
        if os.path.exists(font_path):
            pdf.add_font("UnicodeFont", "", font_path)
            if os.path.exists(font_bold_path):
                # Loading the bold version allows <strong> and <b> tags to work in write_html
                pdf.add_font("UnicodeFont", "B", font_bold_path)
            pdf.set_font("UnicodeFont", size=12)
        else:
            # Fallback to standard Helvetica if Windows fonts aren't found
            pdf.set_font("helvetica", size=12)
        
        # Convert markdown to HTML (handles bolding, lists, headers)
        html_content = markdown.markdown(markdown_text)
        
        # Primary path: Render HTML to PDF
        try:
            pdf.write_html(html_content)
        except Exception:
            # Fallback: Strip ALL markdown symbols and use multi_cell to ensure no raw markdown is seen
            # This regex removes #, *, _, `, and [links](url) formatting
            clean_text = re.sub(r'[*_#~`]|\[.*?\]\(.*?\)', '', markdown_text)
            pdf.multi_cell(0, 10, txt=clean_text)
            
        return bytes(pdf.output())
    except Exception as e:
        # Ultimate safety fallback
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        # Final attempt to at least provide the text without crashing
        clean_text = re.sub(r'[*_#~`]', '', markdown_text)
        # Encode to latin-1 to avoid fpdf crashes on unicode in this extreme fallback
        safe_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=safe_text)
        return bytes(pdf.output())

def get_available_models():
    """Fetches available models that support generateContent."""
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Remove 'models/' prefix for cleaner display if it exists
                name = m.name.replace('models/', '')
                models.append(name)
        return models
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"] # Fallback

# --- Streamlit UI ---

st.set_page_config(page_title="ADHD Reader & Translator", page_icon="📖")

st.title("📖 ADHD-Friendly Reader")
st.markdown("Transform any content into an ADHD-friendly format with AI-powered simplification and translation.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    input_type = st.radio("Select Input Source", ["Text", "URL", "PDF"])
    target_lang = st.selectbox("Target Language", ["English", "Chinese", "Spanish", "French", "German"])
    
    # Dynamically fetch models
    available_models = get_available_models()
    default_index = 0
    if "gemini-1.5-flash" in available_models:
        default_index = available_models.index("gemini-1.5-flash")
    elif "gemini-pro" in available_models:
        default_index = available_models.index("gemini-pro")
        
    model_choice = st.selectbox("AI Model", available_models, index=default_index)
    bionic_enabled = st.checkbox("Enable Bionic Reading (Bold first half of words)", value=True)
    
    st.divider()
    st.info("The AI will simplify the text and then translate it into your chosen language.")

# Main Area
raw_text = ""

# Initialize session state for processed text
if "processed_text" not in st.session_state:
    st.session_state.processed_text = ""

if input_type == "Text":
    raw_text = st.text_area("Paste your text here:", height=300)
elif input_type == "URL":
    url = st.text_input("Enter URL:")
    if url:
        with st.spinner("Extracting content from URL..."):
            raw_text = extract_text_from_url(url)
elif input_type == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            raw_text = extract_text_from_pdf(uploaded_file)

if raw_text:
    if st.button("Process Content"):
        with st.spinner(f"AI ({model_choice}) is working its magic..."):
            processed_text = process_with_ai(raw_text, target_lang, model_choice)
            
            if bionic_enabled:
                processed_text = apply_bionic_reading(processed_text)
            
            st.session_state.processed_text = processed_text

if st.session_state.processed_text:
    st.divider()
    st.subheader("Processed Content")
    st.markdown(st.session_state.processed_text)

    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        # Streamlit's st.code has a built-in copy button
        st.info("Copy the text below using the icon in the top right:")
        st.code(st.session_state.processed_text, language=None)
    
    with col2:
        st.download_button(
            label="📥 Download as Text File",
            data=st.session_state.processed_text,
            file_name=f"adhd_reader_{target_lang.lower()}.txt",
            mime="text/plain"
        )
        
        try:
            pdf_data = generate_pdf(st.session_state.processed_text)
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name=f"adhd_reader_{target_lang.lower()}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            st.info("Try downloading as a text file instead if the PDF fails.")
else:
    if not raw_text:
        st.info("Provide some content above and click 'Process Content' to begin.")
