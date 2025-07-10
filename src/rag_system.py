"""
RAG (Retrieval-Augmented Generation) system for the multilingual document chatbot.
Handles document indexing, retrieval, and answer generation using OpenAI and vector databases.
"""

# import streamlit as st  # Removed for Gradio compatibility
import openai
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid
import tiktoken
from src.config import Config
from src.translation_service import TranslationService

class RAGSystem:
    """RAG system for document question answering with multilingual support."""
    
    def __init__(self):
        self.openai_client = None
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.translation_service = TranslationService()
        
        # Initialize OpenAI client
        if Config.OPENAI_API_KEY:
            try:
                openai.api_key = Config.OPENAI_API_KEY
                self.openai_client = openai
            except Exception as e:
                st.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            st.error(f"Failed to load embedding model: {e}")
        
        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.Client(Settings(
                persist_directory="./chroma_db",
                allow_reset=True
            ))
            self.collection = self.chroma_client.get_or_create_collection(
                name="document_chunks",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            st.warning(f"Failed to initialize ChromaDB: {e}")
    
    def index_document(self, document_text: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index a document by chunking and storing in vector database.
        
        Args:
            document_text: Full text of the document
            document_info: Document metadata
            
        Returns:
            Indexing result with chunk count and status
        """
        try:
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            # Chunk the document
            chunks = self._chunk_text(document_text)
            
            if not chunks:
                return {"success": False, "error": "No chunks generated from document"}
            
            # Generate embeddings for chunks
            embeddings = []
            chunk_metadata = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                try:
                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk).tolist()
                    embeddings.append(embedding)
                    
                    # Create chunk metadata
                    metadata = {
                        "document_id": doc_id,
                        "chunk_index": i,
                        "filename": document_info.get("filename", "unknown"),
                        "file_type": document_info.get("file_type", "unknown"),
                        "chunk_length": len(chunk),
                        "word_count": len(chunk.split())
                    }
                    chunk_metadata.append(metadata)
                    
                    # Generate chunk ID
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_ids.append(chunk_id)
                    
                except Exception as e:
                    st.warning(f"Failed to process chunk {i}: {e}")
                    continue
            
            if not embeddings:
                return {"success": False, "error": "No embeddings generated"}
            
            # Store in ChromaDB
            if self.collection:
                try:
                    self.collection.add(
                        embeddings=embeddings,
                        documents=chunks,
                        metadatas=chunk_metadata,
                        ids=chunk_ids
                    )
                except Exception as e:
                    st.warning(f"Failed to store in ChromaDB: {e}")
            
            return {
                "success": True,
                "document_id": doc_id,
                "chunks_count": len(chunks),
                "embeddings_count": len(embeddings),
                "storage_method": "chromadb" if self.collection else "memory"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Document indexing failed: {e}"}
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a given query.
        
        Args:
            query: User question
            top_k: Number of top chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        try:
            if not self.collection or not self.embedding_model:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            relevant_chunks = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    chunk_data = {
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "chunk_index": i
                    }
                    relevant_chunks.append(chunk_data)
            
            return relevant_chunks
            
        except Exception as e:
            st.warning(f"Retrieval failed: {e}")
            return []
    
    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]], 
                       target_language: str = 'en') -> Dict[str, Any]:
        """
        Generate an answer using OpenAI GPT with retrieved context.
        
        Args:
            query: User question
            context_chunks: Retrieved relevant chunks
            target_language: Language for the response
            
        Returns:
            Generated answer with metadata
        """
        try:
            if not self.openai_client:
                return {"success": False, "error": "OpenAI client not available"}
            
            # Prepare context from chunks
            context_text = self._prepare_context(context_chunks)
            
            # Create prompt
            prompt = self._create_prompt(query, context_text, target_language)
            
            # Call OpenAI API
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(target_language)
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Calculate token usage
            tokens_used = response.usage.total_tokens
            
            return {
                "success": True,
                "answer": answer,
                "context_chunks_used": len(context_chunks),
                "tokens_used": tokens_used,
                "model_used": "gpt-3.5-turbo",
                "target_language": target_language
            }
            
        except Exception as e:
            return {"success": False, "error": f"Answer generation failed: {e}"}
    
    def ask_question(self, query: str, target_language: str = 'en') -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve relevant chunks and generate answer.
        
        Args:
            query: User question
            target_language: Language for the response
            
        Returns:
            Complete response with answer, sources, and metadata
        """
        try:
            # Step 1: Retrieve relevant chunks
            relevant_chunks = self.retrieve_relevant_chunks(query, top_k=5)
            
            if not relevant_chunks:
                return {
                    "success": False,
                    "error": "No relevant information found in the document",
                    "answer": "I couldn't find relevant information in the uploaded document to answer your question."
                }
            
            # Step 2: Generate answer
            answer_result = self.generate_answer(query, relevant_chunks, target_language)
            
            if not answer_result["success"]:
                return answer_result
            
            # Step 3: Prepare response with sources
            sources = []
            for chunk in relevant_chunks:
                source_info = {
                    "filename": chunk["metadata"].get("filename", "Unknown"),
                    "chunk_index": chunk["metadata"].get("chunk_index", 0),
                    "similarity_score": chunk["similarity_score"],
                    "preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
                }
                sources.append(source_info)
            
            return {
                "success": True,
                "answer": answer_result["answer"],
                "sources": sources,
                "metadata": {
                    "chunks_retrieved": len(relevant_chunks),
                    "tokens_used": answer_result.get("tokens_used", 0),
                    "model_used": answer_result.get("model_used", "unknown"),
                    "target_language": target_language
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Question answering failed: {e}"}
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                for i in range(end - 100, end):
                    if i > start and text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + 1, end - overlap)
            
            if start >= len(text):
                break
        
        return chunks
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text from retrieved chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            context_parts.append(f"Context {i+1}:\n{chunk['text']}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, target_language: str) -> str:
        """Create prompt for answer generation."""
        language_name = Config.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        prompt = f"""Based on the following context from the uploaded document, please answer the user's question in {language_name}.

Context:
{context}

Question: {query}

Instructions:
1. Answer based only on the information provided in the context
2. If the context doesn't contain enough information, say so clearly
3. Respond in {language_name}
4. Be precise and helpful
5. Include relevant details from the context

Answer:"""
        
        return prompt
    
    def _get_system_prompt(self, target_language: str) -> str:
        """Get system prompt for the chatbot."""
        language_name = Config.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        return f"""You are a helpful multilingual document assistant. Your task is to answer questions about uploaded documents accurately and clearly in {language_name}.

Key guidelines:
- Answer based only on the provided document context
- Be accurate and precise
- If information is not in the document, clearly state that
- Respond in {language_name}
- Be helpful and professional
- Cite specific parts of the document when relevant"""
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current document collection."""
        try:
            if not self.collection:
                return {"error": "No collection available"}
            
            count = self.collection.count()
            
            return {
                "total_chunks": count,
                "collection_name": "document_chunks",
                "embedding_model": "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            return {"error": f"Failed to get collection stats: {e}"}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            if self.collection:
                # Delete and recreate collection
                self.chroma_client.delete_collection("document_chunks")
                self.collection = self.chroma_client.create_collection(
                    name="document_chunks",
                    metadata={"hnsw:space": "cosine"}
                )
                return True
        except Exception as e:
            st.error(f"Failed to clear collection: {e}")
        return False
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimation
            return len(text.split()) * 1.3 