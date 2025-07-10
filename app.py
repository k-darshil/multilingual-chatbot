"""
Main Streamlit application for the Multilingual Document Chatbot.
Provides a user-friendly interface for document upload, language selection, and Q&A.
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.document_processor import DocumentProcessor
from src.translation_service import TranslationService
from src.rag_system import RAGSystem

# Page configuration
st.set_page_config(
    page_title="Multilingual Document Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .document-info {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    
    if 'translation_service' not in st.session_state:
        st.session_state.translation_service = TranslationService()
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGSystem()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    
    if 'document_indexed' not in st.session_state:
        st.session_state.document_indexed = False

def display_header():
    """Display the main header and description."""
    st.markdown('<h1 class="main-header">🤖 Multilingual Document Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload documents in any language and ask questions in your preferred language</p>', unsafe_allow_html=True)
    
    # Configuration validation
    is_valid, errors = Config.validate_config()
    if not is_valid:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.error("Configuration Issues:")
        for error in errors:
            st.write(f"❌ {error}")
        st.write("Please check your API keys in the secrets.toml file or environment variables.")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    
    return True

def display_sidebar():
    """Display the sidebar with settings and document info."""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Language selection
        st.markdown("### 🌍 Response Language")
        language_options = Config.get_language_options()
        selected_language = st.selectbox(
            "Choose your preferred language:",
            options=[code for code, name in language_options],
            format_func=lambda x: next(name for code, name in language_options if code == x),
            index=0  # Default to English
        )
        st.session_state.selected_language = selected_language
        
        # Document information
        if st.session_state.current_document:
            st.markdown("### 📄 Current Document")
            st.markdown('<div class="document-info">', unsafe_allow_html=True)
            doc = st.session_state.current_document
            st.write(f"**File:** {doc.get('filename', 'Unknown')}")
            st.write(f"**Type:** {doc.get('file_type', 'Unknown')}")
            st.write(f"**Size:** {doc.get('file_size', 0) / 1024:.1f} KB")
            st.write(f"**Pages:** {doc.get('pages', 'Unknown')}")
            st.write(f"**Words:** {doc.get('word_count', 'Unknown'):,}")
            
            # Language information
            if doc.get('detected_language'):
                detected_lang_name = st.session_state.translation_service.get_language_name(doc['detected_language'])
                st.write(f"**Original Language:** {detected_lang_name}")
            
            if doc.get('translation_needed'):
                target_lang_name = st.session_state.translation_service.get_language_name(doc['target_language'])
                if doc.get('translation_success'):
                    st.write(f"**Translated to:** {target_lang_name} ✅")
                else:
                    st.write(f"**Translation to {target_lang_name}:** Failed ❌")
                    if doc.get('translation_error'):
                        st.write(f"*Error: {doc['translation_error'][:50]}...*")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear document button
            if st.button("🗑️ Clear Document"):
                st.session_state.current_document = None
                st.session_state.document_indexed = False
                st.session_state.chat_history = []
                if st.session_state.rag_system.clear_collection():
                    st.success("Document cleared successfully!")
                st.rerun()
        
        # Collection stats
        if st.session_state.rag_system:
            stats = st.session_state.rag_system.get_collection_stats()
            if "total_chunks" in stats:
                st.markdown("### 📊 Vector Database")
                st.write(f"**Chunks stored:** {stats['total_chunks']}")
                st.write(f"**Embedding model:** {stats.get('embedding_model', 'Unknown')}")

def upload_document():
    """Handle document upload and processing."""
    st.markdown("## 📁 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt', 'doc'],
        help="Supported formats: PDF, DOCX, TXT, DOC (Max 50MB)"
    )
    
    if uploaded_file is not None:
        # Validate file
        is_valid, error_message = st.session_state.document_processor.validate_file(uploaded_file)
        
        if not is_valid:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ {error_message}")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Process document
        with st.spinner("Processing document..."):
            result = st.session_state.document_processor.process_file(
                uploaded_file, 
                target_language=st.session_state.selected_language,
                translation_service=st.session_state.translation_service
            )
        
        if result["success"]:
            st.session_state.current_document = result
            st.markdown('<div class="document-info">', unsafe_allow_html=True)
            st.success("✅ Document processed successfully!")
            st.write(f"**Extracted {result['word_count']:,} words** from {result['pages']} page(s)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Index document for RAG
            with st.spinner("Indexing document for search..."):
                index_result = st.session_state.rag_system.index_document(
                    result['text'], 
                    result
                )
            
            if index_result["success"]:
                st.session_state.document_indexed = True
                st.success(f"✅ Document indexed with {index_result['chunks_count']} chunks")
            else:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.warning(f"⚠️ Indexing failed: {index_result.get('error', 'Unknown error')}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            st.markdown('</div>', unsafe_allow_html=True)

def display_chat_interface():
    """Display the chat interface for Q&A."""
    if not st.session_state.current_document:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.info("👆 Please upload a document first to start asking questions.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown("## 💬 Ask Questions About Your Document")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📝 Conversation History")
        for i, (question, answer, metadata) in enumerate(st.session_state.chat_history):
            # User question
            st.markdown('<div class="chat-message user-message">', unsafe_allow_html=True)
            st.markdown(f"**You:** {question}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Assistant answer
            st.markdown('<div class="chat-message assistant-message">', unsafe_allow_html=True)
            st.markdown(f"**Assistant:** {answer}")
            
            # Show metadata if available
            if metadata and "sources" in metadata:
                with st.expander("📚 Sources", expanded=False):
                    for j, source in enumerate(metadata["sources"][:3]):  # Show top 3 sources
                        st.write(f"**Source {j+1}:** {source.get('filename', 'Unknown')}")
                        st.write(f"*Similarity: {source.get('similarity_score', 0):.2f}*")
                        st.write(f"Preview: {source.get('preview', 'No preview')}")
                        st.write("---")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Question input
    question = st.chat_input(
        "Ask a question about your document...",
        key="question_input"
    )
    
    if question:
        # Add user question to chat
        st.markdown('<div class="chat-message user-message">', unsafe_allow_html=True)
        st.markdown(f"**You:** {question}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate answer
        with st.spinner("Thinking..."):
            answer_result = st.session_state.rag_system.ask_question(
                question, 
                st.session_state.selected_language
            )
        
        if answer_result["success"]:
            answer = answer_result["answer"]
            
            # Display answer
            st.markdown('<div class="chat-message assistant-message">', unsafe_allow_html=True)
            st.markdown(f"**Assistant:** {answer}")
            
            # Show sources
            if "sources" in answer_result:
                with st.expander("📚 Sources", expanded=False):
                    for i, source in enumerate(answer_result["sources"][:3]):
                        st.write(f"**Source {i+1}:** {source.get('filename', 'Unknown')}")
                        st.write(f"*Similarity: {source.get('similarity_score', 0):.2f}*")
                        st.write(f"Preview: {source.get('preview', 'No preview')}")
                        st.write("---")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append((question, answer, answer_result))
        
        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ {answer_result.get('error', 'Failed to generate answer')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Rerun to update the interface
        st.rerun()

def display_features():
    """Display feature information."""
    with st.expander("🚀 Features", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📄 Document Processing")
            st.write("- PDF, DOCX, TXT support")
            st.write("- Text extraction with multiple fallbacks")
            st.write("- Document chunking for better search")
        
        with col2:
            st.markdown("### 🌍 Multilingual Support")
            st.write("- 20+ supported languages")
            st.write("- Automatic language detection")
            st.write("- Real-time translation")
        
        with col3:
            st.markdown("### 🤖 AI-Powered Q&A")
            st.write("- RAG-based question answering")
            st.write("- Context-aware responses")
            st.write("- Source attribution")

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header and check configuration
    if not display_header():
        return
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        upload_document()
        display_features()
    
    with col2:
        display_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("*Multilingual Document Understanding*")

if __name__ == "__main__":
    main() 