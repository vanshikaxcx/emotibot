"""
Configuration settings for EmotiBot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Model Settings
    GOOGLE_MODEL = "gemini-pro"
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Speech Settings
    SPEECH_RATE = 150
    SPEECH_LANG = "en"
    
    # Emotion Detection Settings
    EMOTION_THRESHOLD = 0.5
    
    # Vector Database Settings
    CHROMA_PERSIST_DIR = "./chroma_db"
    COLLECTION_NAME = "emotibot_memory"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_keys = [
            cls.GOOGLE_API_KEY,
            cls.OPENAI_API_KEY
        ]
        
        missing_keys = [key for key in required_keys if not key]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        return True
