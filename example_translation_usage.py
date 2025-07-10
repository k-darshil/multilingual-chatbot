#!/usr/bin/env python3
"""
Example usage of the TranslationService with Google Cloud service account authentication.

Before running this script, configure your secrets.toml:

Option 1 - Service Account JSON (Recommended):
[secrets]
GOOGLE_TRANSLATE_API_KEY = '{"type": "service_account", "project_id": "your-project", "private_key_id": "...", "private_key": "...", "client_email": "...", "client_id": "...", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token"}'
GOOGLE_PROJECT_ID = "your-project-id"

Option 2 - Service Account File Path:
[secrets]
GOOGLE_TRANSLATE_API_KEY = "/path/to/your/service-account.json"
GOOGLE_PROJECT_ID = "your-project-id"

Option 3 - Application Default Credentials:
Run: gcloud auth application-default login
Then just set:
[secrets]
GOOGLE_PROJECT_ID = "your-project-id"
"""

import sys
sys.path.append('.')

try:
    from src.translation_service import TranslationService
    
    print("🚀 Testing Google Cloud Translation API v3 with Service Account Authentication")
    print("=" * 70)
    
    # Initialize the translation service
    translator = TranslationService()
    
    if translator.translate_client:
        print("✅ Translation service initialized successfully!")
        
        # Test connection
        connection_test = translator.test_connection()
        if connection_test["success"]:
            print("✅ Connection test passed!")
            print(f"   Test translation: '{connection_test['test_translation']['original']}' → '{connection_test['test_translation']['translated']}'")
        else:
            print(f"❌ Connection test failed: {connection_test['error']}")
            exit(1)
        
        # Example translations with caching
        print("\n📝 Example Translations:")
        print("-" * 40)
        
        examples = [
            ("Hello, world!", "es", "example1.txt"),
            ("How are you today?", "fr", "example2.txt"),
            ("Good morning!", "de", "example3.txt"),
            ("Thank you very much!", "ja", "example4.txt")
        ]
        
        for text, target_lang, filename in examples:
            print(f"\nTranslating: '{text}' → {target_lang}")
            
            result = translator.translate_text(
                text=text,
                target_language=target_lang,
                filename=filename
            )
            
            if result["success"]:
                print(f"  ✓ Result: '{result['translated_text']}'")
                print(f"  ✓ Method: {result['method']}")
                print(f"  ✓ Source: {result['source_language']} → Target: {result['target_language']}")
            else:
                print(f"  ❌ Error: {result['error']}")
        
        # Test caching by repeating first translation
        print(f"\n🔄 Testing cache with repeat translation:")
        print("-" * 40)
        
        repeat_result = translator.translate_text(
            text="Hello, world!",
            target_language="es",
            filename="example1.txt"
        )
        
        if repeat_result["success"]:
            print(f"  ✓ Cached result: '{repeat_result['translated_text']}'")
            print(f"  ✓ Method: {repeat_result['method']}")
            print(f"  ✓ Cache working: {'cached' in repeat_result['method']}")
        
        # Show cache statistics
        cache_stats = translator.get_cache_stats()
        if cache_stats["success"]:
            print(f"\n📊 Cache Statistics:")
            print("-" * 40)
            print(f"  Cache files: {cache_stats['total_files']}")
            print(f"  Cache size: {cache_stats['total_size_mb']} MB")
            print(f"  Cache directory: {cache_stats['cache_directory']}")
        
        print("\n🎉 All tests completed successfully!")
        
    else:
        print("❌ Translation service failed to initialize.")
        print("Please check your secrets.toml configuration:")
        print("""
Option 1 - Service Account JSON:
[secrets]
GOOGLE_TRANSLATE_API_KEY = '{"type": "service_account", ...}'
GOOGLE_PROJECT_ID = "your-project-id"

Option 2 - Service Account File:
[secrets]  
GOOGLE_TRANSLATE_API_KEY = "/path/to/service-account.json"
GOOGLE_PROJECT_ID = "your-project-id"

Option 3 - Application Default Credentials:
Run: gcloud auth application-default login
        """)
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Run: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 