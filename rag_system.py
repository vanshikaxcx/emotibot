"""
RAG (Retrieval-Augmented Generation) system for EmotiBot
Manages document storage, retrieval, and context generation
"""
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Optional, Tuple
import uuid
import json
import os
from datetime import datetime
import logging
from document_processor import DocumentProcessor
from config import Config

class RAGSystem:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        
        # Initialize the system
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize all system components"""
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Embedding model loaded successfully")
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"description": "EmotiBot conversation memory and documents"}
            )
            
            self.logger.info("RAG system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            return []
    
    def add_document(self, text: str, metadata: Dict = None, chunk_size: int = 1000) -> bool:
        """
        Add a document to the knowledge base
        
        Args:
            text: Document text
            metadata: Optional metadata dict
            chunk_size: Size of text chunks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Chunk the document
            chunks = self.doc_processor.chunk_text(text, chunk_size=chunk_size)
            
            if not chunks:
                self.logger.warning("No chunks generated from document")
                return False
            
            # Generate IDs for chunks
            chunk_ids = [str(uuid.uuid4()) for _ in chunks]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            if not embeddings:
                self.logger.error("Failed to generate embeddings for document")
                return False
            
            # Prepare metadata for each chunk
            chunk_metadata = []
            for i, chunk_id in enumerate(chunk_ids):
                chunk_meta = {
                    'chunk_id': chunk_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'timestamp': datetime.now().isoformat(),
                    'type': 'document'
                }
                
                # Add user metadata if provided
                if metadata:
                    chunk_meta.update(metadata)
                
                chunk_metadata.append(chunk_meta)
            
            # Add to ChromaDB
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            self.logger.info(f"Added document with {len(chunks)} chunks to knowledge base")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding document to RAG system: {e}")
            return False
    
    def add_conversation(self, user_message: str, bot_response: str, emotions: Dict = None) -> bool:
        """
        Add a conversation exchange to memory
        
        Args:
            user_message: User's message
            bot_response: Bot's response
            emotions: Detected emotions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create conversation text
            conversation_text = f"User: {user_message}\nEmotiBot: {bot_response}"
            
            # Generate embedding
            embeddings = self.generate_embeddings([conversation_text])
            
            if not embeddings:
                return False
            
            # Prepare metadata
            metadata = {
                'type': 'conversation',
                'user_message': user_message,
                'bot_response': bot_response,
                'timestamp': datetime.now().isoformat()
            }
            
            if emotions:
                metadata['emotions'] = json.dumps(emotions)
            
            # Add to ChromaDB
            conversation_id = str(uuid.uuid4())
            self.collection.add(
                documents=[conversation_text],
                embeddings=embeddings,
                metadatas=[metadata],
                ids=[conversation_id]
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding conversation to memory: {e}")
            return False
    
    def search_similar(self, query: str, n_results: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """
        Search for similar content in the knowledge base
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embeddings = self.generate_embeddings([query])
            
            if not query_embeddings:
                return []
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=filter_dict
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                result = {
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def get_relevant_context(self, user_message: str, max_context_length: int = 2000) -> str:
        """
        Get relevant context for generating a response
        
        Args:
            user_message: User's message
            max_context_length: Maximum length of context
            
        Returns:
            Relevant context string
        """
        try:
            # Search for relevant documents and conversations
            results = self.search_similar(user_message, n_results=5)
            
            context_parts = []
            current_length = 0
            
            for result in results:
                document = result['document']
                metadata = result['metadata']
                
                # Add context with source information
                if metadata.get('type') == 'conversation':
                    context_part = f"Previous conversation: {document}\n"
                else:
                    source = metadata.get('source', 'Unknown')
                    context_part = f"From {source}: {document}\n"
                
                # Check if adding this context would exceed the limit
                if current_length + len(context_part) > max_context_length:
                    break
                
                context_parts.append(context_part)
                current_length += len(context_part)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.logger.error(f"Error getting relevant context: {e}")
            return ""
    
    def generate_response(self, user_message: str, emotions: Dict = None) -> str:
        """
        Generate a response using RAG
        
        Args:
            user_message: User's message
            emotions: Detected emotions
            
        Returns:
            Generated response
        """
        try:
            # Get relevant context
            context = self.get_relevant_context(user_message)
            
            # Prepare the prompt
            emotion_info = ""
            if emotions:
                dominant_emotion = emotions.get('dominant_emotion', 'neutral')
                confidence = emotions.get('confidence', 0)
                emotion_info = f"The user seems to be feeling {dominant_emotion} (confidence: {confidence:.2f}). "
            
            prompt = f"""You are EmotiBot, an empathetic AI companion. {emotion_info}Respond compassionately to the user's message.

Relevant context:
{context}

User message: {user_message}

Please provide a helpful, empathetic response:"""
            
            # Generate response using Gemini
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(prompt)
            bot_response = response.text
            
            # Add this conversation to memory
            self.add_conversation(user_message, bot_response, emotions)
            
            return bot_response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble generating a response right now. Please try again."
    
    def add_document_file(self, file_path: str, metadata: Dict = None) -> bool:
        """
        Add a document file to the knowledge base
        
        Args:
            file_path: Path to document file
            metadata: Optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the document
            text = self.doc_processor.read_document(file_path)
            
            if not text:
                self.logger.error(f"Could not extract text from {file_path}")
                return False
            
            # Add file metadata
            file_metadata = {
                'source': os.path.basename(file_path),
                'file_path': file_path,
                'file_type': os.path.splitext(file_path)[1]
            }
            
            if metadata:
                file_metadata.update(metadata)
            
            # Add to knowledge base
            return self.add_document(text, file_metadata)
            
        except Exception as e:
            self.logger.error(f"Error adding document file {file_path}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the knowledge base
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get some sample documents to analyze types
            sample_results = self.collection.get(limit=100)
            
            doc_count = 0
            conversation_count = 0
            
            for metadata in sample_results.get('metadatas', []):
                if metadata.get('type') == 'document':
                    doc_count += 1
                elif metadata.get('type') == 'conversation':
                    conversation_count += 1
            
            return {
                'total_items': count,
                'document_chunks': doc_count,
                'conversations': conversation_count,
                'collection_name': Config.COLLECTION_NAME
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection
            self.chroma_client.delete_collection(Config.COLLECTION_NAME)
            
            # Recreate the collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"description": "EmotiBot conversation memory and documents"}
            )
            
            self.logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing collection: {e}")
            return False
