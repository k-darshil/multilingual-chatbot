"""
NLLB Translation Service for open-source translation using Facebook's NLLB model.
Handles model caching, loading, and translation with support for multiple languages.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import langdetect

from src.language_mapping import LanguageMapping, TranslationService

class NLLBTranslationService:
    """Open-source translation service using Facebook's NLLB model."""
    
    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.translator = None
        self.cache_dir = Path("cache")
        self.models_dir = Path("models")
        
        # Create directories if they don't exist
        self.cache_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        print(f"🔍 Initializing NLLB Translation Service with model: {model_name}")
        
    def _load_model(self) -> bool:
        """
        Load the NLLB model and tokenizer with caching to models/ directory.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self.model is not None and self.tokenizer is not None:
            return True
            
        try:
            print(f"📥 Loading NLLB model: {self.model_name}")
            print(f"💾 Models will be cached in: {self.models_dir.absolute()}")
            
            # Load tokenizer with caching
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=str(self.models_dir)
            )
            
            # Load model with caching and optimization
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                cache_dir=str(self.models_dir),
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            print(f"✅ NLLB model loaded successfully")
            print(f"🎯 Model device: {next(self.model.parameters()).device}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load NLLB model: {e}")
            return False
    
    def _get_device(self) -> str:
        """Get the device to use for inference."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Global language code or None if detection fails
        """
        try:
            # Use langdetect library (same as Google service for consistency)
            detected = langdetect.detect(text[:1000])  # Use first 1000 chars for detection
            return detected
        except Exception as e:
            print(f"⚠️ Language detection failed: {e}")
            return None
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto', filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text to target language with caching support.
        
        Args:
            text: Text to translate
            target_language: Target language code (global)
            source_language: Source language code (global, default: 'auto' for auto-detection)
            filename: Optional filename for caching
            
        Returns:
            Dict with translation result, confidence, and metadata
        """
        if not text.strip():
            return {"success": False, "error": "Empty text provided"}
        
        # Check if target language is supported
        if not LanguageMapping.is_language_supported(target_language, TranslationService.NLLB):
            return {"success": False, "error": f"Target language '{target_language}' not supported by NLLB"}
        
        # Check cache first if filename is provided
        cache_key = None
        if filename:
            cache_key = self._generate_cache_key(filename, text, target_language, source_language, "NLLB")
            cached_result = self._load_translation_cache(cache_key)
            if cached_result:
                cached_result["method"] = cached_result.get("method", "nllb") + "_cached"
                print("📋 Using cached NLLB translation")
                return cached_result
        
        # Detect source language if auto
        detected_lang = None
        if source_language == 'auto':
            detected_lang = self.detect_language(text)
            if detected_lang:
                source_language = detected_lang
            else:
                # Default to English if detection fails
                source_language = 'en'
        
        # If source and target are the same, return original text
        if source_language == target_language:
            result = {
                "success": True,
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "method": "no_translation_needed"
            }
            
            if filename and cache_key:
                self._save_translation_cache(cache_key, result)
            
            return result
        
        # Check if source language is supported
        if not LanguageMapping.is_language_supported(source_language, TranslationService.NLLB):
            return {"success": False, "error": f"Source language '{source_language}' not supported by NLLB"}
        
        # Load model if not already loaded
        if not self._load_model():
            return {"success": False, "error": "Failed to load NLLB model"}
        
        try:
            result = self._translate_with_nllb(text, target_language, source_language)
            
            if result["success"]:
                result["method"] = "nllb"
                
                # Save to cache if filename provided
                if filename and cache_key:
                    print(f"💾 Saving NLLB translation to cache: {cache_key}")
                    self._save_translation_cache(cache_key, result)
                
                return result
            else:
                return result
                
        except Exception as e:
            error_msg = f"NLLB translation failed: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _translate_with_nllb(self, text: str, target_lang: str, source_lang: str) -> Dict[str, Any]:
        """
        Translate using NLLB model.
        
        Args:
            text: Text to translate
            target_lang: Target language (global code)
            source_lang: Source language (global code)
            
        Returns:
            Translation result dictionary
        """
        try:
            # Convert global codes to NLLB codes
            nllb_source = LanguageMapping.get_service_code(source_lang, TranslationService.NLLB)
            nllb_target = LanguageMapping.get_service_code(target_lang, TranslationService.NLLB)
            
            if not nllb_source or not nllb_target:
                return {
                    "success": False,
                    "error": f"Language mapping failed: {source_lang} -> {nllb_source}, {target_lang} -> {nllb_target}"
                }
            
            print(f"🔄 Translating with NLLB: {source_lang} ({nllb_source}) -> {target_lang} ({nllb_target})")
            
            # Split text into chunks if it's too long
            chunks = self._split_text_for_translation(text)
            translated_chunks = []
            
            for chunk in chunks:
                # Set source language in tokenizer
                self.tokenizer.src_lang = nllb_source
                
                # Tokenize input
                inputs = self.tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=512)
                
                # Move inputs to the same device as model
                device = next(self.model.parameters()).device
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                # Generate translation
                with torch.no_grad():
                    translated_tokens = self.model.generate(
                        **inputs,
                        forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(nllb_target),
                        max_length=512,
                        num_beams=4,
                        no_repeat_ngram_size=2,
                        do_sample=False,
                        early_stopping=True
                    )
                
                # Decode translation
                translated_text = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
                translated_chunks.append(translated_text)
            
            # Join all chunks
            final_translation = ' '.join(translated_chunks)
            
            return {
                "success": True,
                "translated_text": final_translation,
                "source_language": source_lang,
                "target_language": target_lang,
                "nllb_source_code": nllb_source,
                "nllb_target_code": nllb_target
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"NLLB model translation failed: {e}"
            }
    
    def _split_text_for_translation(self, text: str, max_length: int = 400) -> List[str]:
        """
        Split text into chunks suitable for NLLB translation.
        
        Args:
            text: Text to split
            max_length: Maximum length per chunk
            
        Returns:
            List of text chunks
        """
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
    
    def _generate_cache_key(self, filename: str, text: str, target_lang: str, source_lang: str, service: str) -> str:
        """
        Generate cache key for translation.
        
        Args:
            filename: Original filename
            text: Text to translate
            target_lang: Target language
            source_lang: Source language
            service: Service name (NLLB)
            
        Returns:
            Cache key string
        """
        # Create a hash of the text content for uniqueness
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
        
        # Clean filename for cache key
        clean_filename = Path(filename).stem
        
        # Format: <filename>__<service>__<source_lang>__<target_lang>__<text_hash>
        cache_key = f"{clean_filename}__{service}__{source_lang}__{target_lang}__{text_hash}"
        
        return cache_key
    
    def _save_translation_cache(self, cache_key: str, translation_result: Dict[str, Any]) -> None:
        """Save translation result to cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(translation_result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save NLLB translation cache: {e}")
    
    def _load_translation_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load translation result from cache."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load NLLB translation cache: {e}")
        return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages for NLLB."""
        return LanguageMapping.get_supported_languages(TranslationService.NLLB)
    
    def is_translation_needed(self, text: str, target_language: str) -> bool:
        """Check if translation is needed based on detected language."""
        detected_lang = self.detect_language(text)
        return detected_lang != target_language if detected_lang else True
    
    def get_language_name(self, language_code: str) -> str:
        """Get full language name from language code."""
        return LanguageMapping.get_language_name(language_code)
    
    def validate_language_code(self, language_code: str) -> bool:
        """Validate if language code is supported by NLLB."""
        return LanguageMapping.is_language_supported(language_code, TranslationService.NLLB)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if self.model is None:
            return {"loaded": False}
        
        device = next(self.model.parameters()).device
        return {
            "loaded": True,
            "model_name": self.model_name,
            "device": str(device),
            "model_size": sum(p.numel() for p in self.model.parameters()),
            "cache_dir": str(self.models_dir.absolute())
        } 