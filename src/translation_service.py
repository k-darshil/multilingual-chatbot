"""
Translation service module for multilingual document chatbot.
Supports Google Translate API with fallback to free translation services.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from deep_translator import GoogleTranslator
# from googletrans import Translator as GoogleTranslatorAPI  # Commented out due to httpcore compatibility issues
import langdetect
from src.config import Config

class TranslationService:
    """Service for translating text between different languages."""
    
    def __init__(self):
        self.api_translator = None
        self.free_translator = GoogleTranslator()
        self.fallback_translator = None  # Disabled due to compatibility issues
        
        # Initialize API translator if key is available
        if Config.GOOGLE_TRANSLATE_API_KEY:
            try:
                # Note: For Google Cloud Translation API, you'd initialize it here
                # This is a placeholder for the actual API initialization
                # self.api_translator = GoogleTranslatorAPI()  # Disabled for now
                pass
            except Exception as e:
                st.warning(f"Could not initialize Google Translate API: {e}")
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es', 'hi') or None if detection fails
        """
        try:
            # Use langdetect library
            detected = langdetect.detect(text[:1000])  # Use first 1000 chars for detection
            return detected
        except Exception as e:
            st.warning(f"Language detection failed: {e}")
            return None
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> Dict[str, Any]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: 'auto' for auto-detection)
            
        Returns:
            Dict with translation result, confidence, and metadata
        """
        if not text.strip():
            return {"success": False, "error": "Empty text provided"}
        
        # If source and target are the same, return original text
        detected_lang = self.detect_language(text)
        if detected_lang == target_language:
            return {
                "success": True,
                "translated_text": text,
                "source_language": detected_lang,
                "target_language": target_language,
                "method": "no_translation_needed"
            }
        
        # Try different translation methods (googletrans disabled due to compatibility issues)
        translation_methods = [
            ("google_api", self._translate_with_api),
            ("google_free", self._translate_with_free_google),
            # ("googletrans", self._translate_with_googletrans)  # Disabled for now
        ]
        
        for method_name, method_func in translation_methods:
            try:
                result = method_func(text, target_language, source_language)
                if result["success"]:
                    result["method"] = method_name
                    return result
            except Exception as e:
                st.warning(f"Translation method {method_name} failed: {e}")
                continue
        
        return {"success": False, "error": "All translation methods failed"}
    
    def _translate_with_api(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using Google Cloud Translation API (if available)."""
        if not self.api_translator or not Config.GOOGLE_TRANSLATE_API_KEY:
            raise Exception("Google Translate API not available")
        
        # This is a placeholder for actual Google Cloud Translation API
        # You would implement the actual API call here
        raise Exception("Google Cloud Translation API not implemented")
    
    def _translate_with_free_google(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using deep-translator GoogleTranslator."""
        try:
            # Handle auto detection
            if source_lang == 'auto':
                detected_lang = self.detect_language(text)
                source_lang = detected_lang if detected_lang else 'en'
            
            # Create translator instance
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Split long text into chunks to avoid limits
            chunks = self._split_text_for_translation(text)
            translated_chunks = []
            
            for chunk in chunks:
                translated_chunk = translator.translate(chunk)
                if translated_chunk:
                    translated_chunks.append(translated_chunk)
            
            translated_text = ' '.join(translated_chunks)
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang
            }
            
        except Exception as e:
            raise Exception(f"Free Google translation failed: {e}")
    
    def _translate_with_googletrans(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using googletrans library."""
        try:
            # Split long text into chunks
            chunks = self._split_text_for_translation(text, max_length=4000)
            translated_chunks = []
            detected_source = None
            
            for chunk in chunks:
                result = self.fallback_translator.translate(
                    chunk, 
                    dest=target_lang, 
                    src=source_lang if source_lang != 'auto' else None
                )
                
                if result:
                    translated_chunks.append(result.text)
                    if not detected_source:
                        detected_source = result.src
            
            translated_text = ' '.join(translated_chunks)
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": detected_source or source_lang,
                "target_language": target_lang
            }
            
        except Exception as e:
            raise Exception(f"Googletrans translation failed: {e}")
    
    def _split_text_for_translation(self, text: str, max_length: int = 5000) -> List[str]:
        """Split text into chunks suitable for translation APIs."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences first
        sentences = text.replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed limit, save current chunk
            if len(current_chunk) + len(sentence) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += (" " + sentence if current_chunk else sentence)
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def translate_document_summary(self, document_info: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Translate document summary and metadata.
        
        Args:
            document_info: Document information dict
            target_language: Target language code
            
        Returns:
            Translated document information
        """
        try:
            # Create a summary of the document
            text_preview = document_info.get('text', '')[:500] + "..."
            
            summary_text = f"""Document: {document_info.get('filename', 'Unknown')}
File Type: {document_info.get('file_type', 'Unknown')}
Pages: {document_info.get('pages', 'Unknown')}
Word Count: {document_info.get('word_count', 'Unknown')}

Content Preview:
{text_preview}"""
            
            translation_result = self.translate_text(summary_text, target_language)
            
            if translation_result["success"]:
                return {
                    "success": True,
                    "translated_summary": translation_result["translated_text"],
                    "source_language": translation_result.get("source_language"),
                    "target_language": target_language
                }
            else:
                return {"success": False, "error": translation_result.get("error")}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to translate document summary: {e}"}
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages for translation."""
        return Config.SUPPORTED_LANGUAGES.copy()
    
    def is_translation_needed(self, text: str, target_language: str) -> bool:
        """Check if translation is needed based on detected language."""
        detected_lang = self.detect_language(text)
        return detected_lang != target_language if detected_lang else True
    
    def get_language_name(self, language_code: str) -> str:
        """Get full language name from language code."""
        return Config.SUPPORTED_LANGUAGES.get(language_code, language_code.upper())
    
    def validate_language_code(self, language_code: str) -> bool:
        """Validate if language code is supported."""
        return language_code in Config.SUPPORTED_LANGUAGES
    
    def batch_translate(self, texts: List[str], target_language: str, source_language: str = 'auto') -> List[Dict[str, Any]]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            List of translation results
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.translate_text(text, target_language, source_language)
                result["index"] = i
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "index": i
                })
        
        return results 