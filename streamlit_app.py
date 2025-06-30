import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="EmotiBot - AI Emotional Companion",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 EmotiBot - AI Emotional Companion")
    st.markdown("Welcome to EmotiBot! Your AI-powered emotional conversation companion.")
    
    # Sidebar for configuration
    st.sidebar.title("Configuration")
    
    # Check if environment variables are set (try both .env and Streamlit secrets)
    google_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    
    if not google_api_key:
        st.error("❌ Google API Key not found. Please set GOOGLE_API_KEY in your .env file.")
        return
    
    if not openai_api_key:
        st.error("❌ OpenAI API Key not found. Please set OPENAI_API_KEY in your .env file.")
        return
    
    st.success("✅ API Keys configured successfully!")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Chat input
        user_input = st.text_area("Type your message here:", height=100)
        
        if st.button("Send Message"):
            if user_input:
                st.info(f"You: {user_input}")
                # TODO: Process with emotion detection and generate response
                st.success("EmotiBot: Thank you for your message! I'm here to help you.")
            else:
                st.warning("Please enter a message.")
    
    with col2:
        st.subheader("📊 Emotion Analysis")
        st.info("Emotion analysis will appear here")
        
        st.subheader("🎤 Voice Controls")
        if st.button("Start Voice Recording"):
            st.info("Voice recording feature coming soon!")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and AI")

if __name__ == "__main__":
    main()
