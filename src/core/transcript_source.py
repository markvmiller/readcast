"""Abstract base class for transcript sources."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class TranscriptMetadata:
    """Metadata for a transcript source."""
    title: str
    source_name: str  # Podcast name or YouTube channel
    description: str
    url: str
    source_type: str  # "podcast" or "youtube"


@dataclass
class TranscriptResult:
    """Result from transcript extraction."""
    raw_text: str
    metadata: TranscriptMetadata


class TranscriptSource(ABC):
    """Abstract base class for transcript sources."""
    
    @abstractmethod
    def extract_metadata(self, url: str) -> TranscriptMetadata:
        """Extract metadata from the URL."""
        pass
    
    @abstractmethod
    def extract_transcript(self, url: str) -> TranscriptResult:
        """Extract transcript from the URL."""
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Validate if URL is supported by this source."""
        pass
    
    @abstractmethod
    def get_source_type(self) -> str:
        """Get the source type identifier."""
        pass
