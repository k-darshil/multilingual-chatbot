"""
Main Gradio application for the Multilingual Document Chatbot.
Provides a user-friendly interface for document upload, language selection, and Q&A.
"""

import gradio as gr
import sys
import os
from typing import List, Tuple, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.document_processor import DocumentProcessor
from src.translation_service import TranslationService
from src.rag_system import RAGSystem

# Global state for maintaining session
class AppState:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.translation_service = TranslationService()
        self.rag_system = RAGSystem()
        self.chat_history: List[Tuple[str, str]] = []
        self.current_document: Optional[Dict[str, Any]] = None
        self.document_indexed: bool = False
        self.selected_language: str = "en"

# Initialize global state
app_state = AppState()

def validate_configuration():
    """Validate configuration and return status message."""
    is_valid, errors = Config.validate_config()
    if not is_valid:
        error_msg = "❌ Configuration Issues:\n" + "\n".join([f"• {error}" for error in errors])
        error_msg += "\n\nPlease check your API keys in the .env file."
        return False, error_msg
    return True, "✅ Configuration is valid"

def get_language_options():
    """Get language options for dropdown."""
    language_options = Config.get_language_options()
    return [name for code, name in language_options]

def update_language(language_name: str) -> str:
    """Update selected language."""
    language_map = {name: code for code, name in Config.get_language_options()}
    app_state.selected_language = language_map.get(language_name, "en")
    return f"Language set to: {language_name}"

