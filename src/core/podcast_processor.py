"""Main podcast processing orchestrator."""

import os
from typing import Dict, Optional, Tuple

from .config import Config
from .metadata_extractor import MetadataExtractor
from .speaker_identifier import SpeakerIdentifier
from .audio_downloader import AudioDownloader
from .transcriber import Transcriber
from .transcript_cleaner import TranscriptCleaner
from .document_generator import DocumentGenerator


class PodcastProcessor:
    """Main class that orchestrates the entire podcast processing pipeline."""
    
    def __init__(self):
        """Initialize all components."""
        Config.validate()
        Config.ensure_directories()
        
        self.metadata_extractor = MetadataExtractor()
        self.speaker_identifier = SpeakerIdentifier(
            model=Config.OPENAI_MODEL,
            temperature=0.0
        )
        self.audio_downloader = AudioDownloader(Config.DOWNLOAD_FOLDER)
        self.transcriber = Transcriber(Config.WHISPER_MODEL)
        self.transcript_cleaner = TranscriptCleaner(
            model=Config.OPENAI_MODEL,
            max_tokens_input=Config.MAX_TOKENS_INPUT,
            max_tokens_output=Config.MAX_TOKENS_OUTPUT
        )
        self.document_generator = DocumentGenerator(Config.TRANSCRIPT_FOLDER)
    
    def process_podcast(self, url: str) -> Tuple[str, str]:
        """
        Process a podcast URL from start to finish.
        
        Args:
            url: Podcast episode URL
            
        Returns:
            Tuple of (raw_document_path, cleaned_document_path)
        """
        print(f"Processing podcast: {url}")
        
        # Step 1: Extract metadata
        print("Extracting metadata...")
        metadata = self.metadata_extractor.extract_all_metadata(url)
        podcast_title = metadata["podcast_title"]
        episode_title = metadata["episode_title"]
        episode_description = metadata["episode_description"]
        
        print(f"Podcast: {podcast_title}")
        print(f"Episode: {episode_title}")
        
        # Step 2: Identify speakers
        print("Identifying speakers...")
        speakers = self.speaker_identifier.extract_speakers(
            podcast_title, episode_title, episode_description
        )
        podcast_description = self.speaker_identifier.format_speaker_description(
            speakers, podcast_title
        )
        
        print(f"Host: {speakers['host']}")
        if speakers["cohosts"]:
            print(f"Co-hosts: {', '.join(speakers['cohosts'])}")
        if speakers["guests"]:
            print(f"Guests: {', '.join(speakers['guests'])}")
        
        # Step 3: Download audio
        print("Downloading audio...")
        audio_path = self.audio_downloader.download_audio(url, episode_title)
        if not audio_path:
            raise RuntimeError("Failed to download audio")
        
        # Step 4: Transcribe audio
        print("Transcribing audio...")
        transcription_result = self.transcriber.transcribe_audio(audio_path)
        if not transcription_result:
            raise RuntimeError("Failed to transcribe audio")
        
        raw_transcript = self.transcriber.get_transcript_text(transcription_result)
        
        # Step 5: Generate raw transcript document
        print("Generating raw transcript document...")
        raw_doc_path = self.document_generator.create_document(
            episode_title, podcast_title, speakers, raw_transcript, cleaned=False
        )
        
        # Step 6: Clean transcript
        print("Cleaning transcript...")
        cleaned_transcript = self.transcript_cleaner.clean_transcription(
            raw_transcript, podcast_description, speakers
        )
        
        # Step 7: Generate cleaned transcript document
        print("Generating cleaned transcript document...")
        cleaned_doc_path = self.document_generator.create_document(
            episode_title, podcast_title, speakers, cleaned_transcript, cleaned=True
        )
        
        # Step 8: Cleanup
        print("Cleaning up temporary files...")
        self.audio_downloader.cleanup_file(audio_path)
        
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
            "max_tokens_output": str(Config.MAX_TOKENS_OUTPUT)
        }
