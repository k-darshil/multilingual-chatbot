# Multilingual Document Chatbot

A powerful AI-powered chatbot that can process documents in multiple languages and answer questions about them. Built with **Gradio** for an intuitive web interface.

## Features

- 📄 **Document Processing**: Supports PDF, DOCX, TXT files with multiple extraction methods
- 🌍 **Multilingual Support**: 20+ languages with automatic detection and translation
- 🤖 **AI-Powered Q&A**: RAG-based question answering with source attribution
- 🔍 **Smart Search**: Vector-based document search for accurate responses
- 💻 **Modern Dark UI**: Beautiful dark-themed interface built with Gradio

## Setup

### Prerequisites

- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM recommended
- **Storage**: 2GB free space for dependencies

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd chatbot
```

### Step 2: Create a Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv env-chatbot
env-chatbot\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv env-chatbot
source env-chatbot/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note**: Installation may take 5-10 minutes due to machine learning dependencies.

### Step 4: Configure API Keys

1. **Copy the example environment file:**
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file with your API keys:**

   **Required Configuration:**
   ```env
   # OpenAI API Key (REQUIRED for AI features)
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   **Optional Configuration:**
   ```env
   # Google Cloud Translation (Optional - for enhanced translation)
   GOOGLE_PROJECT_ID=your-google-cloud-project-id
   GOOGLE_TRANSLATE_API_KEY=/path/to/your/service-account-key.json

   # App Settings
   APP_DEBUG=False
   MAX_FILE_SIZE_MB=50

   # Gradio Settings
   GRADIO_SHARE=false  # Set to 'true' for public shareable link
   ```

#### Getting API Keys

**OpenAI API Key (Required):**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

**Google Cloud Translation (Optional):**
- See `google_cloud_setup.md` for detailed Google Cloud setup instructions
- This enables enhanced translation features but is not required for basic functionality

### Step 5: Run the Application

**Option 1: Direct launch**
```bash
python app.py
```

**Option 2: Using the launcher**
```bash
python run_gradio_app.py
```

### Step 6: Access the Application

1. **Open your web browser**
2. **Navigate to:** `http://localhost:7860`
3. **Start using the chatbot:**
   - Upload a document (PDF, DOCX, or TXT)
   - Ask questions about your document
   - Enjoy multilingual support!

### Verification

To verify your setup is working correctly:

1. The web interface should load without errors
2. You should be able to upload a small test document
3. The system should respond to basic questions
4. Check the console for any error messages

## Advanced Configuration

### Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for AI features | None |
| `GOOGLE_PROJECT_ID` | ⚠️ Optional | Google Cloud project ID | None |
| `GOOGLE_TRANSLATE_API_KEY` | ⚠️ Optional | Path to Google service account key | None |
| `APP_DEBUG` | ❌ No | Enable debug mode | False |
| `MAX_FILE_SIZE_MB` | ❌ No | Maximum file upload size | 50 |
| `GRADIO_SHARE` | ❌ No | Create public shareable link | false |

### Custom Port Configuration

To run on a different port, modify the launch settings in `app.py` or `run_gradio_app.py`:

```python
demo.launch(server_port=8080)  # Change to your desired port
```

## Troubleshooting

### Common Setup Issues

**1. "Module not found" errors:**
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**2. "OpenAI API key not set" error:**
- Verify your `.env` file exists in the project root
- Check that `OPENAI_API_KEY` is set correctly
- Ensure no extra spaces or quotes around the key

**3. "Port already in use" error:**
- Change the port in the launch command
- Or stop other applications using port 7860

**4. Document processing failures:**
- Check file format (PDF, DOCX, TXT only)
- Ensure file size is under 50MB
- Try with a different document

**5. Translation not working:**
- Translation features are optional
- Check Google Cloud credentials if using translation
- The app works without translation enabled

### Performance Issues

**If the application is running slowly:**
- Ensure you have at least 4GB RAM available
- Close other memory-intensive applications
- Consider using smaller documents for testing

### Getting Help

1. Check the console output for specific error messages
2. Ensure all prerequisites are met
3. Verify your API keys are valid
4. Try with a fresh virtual environment

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