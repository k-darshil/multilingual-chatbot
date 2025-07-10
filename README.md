# 🤖 Multilingual Document Chatbot

A sophisticated AI-powered chatbot that helps users understand legal, medical, and other important documents in their preferred language. Built using Retrieval-Augmented Generation (RAG) technique with multilingual support.

![Chatbot Demo](https://img.shields.io/badge/Status-Ready%20for%20Development-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-purple)

## 🌟 Features

### 📄 Document Processing
- **Multi-format Support**: PDF, DOCX, TXT, DOC files
- **Advanced Text Extraction**: IBM DocLing integration with fallback methods
- **Intelligent Chunking**: Optimized text segmentation for better RAG performance
- **Large File Support**: Handle documents up to 50MB

### 🌍 Multilingual Capabilities
- **20+ Languages Supported**: Including English, Spanish, French, German, Hindi, Arabic, Chinese, and more
- **Automatic Language Detection**: Smart detection of document language
- **Real-time Translation**: Multiple translation services with fallbacks
- **Cross-language Q&A**: Ask questions in your language about documents in any language

### 🤖 AI-Powered Intelligence
- **RAG Architecture**: Retrieval-Augmented Generation for accurate, context-aware answers
- **Vector Database**: ChromaDB for efficient semantic search
- **Source Attribution**: Clear references to document sections
- **Context-Aware Responses**: Answers grounded in document content

### 🎨 User Experience
- **Modern UI**: Beautiful, responsive Streamlit interface
- **Real-time Chat**: Interactive conversation experience
- **Document Management**: Easy upload, processing, and clearing
- **Progress Tracking**: Clear status indicators and loading states

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (required)
- Google Translate API key (optional, for better translation)

### Installation

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd chatbot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up API keys**:
   
   **Option A: Using Streamlit secrets (Recommended)**
   - Copy `.streamlit/secrets.toml` and fill in your API keys:
   ```toml
   OPENAI_API_KEY = "your_actual_openai_api_key_here"
   GOOGLE_TRANSLATE_API_KEY = "your_google_translate_api_key_here"
   ```

   **Option B: Using environment variables**
   - Copy `env.example` to `.env` and fill in your keys:
   ```bash
   cp env.example .env
   # Edit .env with your actual API keys
   ```

4. **Run the application**:
```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

## 📋 Detailed Setup

### API Keys Setup

#### OpenAI API Key (Required)
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your secrets.toml or .env file

#### Google Translate API Key (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Translation API
3. Create credentials and get your API key
4. Add it to your configuration

*Note: If you don't provide a Google Translate API key, the system will use free translation services.*

### Configuration Options

The application can be configured through several files:

- **`.streamlit/config.toml`**: Streamlit app configuration
- **`.streamlit/secrets.toml`**: API keys and secrets
- **`src/config.py`**: Application settings and supported languages

## 🏗️ Architecture

```
📁 Project Structure
├── 📄 app.py                 # Main Streamlit application
├── 📁 src/
│   ├── 📄 config.py          # Configuration management
│   ├── 📄 document_processor.py  # Document text extraction
│   ├── 📄 translation_service.py # Multilingual translation
│   └── 📄 rag_system.py      # RAG implementation
├── 📁 .streamlit/
│   ├── 📄 config.toml        # Streamlit configuration
│   └── 📄 secrets.toml       # API keys (create from template)
├── 📄 requirements.txt       # Python dependencies
└── 📄 README.md             # Project documentation
```

### System Flow

1. **Document Upload** → User uploads PDF/DOCX/TXT file
2. **Text Extraction** → Multi-method extraction with DocLing/fallbacks
3. **Document Indexing** → Text chunking and vector embedding storage
4. **Question Processing** → User asks question in preferred language
5. **Retrieval** → Semantic search for relevant document chunks
6. **Answer Generation** → OpenAI GPT generates contextual response
7. **Translation** → Response translated to user's language if needed

## 🛠️ Technology Stack

### Core Technologies
- **Frontend**: Streamlit (Python web framework)
- **AI/LLM**: OpenAI GPT-3.5-turbo
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)

### Document Processing
- **Primary**: IBM DocLing (advanced document parsing)
- **Fallbacks**: pdfplumber, PyPDF2, python-docx

### Translation Services
- **Primary**: Google Cloud Translation API
- **Fallbacks**: deep-translator, googletrans

### Additional Libraries
- **Text Processing**: NLTK, tiktoken, langdetect
- **Data Handling**: pandas, numpy
- **Configuration**: python-dotenv, pydantic

## 📖 Usage Guide

### 1. Upload a Document
- Click "Choose a document" in the upload section
- Supported formats: PDF, DOCX, TXT, DOC
- Maximum file size: 50MB
- Wait for processing and indexing to complete

### 2. Select Your Language
- Use the sidebar to choose your preferred response language
- 20+ languages supported including major world languages
- The system will auto-detect document language

### 3. Ask Questions
- Type your question in the chat input at the bottom
- Ask in any supported language
- Questions can be about content, summaries, specific details, etc.

### 4. Review Responses
- Get answers in your selected language
- View source attributions showing which document sections were used
- See similarity scores for transparency

### Example Questions
- "What are the main terms of this contract?"
- "Summarize the key medical recommendations"
- "What are my rights according to this document?"
- "¿Cuáles son los efectos secundarios mencionados?" (Spanish)
- "इस दस्तावेज़ में क्या मुख्य बातें हैं?" (Hindi)

## ⚙️ Advanced Configuration

### Customizing Languages
Edit `src/config.py` to modify the `SUPPORTED_LANGUAGES` dictionary:

```python
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'your_lang_code': 'Your Language Name',
    # Add more languages...
}
```

### Adjusting RAG Parameters
Modify these settings in `src/config.py`:

```python
MAX_CHUNK_SIZE = 1000      # Characters per chunk
CHUNK_OVERLAP = 200        # Overlap between chunks
```

### Database Configuration
For persistent storage, configure Neo4j (optional):

```toml
[secrets]
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your_password"
```

## 🔧 Troubleshooting

### Common Issues

**1. "OpenAI API key is required" error**
- Ensure your OpenAI API key is correctly set in secrets.toml
- Verify the key has sufficient credits

**2. Document processing fails**
- Check file format is supported (PDF, DOCX, TXT)
- Ensure file size is under 50MB
- Try different PDF if text extraction fails

**3. Translation not working**
- Check if your preferred language is in the supported list
- Verify Google Translate API key if using premium features

**4. ChromaDB errors**
- Delete the `chroma_db` folder and restart the application
- Check disk space availability

### Performance Tips

- **Large Documents**: For very large documents, consider splitting them into sections
- **Response Time**: First question may be slower due to model loading
- **Memory Usage**: Clear documents when done to free up memory

## 🧪 Development

### Adding New Features

The modular architecture makes it easy to extend:

- **New Document Types**: Extend `DocumentProcessor` class
- **Translation Services**: Add new methods to `TranslationService`
- **Different LLMs**: Modify `RAGSystem` to support other models
- **UI Improvements**: Customize the Streamlit interface in `app.py`

### Testing

```bash
# Install development dependencies
pip install pytest black flake8