def process_document(uploaded_file):
    """Process uploaded document."""
    if uploaded_file is None:
        return "❌ No file uploaded", "No document loaded", "No document loaded"
    
    try:
        # Debug: Check what type of object we received
        print(f"🔍 Debug: Received file object type: {type(uploaded_file)}")
        print(f"🔍 Debug: File object attributes: {dir(uploaded_file)}")
        
        # Handle different types of file objects from Gradio
        if hasattr(uploaded_file, 'name'):
            file_path = uploaded_file.name
            print(f"🔍 Debug: Using file path from .name: {file_path}")
        elif isinstance(uploaded_file, str):
            file_path = uploaded_file
            print(f"🔍 Debug: File is already a string path: {file_path}")
        else:
            # Try to get the file path from common attributes
            for attr in ['path', 'file', 'filename']:
                if hasattr(uploaded_file, attr):
                    file_path = getattr(uploaded_file, attr)
                    print(f"🔍 Debug: Using file path from .{attr}: {file_path}")
                    break
            else:
                return "❌ Unable to extract file path from uploaded file", "No document loaded", "No document loaded"
        
        # Verify the file exists
        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}", "No document loaded", "No document loaded"
            
        print(f"📁 Processing file: {file_path}")
        
        # Create a mock uploaded file object for compatibility with DocumentProcessor
        class MockUploadedFile:
            def __init__(self, file_path):
                self.name = os.path.basename(file_path)
                with open(file_path, 'rb') as f:
                    self.content = f.read()
                self.size = len(self.content)
                self._position = 0
            
            def read(self):
                return self.content
            
            def seek(self, position):
                self._position = position
        
        mock_file = MockUploadedFile(file_path)
        print(f"✅ Created mock file object for: {mock_file.name}")
        
        # Validate file
        print("🔍 Starting file validation...")
        try:
            is_valid, error_message = app_state.document_processor.validate_file(mock_file)
            print(f"✅ File validation completed: {is_valid}")
        except Exception as e:
            print(f"❌ File validation failed: {e}")
            return f"❌ File validation error: {str(e)}", "No document loaded", "No document loaded"
        
        if not is_valid:
            return f"❌ {error_message}", "No document loaded", "No document loaded"
        
        # Process document
        print("🔍 Starting document processing...")
        try:
            result = app_state.document_processor.process_file(
                mock_file,
                target_language=app_state.selected_language,
                translation_service=app_state.translation_service
            )
            print(f"✅ Document processing completed: {result.get('success', False)}")
        except Exception as e:
            print(f"❌ Document processing failed: {e}")
            return f"❌ Document processing error: {str(e)}", "No document loaded", "No document loaded"
        
        if result["success"]:
            app_state.current_document = result
            print(f"✅ Document stored in app state")
            
            # Index document for RAG
            print("🔍 Starting RAG indexing...")
            try:
                index_result = app_state.rag_system.index_document(
                    result['text'], 
                    result
                )
                print(f"✅ RAG indexing completed: {index_result.get('success', False)}")
            except Exception as e:
                print(f"❌ RAG indexing failed: {e}")
                return f"❌ RAG indexing error: {str(e)}", "No document loaded", "No document loaded"
            
            if index_result["success"]:
                app_state.document_indexed = True
                app_state.chat_history = []  # Clear chat history for new document
                
                print("🔍 Creating success message...")
                try:
                    success_msg = f"✅ Document processed successfully!\n"
                    success_msg += f"📄 Extracted {result['word_count']:,} words from {result['pages']} page(s)\n"
                    success_msg += f"🔍 Indexed with {index_result['chunks_count']} chunks"
                    
                    # Document info
                    doc_info = f"**File:** {result.get('filename', 'Unknown')}\n"
                    doc_info += f"**Type:** {result.get('file_type', 'Unknown')}\n"
                    doc_info += f"**Size:** {result.get('file_size', 0) / 1024:.1f} KB\n"
                    doc_info += f"**Pages:** {result.get('pages', 'Unknown')}\n"
                    doc_info += f"**Words:** {result.get('word_count', 'Unknown'):,}\n"
                    
                    if result.get('detected_language'):
                        detected_lang_name = app_state.translation_service.get_language_name(result['detected_language'])
                        doc_info += f"**Original Language:** {detected_lang_name}\n"
                    
                    if result.get('translation_needed'):
                        target_lang_name = app_state.translation_service.get_language_name(result['target_language'])
                        if result.get('translation_success'):
                            doc_info += f"**Translated to:** {target_lang_name} ✅\n"
                        else:
                            doc_info += f"**Translation to {target_lang_name}:** Failed ❌\n"
                    
                    print("✅ Success message created, returning results...")
                    return success_msg, doc_info, "Ready to answer questions!"
                    
                except Exception as e:
                    print(f"❌ Error creating success message: {e}")
                    return f"❌ Error creating success message: {str(e)}", "No document loaded", "No document loaded"
            else:
                return f"⚠️ Document processed but indexing failed: {index_result.get('error', 'Unknown error')}", "No document loaded", "No document loaded"
        else:
            return f"❌ Processing failed: {result.get('error', 'Unknown error')}", "No document loaded", "No document loaded"
                
    except Exception as e:
        print(f"❌ Exception in process_document: {str(e)}")
        print(f"🔍 Debug: Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return f"❌ Error processing document: {str(e)}", "No document loaded", "No document loaded"

def clear_document():
    """Clear current document and reset state."""
    app_state.current_document = None
    app_state.document_indexed = False
    app_state.chat_history = []
    if app_state.rag_system.clear_collection():
        return "🗑️ Document cleared successfully!", "No document loaded", "No document loaded"
    return "❌ Failed to clear document", "No document loaded", "No document loaded"

def chat_with_document(message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Handle chat interaction with the document."""
    if not app_state.current_document:
        new_history = history + [(message, "❌ Please upload a document first.")]
        return new_history, ""
    
    if not message.strip():
        return history, ""
    
    try:
        # Generate answer using RAG system
        answer_result = app_state.rag_system.ask_question(
            message, 
            app_state.selected_language
        )
        
        if answer_result["success"]:
            answer = answer_result["answer"]
            
            # Format sources information
            sources_info = ""
            if "sources" in answer_result and answer_result["sources"]:
                sources_info = "\n\n📚 **Sources:**\n"
                for i, source in enumerate(answer_result["sources"][:3]):
                    sources_info += f"**Source {i+1}:** {source.get('filename', 'Unknown')} "
                    sources_info += f"(Similarity: {source.get('similarity_score', 0):.2f})\n"
                    sources_info += f"Preview: {source.get('preview', 'No preview')}\n\n"
            
            full_answer = answer + sources_info
            
            # Add to app state chat history for persistence
            app_state.chat_history.append((message, full_answer))
            
            # Return updated history
            new_history = history + [(message, full_answer)]
            return new_history, ""
        else:
            error_msg = f"❌ {answer_result.get('error', 'Failed to generate answer')}"
            new_history = history + [(message, error_msg)]
            return new_history, ""
            
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        new_history = history + [(message, error_msg)]
        return new_history, ""

def create_interface():
    """Create the Gradio interface."""
    
    # Simple CSS for styling
    css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    """
    
    with gr.Blocks(
        title="Multilingual Document Chatbot",
        css=css
    ) as interface:
        
        # Header
        gr.HTML('<div class="main-header">🤖 Multilingual Document Chatbot</div>')
        gr.HTML('<div style="text-align: center; margin-bottom: 2rem;">Upload documents in any language and ask questions in your preferred language</div>')
        
        # Configuration status
        config_valid, config_msg = validate_configuration()
        if not config_valid:
            gr.HTML(f'<div style="background-color: #ffebee; padding: 1rem; border-radius: 8px; border: 1px solid #f44336; margin: 1rem 0; color: #c62828;">{config_msg}</div>')
        
        with gr.Row():
            # Left column - Document upload and settings
            with gr.Column(scale=1):
                gr.HTML('<h3>⚙️ Settings & Document Upload</h3>')
                
                # Language selection
                language_dropdown = gr.Dropdown(
                    choices=get_language_options(),
                    value="English",
                    label="🌍 Response Language"
                )
                
                language_status = gr.Textbox(
                    value="Language set to: English",
                    label="Language Status",
                    interactive=False
                )
                
                # Document upload
                gr.HTML('<h4>📁 Upload Document</h4>')
                file_upload = gr.File(
                    label="Choose a document",
                    file_types=[".pdf", ".docx", ".txt", ".doc"]
                )
                
                upload_status = gr.Textbox(
                    label="Upload Status",
                    interactive=False,
                    lines=3
                )
                
                # Document info
                document_info = gr.Textbox(
                    label="📄 Document Information",
                    interactive=False,
                    lines=8,
                    value="No document loaded"
                )
                
                # Chat status
                chat_status = gr.Textbox(
                    label="💬 Chat Status",
                    interactive=False,
                    value="No document loaded"
                )
                
                # Clear document button
                clear_btn = gr.Button("🗑️ Clear Document")
                
            # Right column - Chat interface
            with gr.Column(scale=2):
                gr.HTML('<h3>💬 Ask Questions About Your Document</h3>')
                
                # Chat interface
                chatbot = gr.Chatbot(
                    height=500,
                    label="Conversation"
                )
                
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask a question about your document...",
                    lines=2
                )
                
                submit_btn = gr.Button("Send", variant="primary")
                
        # Event handlers
        language_dropdown.change(
            fn=update_language,
            inputs=[language_dropdown],
            outputs=[language_status]
        )
        
        file_upload.change(
            fn=process_document,
            inputs=[file_upload],
            outputs=[upload_status, document_info, chat_status]
        )
        
        clear_btn.click(
            fn=clear_document,
            outputs=[upload_status, document_info, chat_status]
        )
        
        # Chat event handlers
        submit_btn.click(
            fn=chat_with_document,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            fn=chat_with_document,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
    return interface

def main():
    """Main application function."""
    interface = create_interface()
    
    # Get environment variables with proper defaults
    share_app = os.getenv("GRADIO_SHARE", "false").lower() in ["true", "1", "yes"]
    
    print(f"🚀 Starting Multilingual Document Chatbot...")
    print(f"📡 Share mode: {'Enabled' if share_app else 'Disabled'}")
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0" if share_app else "127.0.0.1",
        server_port=7860,
        share=share_app,
        show_error=True,
        inbrowser=not share_app,  # Don't auto-open browser if sharing publicly
        debug=True
    )

if __name__ == "__main__":
    main() 