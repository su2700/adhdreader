# GEMINI.md - ADHD-Friendly Reader & Translator

## Project Overview
An AI-powered web application designed to enhance reading accessibility for individuals with ADHD. The application simplifies complex content, provides translations, and applies focus-enhancing visual effects like "Bionic Reading."

### Main Technologies
- **Frontend/Backend:** [Streamlit](https://streamlit.io/)
- **AI Engine:** [Google Gemini API](https://ai.google.dev/) (via `google-generativeai`)
- **PDF Processing:** [PyPDF2](https://pypdf2.readthedocs.io/)
- **Web Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Requests](https://requests.readthedocs.io/)
- **Environment Management:** `python-dotenv`

### Architecture
The project is a monolithic Streamlit application centered around `app.py`.
- **Text Extraction:** Functions for PDF (`extract_text_from_pdf`) and URL (`extract_text_from_url`) processing.
- **AI Processing:** Uses Gemini models to rewrite and translate text based on a specific ADHD-friendly prompt.
- **Visual Enhancements:** `apply_bionic_reading` uses regex to bold the first half of words to improve eye tracking.
- **Exporting:** Users can download the processed content as a plain text file or as a formatted PDF.
- **UI:** Interactive sidebar for settings (input source, language, model selection) and a main area for content display.

## Building and Running

### Prerequisites
- Python 3.8+
- A Google Gemini API Key

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   - Create a `.env` file in the root.
   - Add your key: `GEMINI_API_KEY=your_key_here`

### Running the App
```bash
streamlit run app.py
```

### Testing
- Currently, there is no automated test suite. Manual testing is performed by running the app and verifying processing across different input types (Text, URL, PDF).

## Development Conventions

### Coding Style
- Follows standard Python (PEP 8) conventions.
- Uses docstrings for main functions.
- Streamlit-specific patterns for UI state and sidebar management.

### AI Integration
- Models are dynamically fetched using `genai.list_models()`.
- The prompt engineering in `process_with_ai` is central to the "ADHD-friendly" transformation.

### Future Improvements (TODO)
- [ ] Add unit tests for text extraction and bionic reading logic.
- [ ] Implement more robust error handling for scraping and PDF parsing.
- [ ] Add support for more document formats (e.g., DOCX).
- [ ] Improve the "Bionic Reading" regex to handle edge cases better.