# Run tests (when available)
pytest

# Format code
black src/ app.py

# Lint code
flake8 src/ app.py
```

## 📊 Project Metrics

This project addresses the requirements outlined in the original proposal:

- ✅ **Document Upload & Processing**: Multi-format support with robust extraction
- ✅ **Multilingual Translation**: 20+ languages with multiple service fallbacks
- ✅ **RAG Implementation**: Advanced retrieval and generation pipeline
- ✅ **Modern UI**: Streamlit-based responsive interface
- ✅ **API Integration**: OpenAI, Google Translate, and other services
- ✅ **Modular Architecture**: Extensible and maintainable codebase

### Evaluation Metrics
The system can be evaluated using:
- **BLEU/ROUGE scores** for translation quality
- **Exact Match (EM)** for factual accuracy
- **F1 score** for information retrieval
- **User satisfaction** through interface usability

## 🤝 Contributing

Contributions are welcome! Please consider:

1. **Code Quality**: Follow Python best practices and existing code style
2. **Documentation**: Update README and code comments for any changes
3. **Testing**: Add tests for new functionality
4. **Issues**: Report bugs and suggest features through GitHub issues

## 📄 License

This project is created for educational purposes as part of an AI course project. Please ensure compliance with API terms of service for OpenAI and Google services.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Streamlit** for the amazing web framework
- **IBM DocLing** for advanced document processing
- **ChromaDB** for vector database capabilities
- **Sentence Transformers** for embedding models

## 📞 Support

For questions about this implementation:

1. Check the troubleshooting section above
2. Review the code comments and documentation
3. Ensure all API keys are correctly configured
4. Verify all dependencies are installed

---

**Built with ❤️ for multilingual document understanding**

*This chatbot aims to break down language barriers and make important documents accessible to everyone, regardless of their native language.* 