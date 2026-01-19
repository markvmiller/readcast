"""Podcast metadata extraction from web pages."""

import json
import re
import html
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup, Comment


class MetadataExtractor:
    """Extracts podcast metadata from web pages."""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
    
    def extract_podcast_title(self, url: str) -> str:
        """Extract podcast channel name from page."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look through JSON-LD script tags
            for script_tag in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script_tag.string)
                    
                    items = data if isinstance(data, list) else [data]
                    
                    for item in items:
                        if item.get("@type") == "PodcastEpisode":
                            series = item.get("partOfSeries")
                            if isinstance(series, dict):
                                name = series.get("name")
                                if name:
                                    return name
                except (json.JSONDecodeError, TypeError):
                    continue
                    
        except Exception as e:
            print(f"Error extracting podcast title: {e}")
            
        return "untitled_podcast"
    
    def extract_episode_title(self, url: str) -> str:
        """Extract episode title from page."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try Open Graph meta tag
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"]
            else:
                # Try meta name="title"
                meta_title = soup.find("meta", attrs={"name": "title"})
                if meta_title and meta_title.get("content"):
                    title = meta_title["content"]
                else:
                    # Fall back to title tag
                    title = soup.title.string.strip() if soup.title and soup.title.string else "untitled_episode"
            
            # Clean up the title
            title = re.sub(r'[^\x00-\x7F]+', '', title)
            title = re.sub(r'\s+', ' ', title).strip()
            title = title.replace("&", "And").title()
            title = title.replace(":", ",")
            title = title.replace("-", ",")
            title = title.replace(" ,", ",")
            
            return title
            
        except Exception as e:
            print(f"Error extracting episode title: {e}")
            return "untitled_episode"
    
    def extract_episode_description(self, url: str) -> str:
        """Extract full episode description from page."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try JSON-LD first
            json_fallback = None
            for tag in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(tag.string)
                except (TypeError, json.JSONDecodeError):
                    continue
                
                for item in (data if isinstance(data, list) else [data]):
                    if item.get("@type") == "PodcastEpisode":
                        desc = item.get("description")
                        if desc and len(desc) > 400:
                            return desc.strip()
                        json_fallback = desc or json_fallback
            
            # Try HTML comment block
            wrapper = soup.find("div", attrs={"data-testid": "paragraphs"})
            if wrapper:
                paragraphs = []
                
                for node in wrapper.descendants:
                    if getattr(node, "name", None) == "p":
                        paragraphs.append(node.get_text(" ", strip=True))
                    elif isinstance(node, Comment):
                        sub = BeautifulSoup(node, "html.parser")
                        paragraphs.extend(
                            p.get_text(" ", strip=True) for p in sub.find_all("p")
                        )
                
                text = "\n\n".join(html.unescape(p) for p in paragraphs if p)
                if text:
                    return text
            
            # Fallback to JSON-LD
            if json_fallback:
                return json_fallback.strip()
                
        except Exception as e:
            print(f"Error extracting episode description: {e}")
            
        return "no_description_found"
    
    def extract_all_metadata(self, url: str) -> Dict[str, str]:
        """Extract all metadata from a podcast URL."""
        return {
            "podcast_title": self.extract_podcast_title(url),
            "episode_title": self.extract_episode_title(url),
            "episode_description": self.extract_episode_description(url)
        }
