"""Audio downloader for podcast episodes."""

import os
import re
import requests
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class AudioDownloader:
    """Downloads podcast audio from URLs."""
    
    def __init__(self, download_folder: str = "downloads"):
        self.download_folder = download_folder
        os.makedirs(download_folder, exist_ok=True)
    
    def download_audio(self, url: str, episode_title: str) -> Optional[str]:
        """
        Download audio from podcast URL and save as MP3.
        
        Args:
            url: Podcast page URL
            episode_title: Clean episode title for filename
            
        Returns:
            Path to downloaded MP3 file, or None if failed
        """
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to load page: {response.status_code}")
                return None
            
            # Find MP3 links using regex
            html_content = response.text
            mp3_links = re.findall(r'https?://[^\s"\']+\.mp3', html_content)
            unique_links = list(set(mp3_links))
            
            if not unique_links:
                print("No .mp3 links found.")
                return None
            
            # Download the first unique MP3 link
            mp3_url = unique_links[0]
            print(f"Downloading: {mp3_url}")
            
            # Create safe filename
            safe_title = "".join(c for c in episode_title if c.isalnum() or c in (" ", "_", "-")).strip()
            mp3_path = os.path.join(self.download_folder, f"{safe_title}.mp3")
            
            # Download the file
            r = requests.get(mp3_url, stream=True)
            r.raise_for_status()
            
            with open(mp3_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Saved as: {mp3_path}")
            return mp3_path
            
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
    
    def cleanup_file(self, file_path: str) -> None:
        """Remove downloaded audio file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")
