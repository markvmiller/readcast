"""Main transcript processing orchestrator supporting multiple sources."""

import os
from typing import Dict, Optional, Tuple

from .config import Config
from .speaker_identifier import SpeakerIdentifier
from .transcript_cleaner import TranscriptCleaner
from .document_generator import DocumentGenerator
from .transcript_source import TranscriptSource
from .podcast_source import PodcastSource
from .youtube_source import YouTubeSource


class TranscriptProcessor:
    """Main class that orchestrates transcript processing from multiple sources."""
    
    def __init__(self):
        """Initialize all components."""
        Config.validate()
        Config.ensure_directories()
        
        # Initialize shared components
        self.speaker_identifier = SpeakerIdentifier(
            model=Config.OPENAI_MODEL,
            temperature=0.0
        )
        self.transcript_cleaner = TranscriptCleaner(
            model=Config.OPENAI_MODEL,
            max_tokens_input=Config.MAX_TOKENS_INPUT,
            max_tokens_output=Config.MAX_TOKENS_OUTPUT
        )
        self.document_generator = DocumentGenerator(Config.TRANSCRIPT_FOLDER)
        
        # Initialize transcript sources
        self.sources = {
            "podcast": PodcastSource(
                download_folder=Config.DOWNLOAD_FOLDER,
                whisper_model=Config.WHISPER_MODEL
            ),
            "youtube": YouTubeSource()
        }
    
    def get_supported_sources(self) -> Dict[str, str]:
        """Get supported source types and their descriptions."""
        return {
            "podcast": "Podcast episodes (Apple Podcasts, Spotify, MP3)",
            "youtube": "YouTube videos"
        }
    
    def validate_url(self, source_type: str, url: str) -> bool:
        """Validate URL for a specific source type."""
        if source_type not in self.sources:
            return False
        
        return self.sources[source_type].validate_url(url)
    
    def process_transcript(self, source_type: str, url: str) -> Tuple[str, str]:
        """
        Process a transcript from any supported source.
        
        Args:
            source_type: Type of source ("podcast" or "youtube")
            url: URL of the content
            
        Returns:
            Tuple of (raw_document_path, cleaned_document_path)
        """
        print(f"Processing {source_type}: {url}")
        
        # Validate source type
        if source_type not in self.sources:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        source = self.sources[source_type]
        
        # Step 1: Extract transcript and metadata
        print("Extracting transcript and metadata...")
        transcript_result = source.extract_transcript(url)
        metadata = transcript_result.metadata
        
        print(f"Title: {metadata.title}")
        print(f"Source: {metadata.source_name}")
        print(f"Type: {metadata.source_type}")
        
        # Step 2: Identify speakers
        print("Identifying speakers...")
        speakers = self.speaker_identifier.extract_speakers(
            metadata.source_name, metadata.title, metadata.description
        )
        
        # For YouTube, adjust the description format
        if metadata.source_type == "youtube":
            content_description = f"a YouTube video from {metadata.source_name}"
        else:
            content_description = self.speaker_identifier.format_speaker_description(
                speakers, metadata.source_name
            )
        
        print(f"Host: {speakers['host']}")
        if speakers["cohosts"]:
            print(f"Co-hosts: {', '.join(speakers['cohosts'])}")
        if speakers["guests"]:
            print(f"Guests: {', '.join(speakers['guests'])}")
        
        # Step 3: Generate raw transcript document
        print("Generating raw transcript document...")
        raw_doc_path = self.document_generator.create_document(
            metadata.title, metadata.source_name, speakers, 
            transcript_result.raw_text, cleaned=False
        )

        # Step 4: Cleanup (for podcast sources)
        if hasattr(source, 'cleanup'):
            source.cleanup()

        # Step 5: Clean transcript
        print("Cleaning transcript...")
        cleaned_transcript = self.transcript_cleaner.clean_transcription(
            transcript_result.raw_text, content_description, speakers
        )
        
        # Step 6: Generate cleaned transcript document
        print("Generating cleaned transcript document...")
        cleaned_doc_path = self.document_generator.create_document(
            metadata.title, metadata.source_name, speakers, 
            cleaned_transcript, cleaned=True
        )
                
        print("Processing completed successfully!")
        return raw_doc_path, cleaned_doc_path
    
    def get_processing_status(self) -> Dict[str, str]:
        """Get current processing status and configuration."""
        return {
            "whisper_model": Config.WHISPER_MODEL,
            "openai_model": Config.OPENAI_MODEL,
            "download_folder": Config.DOWNLOAD_FOLDER,
            "transcript_folder": Config.TRANSCRIPT_FOLDER,
            "max_tokens_input": str(Config.MAX_TOKENS_INPUT),
            "max_tokens_output": str(Config.MAX_TOKENS_OUTPUT),
            "supported_sources": ", ".join(self.get_supported_sources().keys())
        }


# Keep the old class name for backward compatibility
class PodcastProcessor(TranscriptProcessor):
    """Legacy class name for backward compatibility."""
    pass
