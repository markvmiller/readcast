"""YouTube transcript source implementation."""

import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable
)

from .transcript_source import TranscriptSource, TranscriptMetadata, TranscriptResult


class YouTubeSource(TranscriptSource):
    """YouTube transcript source using youtube_transcript_api."""
    
    def __init__(self):
        self.source_type = "youtube"
    
    def validate_url(self, url: str) -> bool:
        """Validate YouTube URL."""
        if not url:
            return False
        
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+'
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    # def extract_metadata(self, url: str) -> TranscriptMetadata:
    #     """Extract YouTube video metadata."""
    #     try:
    #         with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    #             info = ydl.extract_info(url, download=False)
                
    #             title = self._clean_name(info.get('title', 'Untitled Video'))
    #             channel_name = self._clean_name(info.get('uploader', 'Unknown Channel'))
    #             description = info.get('description', 'No description available')
                
    #             return TranscriptMetadata(
    #                 title=title,
    #                 source_name=channel_name,
    #                 description=description,
    #                 url=url,
    #                 source_type=self.source_type
    #             )
                
    #     except Exception as e:
    #         raise RuntimeError(f"Failed to extract YouTube metadata: {e}")
    def extract_metadata(self, url: str) -> TranscriptMetadata:
        """Extract YouTube video metadata without triggering stream extraction."""
        try:
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "no_warnings": True,
                "extract_flat": True,          # 🔑 do NOT resolve formats
                "force_generic_extractor": False,
                "extractor_args": {
                    "youtube": {
                        "skip": ["dash", "hls"],  # 🔑 avoid SABR paths
                    }
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = self._clean_name(info.get("title", "Untitled Video"))
            channel_name = self._clean_name(info.get("uploader", "Unknown Channel"))
            description = info.get("description", "No description available")

            return TranscriptMetadata(
                title=title,
                source_name=channel_name,
                description=description,
                url=url,
                source_type=self.source_type
            )

        except Exception as e:
            raise RuntimeError(f"Failed to extract YouTube metadata: {e}")


    def extract_transcript(self, url: str) -> TranscriptResult:
        """Extract transcript from YouTube video."""
        try:
            # Extract metadata first
            metadata = self.extract_metadata(url)
            
            # Extract video ID
            video_id = self._extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            # Get transcript
            api = YouTubeTranscriptApi()
            
            # Try to get manual transcript first, fall back to auto-generated
            try:
                transcript_list = api.list(video_id)
                transcript = transcript_list.find_transcript(['en'])
                transcript_data = transcript.fetch()
            except NoTranscriptFound:
                # Fall back to auto-generated transcript
                gen = transcript_list.find_generated_transcript(['en'])
                transcript_data = gen.fetch()
            
            # Join transcript text
            raw_text = " ".join(snippet.text for snippet in transcript_data)
            
            return TranscriptResult(
                raw_text=raw_text,
                metadata=metadata
            )
            
        except TranscriptsDisabled:
            raise RuntimeError("Transcripts are disabled for this video")
        except NoTranscriptFound:
            raise RuntimeError("No transcript found for this video")
        except VideoUnavailable:
            raise RuntimeError("Video is unavailable or private")
        except Exception as e:
            raise RuntimeError(f"Failed to extract YouTube transcript: {e}")
    
    def get_source_type(self) -> str:
        """Get the source type identifier."""
        return self.source_type
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _clean_name(self, name: str) -> str:
        if not name:
            return "Unknown"

        name = re.sub(r"\s+", " ", name).strip()

        # Remove characters illegal on Windows/macOS/Linux
        name = re.sub(r"[<>:\"/\\|?*']", "", name)

        return name

"""
future enhancement idea: separate these two in the code:
display_title = original_title
filename_title = make_filesystem_safe(original_title)

"""