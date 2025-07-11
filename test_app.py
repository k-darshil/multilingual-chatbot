#!/usr/bin/env python3
"""
Simple test script to verify the Gradio app starts without errors.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import gradio as gr
        print("✅ Gradio imported successfully")
        
        # Test our modules
        from src.config import Config
        print("✅ Config imported successfully")
        
        from src.document_processor import DocumentProcessor
        print("✅ DocumentProcessor imported successfully")
        
        from src.translation_service import TranslationService
        print("✅ TranslationService imported successfully")
        
        from src.rag_system import RAGSystem
        print("✅ RAGSystem imported successfully")
        
        # Test app import
        import app
        print("✅ App module imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        print("\nTesting configuration...")
        from src.config import Config
        
        # Test config validation
        is_valid, errors = Config.validate_config()
        
        if is_valid:
            print("✅ Configuration is valid")
        else:
            print("⚠️ Configuration issues found:")
            for error in errors:
                print(f"  • {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_interface_creation():
    """Test that the Gradio interface can be created."""
    try:
        print("\nTesting interface creation...")
        
        from app import create_interface
        
        # Create interface (but don't launch)
        interface = create_interface()
        
        print("✅ Gradio interface created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Interface creation error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Gradio App...\n")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_config():
        tests_passed += 1
    
    if test_interface_creation():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The app should start successfully.")
        print("\nTo run the app:")
        print("  python run_gradio_app.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 