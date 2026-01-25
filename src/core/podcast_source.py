"""Podcast transcript source implementation."""

import os
import re
from typing import Optional

from .transcript_source import TranscriptSource, TranscriptMetadata, TranscriptResult
from .metadata_extractor import MetadataExtractor
from .audio_downloader import AudioDownloader
from .transcriber import Transcriber


class PodcastSource(TranscriptSource):
    """Podcast transcript source using Whisper."""
    
    def __init__(self, download_folder: str = "downloads", whisper_model: str = "base"):
        self.source_type = "podcast"
        self.metadata_extractor = MetadataExtractor()
        self.audio_downloader = AudioDownloader(download_folder)
        self.transcriber = Transcriber(whisper_model)
        self._audio_path = None
    
    def validate_url(self, url: str) -> bool:
        """Validate podcast URL."""
        if not url:
            return False
        
        # Support Apple Podcasts, Spotify, and direct MP3 links
        return (
            'podcasts.apple.com' in url or
            'spotify.com' in url and 'episode' in url or
            url.endswith('.mp3')
        )
    
    def extract_metadata(self, url: str) -> TranscriptMetadata:
        """Extract podcast episode metadata."""
        try:
            metadata = self.metadata_extractor.extract_all_metadata(url)
            
            return TranscriptMetadata(
                title=metadata["episode_title"],
                source_name=metadata["podcast_title"],
                description=metadata["episode_description"],
                url=url,
                source_type=self.source_type
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract podcast metadata: {e}")
    
    def extract_transcript(self, url: str) -> TranscriptResult:
        """Extract transcript from podcast episode."""
        try:
            # Extract metadata first
            metadata = self.extract_metadata(url)
            
            # Download audio
            self._audio_path = self.audio_downloader.download_audio(url, metadata.title)
            if not self._audio_path:
                raise RuntimeError("Failed to download podcast audio")
            
            # Transcribe audio
            transcription_result = self.transcriber.transcribe_audio(self._audio_path)
            if not transcription_result:
                raise RuntimeError("Failed to transcribe podcast audio")
            
            raw_text = self.transcriber.get_transcript_text(transcription_result)
            
            return TranscriptResult(
                raw_text=raw_text,
                metadata=metadata
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract podcast transcript: {e}")
    
    def get_source_type(self) -> str:
        """Get the source type identifier."""
        return self.source_type
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self._audio_path and os.path.exists(self._audio_path):
            self.audio_downloader.cleanup_file(self._audio_path)
            self._audio_path = None
