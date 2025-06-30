import streamlit as st
import os
import io
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
from emotion_detector import EmotionDetector
from speech_processor import SpeechProcessor
from document_processor import DocumentProcessor
from rag_system import RAGSystem
import time
import threading

# Load environment variables
load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'emotion_detector' not in st.session_state:
    st.session_state.emotion_detector = EmotionDetector()
if 'speech_processor' not in st.session_state:
    try:
        st.session_state.speech_processor = SpeechProcessor()
    except Exception as e:
        st.error(f"Speech processor initialization failed: {e}")
        st.session_state.speech_processor = None
if 'document_processor' not in st.session_state:
    st.session_state.document_processor = DocumentProcessor()
if 'rag_system' not in st.session_state:
    try:
        st.session_state.rag_system = RAGSystem()
    except Exception as e:
        st.error(f"RAG system initialization failed: {e}")
        st.session_state.rag_system = None

def main():
    st.set_page_config(
        page_title="EmotiBot - AI Emotional Companion",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 EmotiBot - AI Emotional Companion")
    st.markdown("Welcome to EmotiBot! Your AI-powered emotional conversation companion with speech and document processing capabilities.")
    
    # Check API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        try:
            google_api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            pass
    
    if not google_api_key:
        st.error("❌ Google API Key not found. Please set GOOGLE_API_KEY in your .env file.")
        return
    
    # Configure Google AI
    genai.configure(api_key=google_api_key)
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Controls")
        
        # Mode selection
        mode = st.selectbox(
            "Interaction Mode",
            ["💬 Text Chat", "🎤 Voice Chat", "📄 Document Analysis"]
        )
        
        # System status
        st.subheader("🔧 System Status")
        st.success("✅ Google AI: Connected")
        
        if st.session_state.speech_processor:
            st.success("✅ Speech: Available")
        else:
            st.error("❌ Speech: Unavailable")
        
        if st.session_state.rag_system:
            st.success("✅ RAG System: Available")
            
            # Show collection stats
            stats = st.session_state.rag_system.get_collection_stats()
            if 'total_items' in stats:
                st.info(f"📊 Knowledge Base: {stats['total_items']} items")
        else:
            st.error("❌ RAG System: Unavailable")
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content based on mode
    if mode == "💬 Text Chat":
        text_chat_interface()
    elif mode == "🎤 Voice Chat":
        voice_chat_interface()
    elif mode == "📄 Document Analysis":
        document_analysis_interface()

def text_chat_interface():
    """Text-based chat interface"""
    st.subheader("💬 Text Chat")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for chat in st.session_state.chat_history:
            # User message
            with st.chat_message("user"):
                st.write(chat['user_message'])
            
            # Bot response with emotions
            with st.chat_message("assistant"):
                st.write(chat['bot_response'])
                
                # Show emotion analysis if available
                if 'emotions' in chat:
                    emotions = chat['emotions']
                    if emotions.get('dominant_emotion'):
                        emotion_text = f"🎭 Detected emotion: {emotions['dominant_emotion']} ({emotions.get('confidence', 0):.2f})"
                        st.caption(emotion_text)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        process_text_message(user_input)

def voice_chat_interface():
    """Voice-based chat interface"""
    st.subheader("🎤 Voice Chat")
    
    if not st.session_state.speech_processor:
        st.error("Speech processing is not available. Please check your system setup.")
        return
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎤 Start Recording", type="primary"):
            record_and_process_speech()
    
    with col2:
        if st.button("🔊 Test TTS"):
            test_text_to_speech()
    
    with col3:
        if st.button("🧪 Test Speech System"):
            test_speech_system()
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(f"🎤 {chat['user_message']}")
        
        with st.chat_message("assistant"):
            st.write(f"🔊 {chat['bot_response']}")
            
            if 'emotions' in chat:
                emotions = chat['emotions']
                if emotions.get('dominant_emotion'):
                    emotion_text = f"🎭 {emotions['dominant_emotion']} ({emotions.get('confidence', 0):.2f})"
                    st.caption(emotion_text)

def document_analysis_interface():
    """Document analysis interface"""
    st.subheader("📄 Document Analysis")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        # Process document
        with st.spinner("Processing document..."):
            process_uploaded_document(uploaded_file)
    
    # Document chat
    st.subheader("💬 Ask about your documents")
    
    if st.session_state.rag_system:
        doc_question = st.text_input("Ask a question about your uploaded documents:")
        
        if doc_question and st.button("🔍 Search Documents"):
            search_documents(doc_question)

def process_text_message(user_input):
    """Process a text message and generate response"""
    try:
        # Analyze emotions
        emotions = st.session_state.emotion_detector.analyze_text(user_input)
        
        # Generate response
        if st.session_state.rag_system:
            bot_response = st.session_state.rag_system.generate_response(user_input, emotions)
        else:
            # Fallback to direct Gemini
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"You are EmotiBot, an empathetic AI companion. Respond compassionately to: {user_input}"
            response = model.generate_content(prompt)
            bot_response = response.text
        
        # Add to chat history
        chat_entry = {
            'user_message': user_input,
            'bot_response': bot_response,
            'emotions': emotions,
            'timestamp': time.time()
        }
        st.session_state.chat_history.append(chat_entry)
        
        # Rerun to update display
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing message: {e}")

def record_and_process_speech():
    """Record speech and process it"""
    if not st.session_state.speech_processor:
        st.error("Speech processor not available")
        return
    
    try:
        with st.spinner("🎤 Listening... (5 seconds)"):
            # Record speech
            recognized_text = st.session_state.speech_processor.listen_for_speech(timeout=5)
        
        if recognized_text:
            st.success(f"🎤 Heard: {recognized_text}")
            
            # Process the message
            process_text_message(recognized_text)
            
            # Speak the response
            if st.session_state.chat_history:
                latest_response = st.session_state.chat_history[-1]['bot_response']
                with st.spinner("🔊 Speaking response..."):
                    st.session_state.speech_processor.speak_text(latest_response)
        else:
            st.warning("No speech detected or could not understand audio")
            
    except Exception as e:
        st.error(f"Speech processing error: {e}")

def test_text_to_speech():
    """Test text-to-speech functionality"""
    if not st.session_state.speech_processor:
        st.error("Speech processor not available")
        return
    
    test_text = "Hello! This is EmotiBot testing the text-to-speech functionality."
    
    try:
        with st.spinner("🔊 Testing TTS..."):
            success = st.session_state.speech_processor.speak_text(test_text)
        
        if success:
            st.success("✅ TTS test successful!")
        else:
            st.error("❌ TTS test failed")
            
    except Exception as e:
        st.error(f"TTS test error: {e}")

def test_speech_system():
    """Test the entire speech system"""
    if not st.session_state.speech_processor:
        st.error("Speech processor not available")
        return
    
    try:
        with st.spinner("🧪 Testing speech system..."):
            results = st.session_state.speech_processor.test_speech_system()
        
        st.subheader("🧪 Speech System Test Results")
        
        for component, status in results.items():
            if status:
                st.success(f"✅ {component}: Working")
            else:
                st.error(f"❌ {component}: Failed")
                
    except Exception as e:
        st.error(f"Speech system test error: {e}")

def process_uploaded_document(uploaded_file):
    """Process an uploaded document"""
    try:
        # Read file content
        file_content = uploaded_file.read()
        file_type = uploaded_file.type
        
        # Extract text
        if 'pdf' in file_type:
            text = st.session_state.document_processor.read_pdf_from_bytes(file_content)
        elif 'word' in file_type or 'docx' in file_type:
            text = st.session_state.document_processor.read_docx_from_bytes(file_content)
        else:  # txt
            text = file_content.decode('utf-8')
        
        if not text:
            st.error("Could not extract text from document")
            return
        
        # Display preview
        st.subheader("📄 Document Preview")
        st.text_area("Content preview:", text[:1000] + "..." if len(text) > 1000 else text, height=150)
        
        # Add to knowledge base
        if st.session_state.rag_system:
            metadata = {
                'filename': uploaded_file.name,
                'file_type': file_type,
                'upload_time': time.time()
            }
            
            success = st.session_state.rag_system.add_document(text, metadata)
            
            if success:
                st.success(f"✅ Document '{uploaded_file.name}' added to knowledge base!")
            else:
                st.error("Failed to add document to knowledge base")
        else:
            st.warning("RAG system not available - document cannot be added to knowledge base")
            
    except Exception as e:
        st.error(f"Document processing error: {e}")

def search_documents(question):
    """Search documents for relevant information"""
    if not st.session_state.rag_system:
        st.error("RAG system not available")
        return
    
    try:
        with st.spinner("🔍 Searching documents..."):
            # Search for relevant content
            results = st.session_state.rag_system.search_similar(question, n_results=3)
        
        if results:
            st.subheader("🔍 Search Results")
            
            for i, result in enumerate(results, 1):
                with st.expander(f"Result {i} (Score: {1-result['distance']:.3f})"):
                    st.write(result['document'])
                    
                    metadata = result['metadata']
                    if 'filename' in metadata:
                        st.caption(f"Source: {metadata['filename']}")
            
            # Generate answer based on search results
            with st.spinner("🤖 Generating answer..."):
                answer = st.session_state.rag_system.generate_response(question)
            
            st.subheader("🤖 EmotiBot's Answer")
            st.write(answer)
            
        else:
            st.warning("No relevant documents found for your question.")
            
    except Exception as e:
        st.error(f"Document search error: {e}")

if __name__ == "__main__":
    main()
