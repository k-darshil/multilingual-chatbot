# Multilingual Document Chatbot

A powerful AI-powered chatbot that can process documents in multiple languages and answer questions about them. Built with **Gradio** for an intuitive web interface.

## Features

- 📄 **Document Processing**: Supports PDF, DOCX, TXT files with multiple extraction methods
- 🌍 **Multilingual Support**: 20+ languages with automatic detection and translation
- 🤖 **AI-Powered Q&A**: RAG-based question answering with source attribution
- 🔍 **Smart Search**: Vector-based document search for accurate responses
- 💻 **Modern Dark UI**: Beautiful dark-themed interface built with Gradio

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys** (copy `env.example` to `.env` and fill in your keys):
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application:**
   ```bash
   python app.py
   # or use the launcher
   python run_gradio_app.py
   ```

4. **Open in browser:**
   - Navigate to `http://localhost:7860`
   - Upload a document and start asking questions!

## Configuration

Create a `.env` file or set environment variables:

```env
# OpenAI API (required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud Translation (optional, for translation features)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your_project_id

# Alternative: Direct API key
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
```

## Supported Languages

The chatbot supports 20+ languages including:
- English, Spanish, French, German, Italian
- Chinese (Simplified/Traditional), Japanese, Korean
- Arabic, Russian, Portuguese, Dutch
- And many more...

## Architecture

- **Frontend**: Gradio web interface with dark theme
- **Backend**: Python with LangChain for RAG pipeline
- **Document Processing**: Multiple extraction methods (DocLing, pdfplumber, PyPDF2)
- **Vector Database**: ChromaDB for efficient document search
- **Translation**: Google Cloud Translate API
- **AI Model**: OpenAI GPT for question answering

## Migration from Streamlit

This application has been migrated from Streamlit to Gradio for better session management and user experience. All core functionality remains the same:

- ✅ Document upload and processing
- ✅ Language detection and translation
- ✅ RAG-based question answering
- ✅ Source attribution
- ✅ Dark theme support
- ✅ Multilingual interface

## Development

For development setup and advanced configuration, see:
- `setup_instructions.md` - Detailed setup guide
- `google_cloud_setup.md` - Google Cloud configuration
- `src/` - Core application modules

## Troubleshooting

Common issues and solutions:

1. **API Key Issues**: Ensure your OpenAI API key is set correctly
2. **Document Processing Errors**: Check file format and size (max 50MB)
3. **Translation Failures**: Verify Google Cloud credentials if using translation
4. **Port Already in Use**: The app runs on port 7860 by default

## License

MIT License - see LICENSE file for details.

---

*Built with ❤️ using Gradio, LangChain, and OpenAI* 