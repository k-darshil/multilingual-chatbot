"""
Translation service module for multilingual document chatbot.
Supports Google Translate API with fallback to free translation services.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from google.cloud import translate_v3 as translate
import langdetect
import json
import hashlib
from pathlib import Path
from src.config import Config

class TranslationService:
    """Service for translating text between different languages."""
    
    def __init__(self):
        
        print("Initializing Translation Service")
        print("Config.GOOGLE_PROJECT_ID", Config.GOOGLE_PROJECT_ID)
        print("Config.GOOGLE_TRANSLATE_API_KEY", Config.GOOGLE_TRANSLATE_API_KEY)
        
        self.translate_client = None
        self.cache_dir = Path("cache")
        self.project_id = Config.GOOGLE_PROJECT_ID
        self.location = "global"
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize Google Cloud Translate v3 client with service account
        try:
            if not Config.GOOGLE_PROJECT_ID:
                raise ValueError("GOOGLE_PROJECT_ID not configured")
            
            # Google Cloud Translation API v3 requires service account authentication
            if Config.GOOGLE_TRANSLATE_API_KEY:
                try:
                    # Try to parse as JSON service account
                    service_account_info = json.loads(Config.GOOGLE_TRANSLATE_API_KEY)
                    self.translate_client = translate.TranslationServiceClient.from_service_account_info(service_account_info)
                    st.success("✅ Google Cloud Translate v3 initialized with service account.")
                except json.JSONDecodeError:
                    # If not JSON, treat as file path
                    import os
                    if os.path.exists(Config.GOOGLE_TRANSLATE_API_KEY):
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_TRANSLATE_API_KEY
                        self.translate_client = translate.TranslationServiceClient()
                        st.success("✅ Google Cloud Translate v3 initialized with service account file.")
                    else:
                        raise ValueError("GOOGLE_TRANSLATE_API_KEY must be either JSON content or path to service account file")
            else:
                # Try Application Default Credentials
                self.translate_client = translate.TranslationServiceClient()
                st.success("✅ Google Cloud Translate v3 initialized with Application Default Credentials.")
            
        except Exception as e:
            st.error(f"❌ Could not initialize Google Cloud Translate: {e}")
            st.info("""
            **Translation Setup Required**
            
            Google Cloud Translation API v3 requires service account authentication.
            
            **Option 1: Service Account JSON (Recommended)**
            Put your service account JSON content in secrets.toml:
            ```toml
            GOOGLE_TRANSLATE_API_KEY = '{"type": "service_account", "project_id": "...", ...}'
            GOOGLE_PROJECT_ID = "your-project-id"
            ```
            
            **Option 2: Service Account File**
            Put the file path in secrets.toml:
            ```toml
            GOOGLE_TRANSLATE_API_KEY = "/path/to/service-account.json"
            GOOGLE_PROJECT_ID = "your-project-id"
            ```
            
            **Option 3: Application Default Credentials**
            Run: `gcloud auth application-default login`
            """)
    
    def _generate_cache_key(self, filename: str, text: str, target_language: str, source_language: str = 'auto') -> str:
        """Generate a unique cache key for translation."""
        # Create a hash of the content and parameters to ensure uniqueness
        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_key = f"{filename}_{content_hash}_{source_language}_{target_language}"
        return cache_key
    
    def _save_translation_cache(self, cache_key: str, translation_result: Dict[str, Any]) -> None:
        """Save translation result to cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(translation_result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.warning(f"Failed to save translation cache: {e}")
    
    def _load_translation_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load translation result from cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.warning(f"Failed to load translation cache: {e}")
        return None
    
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
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto', filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text to target language with caching support.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: 'auto' for auto-detection)
            filename: Optional filename for caching (if provided, results will be cached)
            
        Returns:
            Dict with translation result, confidence, and metadata
        """
        if not text.strip():
            return {"success": False, "error": "Empty text provided"}
        
        # Check cache first if filename is provided
        print("Checking cache for filename", filename)
        cache_key = None
        if filename:
            cache_key = self._generate_cache_key(filename, text, target_language, source_language)
            cached_result = self._load_translation_cache(cache_key)
            if cached_result:
                cached_result["method"] = cached_result.get("method", "cached") + "_cached"
                print("cache found")
                return cached_result
        print("no cache found")
        
        # If source and target are the same, return original text
        detected_lang = self.detect_language(text)
        if detected_lang == target_language:
            result = {
                "success": True,
                "translated_text": text,
                "source_language": detected_lang,
                "target_language": target_language,
                "method": "no_translation_needed"
            }
            
            # Save to cache if filename provided
            if filename and cache_key:
                self._save_translation_cache(cache_key, result)
            
            return result
        
        # Use Google Cloud Translate API
        try:
            result = self._translate_with_google_cloud(text, target_language, source_language)
            
            # print("Google Cloud Translation result", result)
            
            if result["success"]:
                result["method"] = "google_cloud_translate"
                
                # Save to cache if filename provided
                if filename and cache_key:
                    print("Saving translation cache", cache_key)
                    self._save_translation_cache(cache_key, result)
                
                return result
        except Exception as e:
            st.warning(f"Google Cloud Translation failed: {e}")
            return {"success": False, "error": f"Translation failed: {e}"}
    
    def _translate_with_google_cloud(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """Translate using Google Cloud Translation API v3."""
        if not self.translate_client:
            raise Exception("Google Cloud Translate client not initialized")
        
        if not self.project_id:
            raise Exception("Google Cloud Project ID not configured")
        
        try:
            # Construct the parent path for the API request
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            # Split long text into chunks to avoid API limits
            chunks = self._split_text_for_translation(text)
            translated_chunks = []
            detected_source_lang = source_lang
            
            for chunk in chunks:
                # Prepare request parameters
                request_params = {
                    "parent": parent,
                    "contents": [chunk],
                    "mime_type": "text/plain",
                    "target_language_code": target_lang,
                }
                
                # Only add source language if it's not auto-detection
                if source_lang != 'auto':
                    request_params["source_language_code"] = source_lang
                
                # Translate the chunk
                response = self.translate_client.translate_text(request=request_params)
                
                if response.translations:
                    translation = response.translations[0]
                    translated_chunks.append(translation.translated_text)
                    
                    # Capture detected source language from first translation if auto-detection
                    if source_lang == 'auto' and hasattr(translation, 'detected_language_code'):
                        detected_source_lang = translation.detected_language_code
                else:
                    translated_chunks.append(chunk)  # Fallback to original text
            
            translated_text = ' '.join(translated_chunks)
            
            return {
                "success": True,
                "translated_text": translated_text,
                "source_language": detected_source_lang,
                "target_language": target_lang
            }
            
        except Exception as e:
            raise Exception(f"Google Cloud translation failed: {e}")
    
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
        Translate document summary and metadata with caching support.
        
        Args:
            document_info: Document information dict
            target_language: Target language code
            
        Returns:
            Translated document information
        """
        try:
            # Create a summary of the document
            text_preview = document_info.get('text', '')[:500] + "..."
            filename = document_info.get('filename', 'Unknown')
            
            summary_text = f"""Document: {filename}
File Type: {document_info.get('file_type', 'Unknown')}
Pages: {document_info.get('pages', 'Unknown')}
Word Count: {document_info.get('word_count', 'Unknown')}

Content Preview:
{text_preview}"""
            
            # Use filename for caching the document summary translation
            translation_result = self.translate_text(summary_text, target_language, filename=f"{filename}_summary")
            
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
    
    def batch_translate(self, texts: List[str], target_language: str, source_language: str = 'auto', filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Translate multiple texts in batch with caching support.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code
            filename: Optional filename for caching
            
        Returns:
            List of translation results
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                # Create a unique filename for each text chunk if base filename provided
                chunk_filename = f"{filename}_chunk_{i}" if filename else None
                result = self.translate_text(text, target_language, source_language, filename=chunk_filename)
                result["index"] = i
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "index": i
                })
        
        return results
    
    def clear_translation_cache(self, filename_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear translation cache files.
        
        Args:
            filename_pattern: Optional pattern to match specific files (if None, clears all)
            
        Returns:
            Dict with operation result and count of files cleared
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            files_removed = 0
            
            for cache_file in cache_files:
                if filename_pattern is None or filename_pattern in cache_file.name:
                    cache_file.unlink()
                    files_removed += 1
            
            return {
                "success": True,
                "files_removed": files_removed,
                "message": f"Cleared {files_removed} cache files"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to clear cache: {e}"
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the translation cache.
        
        Returns:
            Dict with cache statistics
        """
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(cache_file.stat().st_size for cache_file in cache_files)
            
            return {
                "success": True,
                "total_files": len(cache_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_directory": str(self.cache_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get cache stats: {e}"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Google Cloud Translate connection.
        
        Returns:
            Dict with connection test results
        """
        if not self.translate_client:
            return {
                "success": False,
                "error": "Translation client not initialized. Please check your authentication setup."
            }
        
        if not self.project_id:
            return {
                "success": False,
                "error": "Google Cloud Project ID not configured. Please set GOOGLE_PROJECT_ID."
            }
        
        try:
            # Test with a simple translation using v3 API
            test_text = "Hello"
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            response = self.translate_client.translate_text(
                request={
                    "parent": parent,
                    "contents": [test_text],
                    "mime_type": "text/plain",
                    "target_language_code": "es"
                }
            )
            
            if response.translations:
                translation = response.translations[0]
                return {
                    "success": True,
                    "message": "Google Cloud Translate v3 connection successful!",
                    "test_translation": {
                        "original": test_text,
                        "translated": translation.translated_text,
                        "target_language": "es",
                        "detected_source": getattr(translation, 'detected_language_code', 'auto')
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Translation test failed - no translations returned"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Translation test failed: {e}"
            } 