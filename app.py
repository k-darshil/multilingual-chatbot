"""
Main Gradio application for the Multilingual Document Chatbot.
Provides a user-friendly interface for document upload, language selection, and Q&A.
"""

import gradio as gr
import sys
import os
from typing import List, Tuple, Optional, Dict, Any

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
        self.chat_history: List[Tuple] = []
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
        error_msg += "\n\nPlease check your API keys in the secrets.toml file or environment variables."
        return False, error_msg
    return True, "✅ Configuration is valid"

def get_language_options():
    """Get language options for dropdown."""
    language_options = Config.get_language_options()
    return {name: code for code, name in language_options}

def update_language(language_name):
    """Update selected language."""
    language_options = get_language_options()
    app_state.selected_language = language_options.get(language_name, "en")
    return f"Language set to: {language_name}"

def process_document(file_path):
    """Process uploaded document."""
    if file_path is None:
        return "❌ No file uploaded", "", ""
    
    try:
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
        
        # Validate file
        is_valid, error_message = app_state.document_processor.validate_file(mock_file)
        
        if not is_valid:
            return f"❌ {error_message}", "", ""
        
        # Process document
        result = app_state.document_processor.process_file(
            mock_file,
            target_language=app_state.selected_language,
            translation_service=app_state.translation_service
        )
        
        if result["success"]:
            app_state.current_document = result
            
            # Index document for RAG
            index_result = app_state.rag_system.index_document(
                result['text'], 
                result
            )
            
            if index_result["success"]:
                app_state.document_indexed = True
                app_state.chat_history = []  # Clear chat history for new document
                
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
                
                # Collection stats
                stats = app_state.rag_system.get_collection_stats()
                if "total_chunks" in stats:
                    doc_info += f"\n**Vector Database:**\n"
                    doc_info += f"Chunks stored: {stats['total_chunks']}\n"
                    doc_info += f"Embedding model: {stats.get('embedding_model', 'Unknown')}"
                
                return success_msg, doc_info, "Ready to answer questions!"
            else:
                return f"⚠️ Document processed but indexing failed: {index_result.get('error', 'Unknown error')}", "", ""
        else:
            return f"❌ Processing failed: {result.get('error', 'Unknown error')}", "", ""
                
    except Exception as e:
        return f"❌ Error processing document: {str(e)}", "", ""

def clear_document():
    """Clear current document and reset state."""
    app_state.current_document = None
    app_state.document_indexed = False
    app_state.chat_history = []
    if app_state.rag_system.clear_collection():
        return "🗑️ Document cleared successfully!", "", "No document loaded"
    return "❌ Failed to clear document", "", "No document loaded"

def chat_with_document(message, history):
    """Handle chat interaction with the document."""
    if not app_state.current_document:
        return history + [("❌ Please upload a document first.", None)], ""
    
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
            app_state.chat_history.append((message, full_answer, answer_result))
            
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
    
    # Custom CSS for dark theme and styling
    css = """
    .gradio-container {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    .dark {
        background-color: #1a1a1a !important;
    }
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #cccccc;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #444;
        margin: 0.5rem 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4caf50;
        background-color: #2a2a2a;
    }
    """
    
    with gr.Blocks(
        title="Multilingual Document Chatbot",
        theme=gr.themes.Base().set(
            body_background_fill="#1a1a1a",
            body_text_color="#ffffff",
            background_fill_primary="#2a2a2a",
            background_fill_secondary="#1a1a1a",
            border_color_primary="#444444",
            color_accent="#FF6B6B",
            color_accent_soft="#FF6B6B",
        ),
        css=css
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">🤖 Multilingual Document Chatbot</div>
        <div class="sub-header">Upload documents in any language and ask questions in your preferred language</div>
        """)
        
        # Configuration status
        config_valid, config_msg = validate_configuration()
        if not config_valid:
            gr.HTML(f'<div style="background-color: #f8d7da; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc3545; margin: 1rem 0; color: #721c24;">{config_msg}</div>')
        
        with gr.Row():
            # Left column - Document upload and settings
            with gr.Column(scale=1):
                gr.HTML('<div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">⚙️ Settings & Document Upload</div>')
                
                # Language selection
                language_options = get_language_options()
                language_dropdown = gr.Dropdown(
                    choices=list(language_options.keys()),
                    value="English",
                    label="🌍 Response Language",
                    info="Choose your preferred language for responses"
                )
                
                language_status = gr.Textbox(
                    value="Language set to: English",
                    label="Language Status",
                    interactive=False
                )
                
                # Document upload
                gr.HTML('<div style="font-size: 1.1rem; font-weight: bold; margin: 1rem 0;">📁 Upload Document</div>')
                file_upload = gr.File(
                    label="Choose a document",
                    file_types=[".pdf", ".docx", ".txt", ".doc"],
                    type="filepath"
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
                    placeholder="No document loaded"
                )
                
                # Chat status
                chat_status = gr.Textbox(
                    label="💬 Chat Status",
                    interactive=False,
                    value="No document loaded"
                )
                
                # Clear document button
                clear_btn = gr.Button("🗑️ Clear Document", variant="secondary")
                
                # Features information
                gr.HTML("""
                <div style="margin-top: 2rem;">
                    <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 1rem;">🚀 Features</div>
                    <div class="feature-box">
                        <strong>📄 Document Processing</strong><br>
                        • PDF, DOCX, TXT support<br>
                        • Text extraction with multiple fallbacks<br>
                        • Document chunking for better search
                    </div>
                    <div class="feature-box">
                        <strong>🌍 Multilingual Support</strong><br>
                        • 20+ supported languages<br>
                        • Automatic language detection<br>
                        • Real-time translation
                    </div>
                    <div class="feature-box">
                        <strong>🤖 AI-Powered Q&A</strong><br>
                        • RAG-based question answering<br>
                        • Context-aware responses<br>
                        • Source attribution
                    </div>
                </div>
                """)
            
            # Right column - Chat interface
            with gr.Column(scale=2):
                gr.HTML('<div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">💬 Ask Questions About Your Document</div>')
                
                # Chat interface
                chatbot = gr.Chatbot(
                    height=500,
                    label="Conversation",
                    show_label=True,
                    container=True,
                    bubble_full_width=False
                )
                
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask a question about your document...",
                    lines=2,
                    max_lines=5
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
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; border-top: 1px solid #444; color: #888;">
            <em>Multilingual Document Understanding</em>
        </div>
        """)
    
    return interface

def main():
    """Main application function."""
    interface = create_interface()
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True,
        favicon_path=None,
        app_kwargs={"docs_url": None, "redoc_url": None}
    )

if __name__ == "__main__":
    main() 