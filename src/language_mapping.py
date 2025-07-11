"""
Language mapping system for the Multilingual Document Chatbot.
Maps between global language codes, Google Cloud codes, and NLLB codes.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum

class TranslationService(Enum):
    GOOGLE_CLOUD = "google_cloud"
    NLLB = "nllb"

class LanguageMapping:
    """
    Global language mapping system that handles different language codes 
    for different translation services.
    """
    
    # NLLB supported languages (from user specification)
    NLLB_SUPPORTED = {
        'en': 'eng_Latn',    # English
        'hi': 'hin_Deva',    # Hindi
        'es': 'spa_Latn',    # Spanish
        'fr': 'fra_Latn',    # French
        'ta': 'tam_Taml',    # Tamil
        'ar': 'arb_Arab',    # Arabic
    }
    
    # Google Cloud to Global mapping (inverse will be computed)
    GOOGLE_TO_GLOBAL = {
        'en': 'en',          # English
        'es': 'es',          # Spanish
        'fr': 'fr',          # French
        'de': 'de',          # German
        'it': 'it',          # Italian
        'pt': 'pt',          # Portuguese
        'ru': 'ru',          # Russian
        'ja': 'ja',          # Japanese
        'ko': 'ko',          # Korean
        'zh': 'zh',          # Chinese (Simplified)
        'ar': 'ar',          # Arabic
        'hi': 'hi',          # Hindi
        'ur': 'ur',          # Urdu
        'bn': 'bn',          # Bengali
        'ta': 'ta',          # Tamil
        'te': 'te',          # Telugu
        'mr': 'mr',          # Marathi
        'gu': 'gu',          # Gujarati
        'kn': 'kn',          # Kannada
        'ml': 'ml',          # Malayalam
        'pa': 'pa',          # Punjabi
    }
    
    # Language names for display
    LANGUAGE_NAMES = {
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
        'pa': 'Punjabi',
    }

    @classmethod
    def get_supported_languages(cls, service: TranslationService) -> Dict[str, str]:
        """
        Get supported languages for a specific service.
        
        Args:
            service: Translation service enum
            
        Returns:
            Dict mapping global language codes to language names
        """
        if service == TranslationService.GOOGLE_CLOUD:
            return {code: cls.LANGUAGE_NAMES[code] for code in cls.GOOGLE_TO_GLOBAL.values()}
        elif service == TranslationService.NLLB:
            return {code: cls.LANGUAGE_NAMES[code] for code in cls.NLLB_SUPPORTED.keys()}
        else:
            return {}

    @classmethod
    def get_service_code(cls, global_code: str, service: TranslationService) -> Optional[str]:
        """
        Convert global language code to service-specific code.
        
        Args:
            global_code: Global language code (e.g., 'en', 'fr')
            service: Translation service enum
            
        Returns:
            Service-specific language code or None if not supported
        """
        if service == TranslationService.GOOGLE_CLOUD:
            # For Google Cloud, the codes are the same as global codes
            return global_code if global_code in cls.GOOGLE_TO_GLOBAL.values() else None
        elif service == TranslationService.NLLB:
            return cls.NLLB_SUPPORTED.get(global_code)
        else:
            return None

    @classmethod
    def get_global_code(cls, service_code: str, service: TranslationService) -> Optional[str]:
        """
        Convert service-specific code to global language code.
        
        Args:
            service_code: Service-specific language code
            service: Translation service enum
            
        Returns:
            Global language code or None if not found
        """
        if service == TranslationService.GOOGLE_CLOUD:
            # For Google Cloud, the codes are the same as global codes
            return service_code if service_code in cls.GOOGLE_TO_GLOBAL.values() else None
        elif service == TranslationService.NLLB:
            # Reverse lookup for NLLB
            for global_code, nllb_code in cls.NLLB_SUPPORTED.items():
                if nllb_code == service_code:
                    return global_code
            return None
        else:
            return None

    @classmethod
    def is_language_supported(cls, global_code: str, service: TranslationService) -> bool:
        """
        Check if a language is supported by a specific service.
        
        Args:
            global_code: Global language code
            service: Translation service enum
            
        Returns:
            True if language is supported, False otherwise
        """
        return cls.get_service_code(global_code, service) is not None

    @classmethod
    def get_language_name(cls, global_code: str) -> str:
        """
        Get the display name for a language code.
        
        Args:
            global_code: Global language code
            
        Returns:
            Language display name or the code itself if not found
        """
        return cls.LANGUAGE_NAMES.get(global_code, global_code.upper())

    @classmethod
    def get_language_options_for_service(cls, service: TranslationService) -> List[Tuple[str, str]]:
        """
        Get language options for UI selection for a specific service.
        
        Args:
            service: Translation service enum
            
        Returns:
            List of (global_code, display_name) tuples
        """
        supported_languages = cls.get_supported_languages(service)
        return [(code, name) for code, name in supported_languages.items()]

    @classmethod
    def get_common_languages(cls) -> List[str]:
        """
        Get languages supported by both services.
        
        Returns:
            List of global language codes supported by both services
        """
        google_codes = set(cls.GOOGLE_TO_GLOBAL.values())
        nllb_codes = set(cls.NLLB_SUPPORTED.keys())
        return list(google_codes.intersection(nllb_codes))

    @classmethod
    def get_service_display_name(cls, service: TranslationService) -> str:
        """
        Get display name for translation service.
        
        Args:
            service: Translation service enum
            
        Returns:
            Display name for the service
        """
        service_names = {
            TranslationService.GOOGLE_CLOUD: "Google Cloud Translate",
            TranslationService.NLLB: "NLLB (Open Source)"
        }
        return service_names.get(service, str(service)) 