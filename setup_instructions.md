# 🚀 Quick Setup Guide - Multilingual Document Chatbot

Follow these steps to get your multilingual document chatbot running in minutes!

## 📋 Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] OpenAI API key (get one at [OpenAI Platform](https://platform.openai.com/api-keys))
- [ ] Google Translate API key (optional, get one at [Google Cloud Console](https://console.cloud.google.com/))

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys

**Option A: Streamlit Secrets (Recommended)**
1. Open `.streamlit/secrets.toml`
2. Replace the placeholder with your actual OpenAI API key:
```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
```

**Option B: Environment Variables**
1. Copy `env.example` to `.env`:
```bash
cp env.example .env
```
2. Edit `.env` and add your API key

### Step 3: Run the Application
```bash
streamlit run app.py
```

### Step 4: Open in Browser
Navigate to `http://localhost:8501`

## 🎯 First Test

1. **Upload a document** (PDF, DOCX, or TXT)
2. **Select your preferred language** in the sidebar
3. **Ask a question** about your document
4. **Get answers** in your chosen language!

## 🔧 Troubleshooting

### "OpenAI API key is required"
- Check that your API key is correctly entered in `secrets.toml`
- Ensure your OpenAI account has available credits

### Installation Issues
- Try using a virtual environment:
```bash
python -m venv chatbot_env
source chatbot_env/bin/activate  # On Windows: chatbot_env\Scripts\activate
pip install -r requirements.txt
```

### Document Processing Errors
- Ensure your document is under 50MB
- Try with a simple text file first to test the system

## 📞 Need Help?

Check the full [README.md](README.md) for detailed documentation and troubleshooting.

---

**You're all set! 🎉 Start uploading documents and asking questions in your preferred language!** 