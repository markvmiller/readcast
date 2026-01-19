"""Speaker identification from podcast metadata."""

import json
import openai
from typing import Dict, List, Optional


class SpeakerIdentifier:
    """Identifies speakers from podcast metadata using OpenAI."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        self.client = openai.OpenAI()
    
    def extract_speakers(self, podcast_title: str, episode_title: str, episode_description: str) -> Dict[str, List[str]]:
        """
        Extract host, cohosts, and guests from podcast metadata.
        
        Returns:
            Dict with keys: host (required), cohosts (optional), guests (optional)
        """
        system_prompt = (
            "You are an assistant that extracts speakers from podcast metadata.\n"
            "Return a JSON object with these keys only:\n"
            "• host (REQUIRED, string)\n"
            "• cohosts (OPTIONAL, list of strings)\n"
            "• guests (OPTIONAL, list of strings)\n"
            "Only respond with valid JSON. Do not include extra commentary."
        )
        
        user_prompt = f"""
Podcast Title: {podcast_title}
Episode Title: {episode_title}
Episode Description:
{episode_description}
        """.strip()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            
            if "host" not in result or not result["host"].strip():
                raise RuntimeError(f"No host identified in the model's output: {result}")
            
            # Ensure proper structure
            result["cohosts"] = result.get("cohosts", [])
            result["guests"] = result.get("guests", [])
            
            return result
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"The model's response was not valid JSON: {content}") from e
        except Exception as e:
            raise RuntimeError(f"Error extracting speakers: {e}") from e
    
    def format_speaker_description(self, speakers: Dict[str, List[str]], podcast_title: str) -> str:
        """Create a human-readable description of the podcast speakers."""
        host = speakers["host"]
        description = f"The {podcast_title} podcast with {host}"
        
        if not description.startswith("The "):
            description = "The " + description
        
        # Add cohosts
        if speakers["cohosts"]:
            cohost_list = speakers["cohosts"]
            cohosts_str = self._join_list_elements(cohost_list)
            description += " and " if len(cohost_list) == 1 else ", "
            description += cohosts_str
        
        # Add guests
        if speakers["guests"]:
            guest_list = speakers["guests"]
            guests_str = self._join_list_elements(guest_list)
            description += f", featuring guest"
            description += " " if len(guest_list) == 1 else "s "
            description += guests_str
        
        return description
    
    def _join_list_elements(self, item_list: List[str]) -> str:
        """Convert a list of elements to human-readable string."""
        if len(item_list) == 1:
            return item_list[0]
        elif len(item_list) == 2:
            return " and ".join(item_list)
        else:
            return ", ".join(item_list[:-1]) + ", and " + item_list[-1]
