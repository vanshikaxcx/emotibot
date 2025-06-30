"""
Emotion detection utilities for EmotiBot
"""
from textblob import TextBlob
import re
from typing import Dict, List, Tuple

class EmotionDetector:
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful', 'glad', 'pleased'],
            'sadness': ['sad', 'depressed', 'upset', 'disappointed', 'heartbroken', 'down'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated'],
            'fear': ['scared', 'afraid', 'terrified', 'anxious', 'worried', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'disgust': ['disgusted', 'revolted', 'sick', 'nauseated', 'repulsed']
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': 'positive' if polarity > 0.1 else 'negative' if polarity < -0.1 else 'neutral'
        }
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions based on keyword matching"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            # Normalize score
            emotion_scores[emotion] = score / len(keywords) if keywords else 0
        
        return emotion_scores
    
    def get_dominant_emotion(self, text: str) -> Tuple[str, float]:
        """Get the dominant emotion from text"""
        emotions = self.detect_emotions(text)
        
        if not emotions:
            return 'neutral', 0.0
        
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]
        
        return dominant_emotion, confidence
    
    def analyze_text(self, text: str) -> Dict:
        """Complete emotion analysis of text"""
        sentiment = self.analyze_sentiment(text)
        emotions = self.detect_emotions(text)
        dominant_emotion, confidence = self.get_dominant_emotion(text)
        
        return {
            'text': text,
            'sentiment': sentiment,
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'confidence': confidence,
            'text_length': len(text),
            'word_count': len(text.split())
        }
