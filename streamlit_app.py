import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables with explicit path
load_dotenv(dotenv_path='.env')

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
    
    # Try multiple ways to get the API keys
    google_api_key = None
    openai_api_key = None
    
    # Method 1: Try from .env file
    try:
        from dotenv import dotenv_values
        env_vars = dotenv_values('.env')
        google_api_key = env_vars.get('GOOGLE_API_KEY')
        openai_api_key = env_vars.get('OPENAI_API_KEY')
    except Exception as e:
        st.sidebar.error(f"Error loading .env: {e}")
    
    # Method 2: Try from environment variables
    if not google_api_key:
        google_api_key = os.getenv("GOOGLE_API_KEY")
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Method 3: Try from Streamlit secrets
    try:
        if not google_api_key:
            google_api_key = st.secrets["GOOGLE_API_KEY"]
        if not openai_api_key:
            openai_api_key = st.secrets["OPENAI_API_KEY"]
    except:
        pass
    
    # Method 4: Allow manual input as fallback
    if not google_api_key:
        st.sidebar.warning("⚠️ Google API Key not found in environment")
        google_api_key = st.sidebar.text_input("Enter Google API Key:", type="password")
    
    if not openai_api_key:
        st.sidebar.warning("⚠️ OpenAI API Key not found in environment")
        openai_api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
    
    # Debug: Show what we found (remove this after testing)
    st.sidebar.write("Debug Info:")
    st.sidebar.write(f"Google API Key found: {'✅' if google_api_key else '❌'}")
    st.sidebar.write(f"OpenAI API Key found: {'✅' if openai_api_key else '❌'}")
    
    # Show first few characters of the key for verification
    if google_api_key:
        st.sidebar.write(f"Google API Key starts with: {google_api_key[:10]}...")
    if openai_api_key:
        st.sidebar.write(f"OpenAI API Key starts with: {openai_api_key[:10]}...")
    
    # Validation with better messaging
    if not google_api_key or len(google_api_key.strip()) == 0:
        st.error("❌ Google API Key not found. Please provide it using one of the methods in the sidebar.")
        st.info("💡 You can enter your API key in the sidebar input field above.")
        return
    
    # OpenAI is optional for basic functionality
    if not openai_api_key:
        st.warning("⚠️ OpenAI API Key not found. Some features may be limited.")
    
    st.success("✅ Google API Key configured successfully!")
    if openai_api_key:
        st.success("✅ OpenAI API Key configured successfully!")
    
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
