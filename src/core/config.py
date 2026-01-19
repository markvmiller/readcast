"""Configuration settings for the podcast transcription application."""

import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS_INPUT: int = 8000
    MAX_TOKENS_OUTPUT: int = 12000
    
    # Whisper settings
    WHISPER_MODEL: str = "base"  # Options: tiny, base, small, medium, large
    
    # File paths
    DOWNLOAD_FOLDER: str = "downloads"
    TRANSCRIPT_FOLDER: str = "transcripts"
    STATIC_FOLDER: str = "static"
    
    # Chunking settings
    CHUNK_OVERLAP: int = 100
    
    # Web UI settings
    WEB_TITLE: str = "Podcast Transcriber"
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key must be set in OPENAI_API_KEY environment variable")
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        for folder in [cls.DOWNLOAD_FOLDER, cls.TRANSCRIPT_FOLDER, cls.STATIC_FOLDER]:
            os.makedirs(folder, exist_ok=True)
