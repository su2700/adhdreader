# 📖 ADHD-Friendly Reader & Translator

An AI-powered web application designed to make reading more accessible for individuals with ADHD. It transforms dense, complex content into simplified, scannable, and highly legible formats, with built-in support for translation.

## 🚀 Features

*   **Multi-Format Input:** Process content from website URLs, uploaded PDF files, or direct text input.
*   **AI Simplification:** Uses Google Gemini to rewrite complex sentences, break down dense paragraphs, and extract key takeaways into bullet points.
*   **Translation:** Automatically translate the processed content into Chinese, Spanish, French, German, or English.
*   **Bionic Reading:** Toggle a "Bionic Reading" effect that bolds the first half of words to guide the eye and improve focus.
*   **Dynamic Model Selection:** Automatically detects and lets you choose from available Gemini models (e.g., Gemini 1.5 Pro, Gemini 1.5 Flash) supported by your API key.
*   **Clean UI:** A distraction-free interface built with Streamlit.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd adhdreader
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    *   Create a `.env` file in the root directory (you can use `.env.example` as a template).
    *   Add your Google Gemini API key:
        ```env
        GEMINI_API_KEY=your_actual_api_key_here
        ```

## 📖 Usage

1.  **Start the application:**
    ```bash
    streamlit run app.py
    ```
2.  **Select your input source** (Text, URL, or PDF) in the sidebar.
3.  **Choose your target language** and preferred **AI model**.
4.  **Click "Process Content"** to generate the ADHD-friendly version.

## 🧰 Tech Stack

*   **Frontend/Backend:** [Streamlit](https://streamlit.io/)
*   **AI Engine:** [Google Gemini API](https://ai.google.dev/)
*   **PDF Processing:** [PyPDF2](https://pypdf2.readthedocs.io/)
*   **Web Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Requests](https://requests.readthedocs.io/)

## 🛡️ License

MIT License - feel free to use and modify for your own projects!
