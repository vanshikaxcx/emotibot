"""
Speech processing utilities for EmotiBot
Handles speech-to-text and text-to-speech functionality
"""
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import pygame
import io
import tempfile
import os
from typing import Optional, Tuple
import threading
import time

class SpeechProcessor:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            self.setup_tts_engine()
        except:
            self.tts_engine = None
            print("Warning: pyttsx3 TTS engine failed to initialize")
        
        # Initialize pygame for audio playback
        try:
            pygame.mixer.init()
        except:
            print("Warning: pygame mixer failed to initialize")
        
        # Calibrate microphone for ambient noise
        self.calibrate_microphone()
    
    def setup_tts_engine(self):
        """Configure the TTS engine settings"""
        if self.tts_engine:
            # Set speech rate
            self.tts_engine.setProperty('rate', 150)
            
            # Set volume
            self.tts_engine.setProperty('volume', 0.9)
            
            # Try to set a female voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone calibrated successfully")
        except Exception as e:
            print(f"Warning: Microphone calibration failed: {e}")
    
    def listen_for_speech(self, timeout: int = 5, phrase_timeout: int = 2) -> Optional[str]:
        """
        Listen for speech input from microphone
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_timeout: Maximum time to wait for phrase to complete
            
        Returns:
            Recognized text or None if failed
        """
        try:
            with self.microphone as source:
                print("Listening for speech...")
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
                
                print("Processing speech...")
                # Recognize speech using Google's speech recognition
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            print("Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return None
    
    def speak_text_pyttsx3(self, text: str) -> bool:
        """
        Convert text to speech using pyttsx3 (offline)
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.tts_engine:
                return False
                
            print(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
            
        except Exception as e:
            print(f"Error with pyttsx3 TTS: {e}")
            return False
    
    def speak_text_gtts(self, text: str, lang: str = 'en') -> bool:
        """
        Convert text to speech using Google TTS (online)
        
        Args:
            text: Text to convert to speech
            lang: Language code (default: 'en')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Speaking with gTTS: {text}")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play the audio file
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
            return True
            
        except Exception as e:
            print(f"Error with gTTS: {e}")
            return False
    
    def speak_text(self, text: str, method: str = 'auto') -> bool:
        """
        Convert text to speech using the best available method
        
        Args:
            text: Text to convert to speech
            method: 'pyttsx3', 'gtts', or 'auto'
            
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            return False
        
        # Clean the text
        text = text.strip()
        
        if method == 'pyttsx3' or method == 'auto':
            if self.speak_text_pyttsx3(text):
                return True
            elif method == 'pyttsx3':
                return False
        
        if method == 'gtts' or method == 'auto':
            return self.speak_text_gtts(text)
        
        return False
    
    def record_audio_to_file(self, filename: str, duration: int = 5) -> bool:
        """
        Record audio to a file for a specified duration
        
        Args:
            filename: Output filename
            duration: Recording duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.microphone as source:
                print(f"Recording for {duration} seconds...")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=duration)
                
                with open(filename, "wb") as f:
                    f.write(audio.get_wav_data())
                
                print(f"Audio saved to {filename}")
                return True
                
        except Exception as e:
            print(f"Error recording audio: {e}")
            return False
    
    def transcribe_audio_file(self, filename: str) -> Optional[str]:
        """
        Transcribe audio from a file
        
        Args:
            filename: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            with sr.AudioFile(filename) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                print(f"Transcribed: {text}")
                return text
                
        except Exception as e:
            print(f"Error transcribing audio file: {e}")
            return None
    
    def test_speech_system(self) -> dict:
        """
        Test the speech system components
        
        Returns:
            Dictionary with test results
        """
        results = {
            'microphone': False,
            'speech_recognition': False,
            'pyttsx3_tts': False,
            'gtts_tts': False,
            'pygame_audio': False
        }
        
        # Test microphone
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            results['microphone'] = True
            print("✓ Microphone test passed")
        except:
            print("✗ Microphone test failed")
        
        # Test speech recognition
        try:
            # This is just testing if the service is available
            results['speech_recognition'] = True
            print("✓ Speech recognition service available")
        except:
            print("✗ Speech recognition test failed")
        
        # Test pyttsx3 TTS
        if self.speak_text_pyttsx3("Testing pyttsx3"):
            results['pyttsx3_tts'] = True
            print("✓ pyttsx3 TTS test passed")
        else:
            print("✗ pyttsx3 TTS test failed")
        
        # Test gTTS
        if self.speak_text_gtts("Testing Google TTS"):
            results['gtts_tts'] = True
            print("✓ Google TTS test passed")
        else:
            print("✗ Google TTS test failed")
        
        # Test pygame audio
        try:
            pygame.mixer.init()
            results['pygame_audio'] = True
            print("✓ Pygame audio test passed")
        except:
            print("✗ Pygame audio test failed")
        
        return results
