"""
Configuration module for the Multilingual Document Chatbot.
Handles API keys, settings, and environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from src.language_mapping import LanguageMapping, TranslationService

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for managing app settings and API keys."""
    
    # API Keys
    OPENAI_API_KEY: str = ""
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    GOOGLE_PROJECT_ID: Optional[str] = None
    IBM_DOCLING_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Neo4j Configuration
    NEO4J_URI: Optional[str] = None
    NEO4J_USERNAME: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None
    
    # Translation Service Configuration
    TRANSLATION_SERVICE: str = "google_cloud"  # Default service
    NLLB_MODEL_NAME: str = "facebook/nllb-200-distilled-600M"
    
    # App Settings
    MAX_FILE_SIZE_MB: int = 50
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Legacy supported languages (kept for backward compatibility)
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
        """Load configuration from environment variables and .env file."""
        # Load from environment variables (which includes .env via dotenv)
        cls.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        cls.GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
        cls.GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
        cls.IBM_DOCLING_API_KEY = os.getenv("IBM_DOCLING_API_KEY")
        cls.HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
        
        cls.NEO4J_URI = os.getenv("NEO4J_URI")
        cls.NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
        cls.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
        
        # Translation service configuration
        cls.TRANSLATION_SERVICE = os.getenv("TRANSLATION_SERVICE", "google_cloud")
        cls.NLLB_MODEL_NAME = os.getenv("NLLB_MODEL_NAME", "facebook/nllb-200-distilled-600M")
        
        # Load other settings
        cls.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
        
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """Validate required configuration settings."""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OpenAI API key is required")
            
        # Check translation service configuration
        if cls.TRANSLATION_SERVICE == "google_cloud":
            if not cls.GOOGLE_TRANSLATE_API_KEY or not cls.GOOGLE_PROJECT_ID:
                errors.append("Google Cloud Translation requires GOOGLE_TRANSLATE_API_KEY and GOOGLE_PROJECT_ID")
        elif cls.TRANSLATION_SERVICE == "nllb":
            # NLLB doesn't require API keys but check if transformers is available
            try:
                import torch
                import transformers
            except ImportError:
                errors.append("NLLB service requires 'torch' and 'transformers' packages")
        else:
            errors.append(f"Unknown translation service: {cls.TRANSLATION_SERVICE}")
            
        return len(errors) == 0, errors
    
    @classmethod
    def get_language_options(cls, service: Optional[str] = None) -> list[tuple[str, str]]:
        """Get language options for UI selection based on translation service."""
        if service == "google_cloud":
            return LanguageMapping.get_language_options_for_service(TranslationService.GOOGLE_CLOUD)
        elif service == "nllb":
            return LanguageMapping.get_language_options_for_service(TranslationService.NLLB)
        else:
            # Default to all languages (legacy behavior)
            return [(code, name) for code, name in cls.SUPPORTED_LANGUAGES.items()]
    
    @classmethod
    def get_translation_service_enum(cls) -> TranslationService:
        """Get the translation service enum from config."""
        if cls.TRANSLATION_SERVICE == "google_cloud":
            return TranslationService.GOOGLE_CLOUD
        elif cls.TRANSLATION_SERVICE == "nllb":
            return TranslationService.NLLB
        else:
            # Default to Google Cloud
            return TranslationService.GOOGLE_CLOUD
    
    @classmethod
    def get_translation_service_options(cls) -> list[tuple[str, str]]:
        """Get available translation service options for UI."""
        return [
            ("google_cloud", "Google Cloud Translate"),
            ("nllb", "NLLB (Open Source)")
        ]
    
    @classmethod
    def is_google_cloud_available(cls) -> bool:
        """Check if Google Cloud translation is properly configured."""
        return bool(cls.GOOGLE_TRANSLATE_API_KEY and cls.GOOGLE_PROJECT_ID)
    
    @classmethod
    def is_nllb_available(cls) -> bool:
        """Check if NLLB translation dependencies are available."""
        try:
            import torch
            import transformers
            return True
        except ImportError:
            return False

# Initialize configuration
Config.load_config() 