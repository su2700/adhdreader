import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import io
import os
from dotenv import load_dotenv
import re

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
            
            st.divider()
            st.subheader("Processed Content")
            
            if bionic_enabled:
                processed_text = apply_bionic_reading(processed_text)
            
            st.markdown(processed_text)
else:
    st.info("Provide some content above and click 'Process Content' to begin.")
