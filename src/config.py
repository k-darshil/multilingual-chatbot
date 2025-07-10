"""
Configuration module for the Multilingual Document Chatbot.
Handles API keys, settings, and environment variables.
"""

import os
import streamlit as st
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for managing app settings and API keys."""
    
    # API Keys
    OPENAI_API_KEY: str = ""
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    IBM_DOCLING_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Neo4j Configuration
    NEO4J_URI: Optional[str] = None
    NEO4J_USERNAME: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None
    
    # App Settings
    MAX_FILE_SIZE_MB: int = 50
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese (Simplified)',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'ur': 'Urdu',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi'
    }
    
    @classmethod
    def load_config(cls):
        """Load configuration from environment variables and Streamlit secrets."""
        try:
            # Try to load from Streamlit secrets first
            cls.OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
            cls.GOOGLE_TRANSLATE_API_KEY = st.secrets.get("GOOGLE_TRANSLATE_API_KEY")
            cls.IBM_DOCLING_API_KEY = st.secrets.get("IBM_DOCLING_API_KEY")
            cls.HUGGINGFACE_API_KEY = st.secrets.get("HUGGINGFACE_API_KEY")
            
            cls.NEO4J_URI = st.secrets.get("NEO4J_URI")
            cls.NEO4J_USERNAME = st.secrets.get("NEO4J_USERNAME")
            cls.NEO4J_PASSWORD = st.secrets.get("NEO4J_PASSWORD")
            
        except Exception:
            # Fall back to environment variables
            cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
            cls.GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
            cls.IBM_DOCLING_API_KEY = os.getenv("IBM_DOCLING_API_KEY")
            cls.HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
            
            cls.NEO4J_URI = os.getenv("NEO4J_URI")
            cls.NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
            cls.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
        
        # Load other settings
        cls.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
        
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """Validate required configuration settings."""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OpenAI API key is required")
            
        return len(errors) == 0, errors
    
    @classmethod
    def get_language_options(cls) -> list[tuple[str, str]]:
        """Get language options for UI selection."""
        return [(code, name) for code, name in cls.SUPPORTED_LANGUAGES.items()]

# Initialize configuration
Config.load_config() 