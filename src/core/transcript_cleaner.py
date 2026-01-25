"""Transcript cleaning and formatting using OpenAI."""

import openai
import tiktoken
from typing import List, Dict, Optional


class TranscriptCleaner:
    """Cleans and formats raw transcription using OpenAI."""
    
    def __init__(self, model: str = "gpt-4o-mini", max_tokens_input: int = 8000, max_tokens_output: int = 12000):
        self.model = model
        self.max_tokens_input = max_tokens_input
        self.max_tokens_output = max_tokens_output
        self.client = openai.OpenAI()
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def split_into_chunks(self, text: str) -> List[str]:
        """Split long text into chunks within token limits."""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ''
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            
            prospective_chunk = current_chunk + ' ' + sentence if current_chunk else sentence
            if len(self.encoder.encode(prospective_chunk)) <= self.max_tokens_input:
                current_chunk = prospective_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def clean_chunk(self, chunk: str, podcast_description: str, speakers: Dict[str, List[str]], 
                   prior_lines: Optional[str] = None) -> str:
        """Clean a single chunk of transcription."""
        host = speakers["host"]
        guests = speakers["guests"]
        
        prompt = f"""
        You are helping to clean and format a transcript from an episode of {podcast_description}. 
        Below is a new chunk of raw transcript text. Please edit it to make it readable, with correct grammar, punctuation, speaker formatting, and paragraph breaks.

        Note: The raw transcript may contain misspellings of the host's or guests' names. When in doubt, always use the host{(' and guests' if guests else '')} names provided: Host = {host}{(', Guests = ' + ', '.join(guests)) if guests else ''}. Replace any unclear or incorrect names in the transcript with these correct names.
        """
        
        if guests:
            guest_names = ", ".join(guests)
            prompt += f"""

        Format the output as a dialogue, like this:
        {host}: What is your favorite color?
        {guests[0]}: My favorite color is blue.
        {host}: Cool.
        
        """
        else:
            prompt += """

        Format the output as a clear monologue or dialogue with proper speaker labels.
        
        """
        
        if prior_lines is None:
            prompt += f"""
        Here is the transcript to edit:

{chunk}
            """
        else:
            prompt += f"""
        This section follows directly after the previous transcript section, which ended with the following line:

{prior_lines}

        The new section is likely to, but may not necessarily, begin with the same speaker as the last speaker above. Here's the raw transcript to edit:

{chunk}
            """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that cleans and formats podcast transcripts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens_output,
                temperature=0.7,
                top_p=1.0,
                n=1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error cleaning chunk: {e}")
            return chunk  # Return original chunk if cleaning fails
    
    def clean_transcription(self, raw_transcription: str, podcast_description: str, 
                           speakers: Dict[str, List[str]]) -> str:
        """Clean entire transcription by processing chunks."""
        chunks = self.split_into_chunks(raw_transcription)
        cleaned_chunks = []
        prior_lines = None
        
        for i, chunk in enumerate(chunks):
            print(f"Cleaning chunk {i+1}/{len(chunks)}")
            
            cleaned_chunk = self.clean_chunk(chunk, podcast_description, speakers, prior_lines)
            cleaned_chunks.append(cleaned_chunk)
            
            # Extract final lines for next chunk context
            lines = [line.strip() for line in cleaned_chunk.strip().split('\n') if line.strip()]
            if lines:
                prior_lines = "\n".join(lines[-2:])  # Keep last 2 lines for context
        
        return "\n".join(cleaned_chunks)
