"""Audio transcription using Whisper."""

import os
import whisper
from typing import Dict, Optional


class Transcriber:
    """Transcribes audio files using OpenAI Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize transcriber with specified Whisper model.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
    
    def _load_model(self) -> None:
        """Load Whisper model (lazy loading)."""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
    
    def transcribe_audio(self, audio_path: str) -> Optional[Dict]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcription result dictionary or None if failed
        """
        try:
            self._load_model()
            
            if not os.path.exists(audio_path):
                print(f"Audio file not found: {audio_path}")
                return None
            
            print(f"Transcribing: {audio_path}")
            result = self.model.transcribe(audio_path)
            
            print("Transcription completed")
            return result
            
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
    
    def get_transcript_text(self, transcription_result: Dict) -> str:
        """Extract raw text from transcription result."""
        if transcription_result and 'text' in transcription_result:
            return transcription_result['text']
        return ""
