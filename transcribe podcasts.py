
import requests
import re
import os
from urllib.parse import urljoin
import requests
import whisper
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from docx import Document
from bs4 import BeautifulSoup
import openai
import tiktoken

#%%
podcast_episode_url = "<PODCAST URL>"
download_folder="downloads"
transcript_folder="transcripts"

def get_episode_title_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Try Open Graph <meta property="og:title">
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"]

    # Try <meta name="title">
    meta_title = soup.find("meta", attrs={"name": "title"})
    if meta_title and meta_title.get("content"):
        return meta_title["content"]

    # Fall back to <title> tag
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return "untitled_episode"

podcast_title = re.sub(r'[^\x00-\x7F]+', '', get_episode_title_from_page(podcast_episode_url))
# Step 2: Collapse multiple spaces into a single space
podcast_title = re.sub(r'\s+', ' ', podcast_title).strip()
#convert "&"" to "and"
podcast_title = podcast_title.replace("&", "And").title()
podcast_title = podcast_title.replace(":", ",")
podcast_title = podcast_title.replace("-", ",")

print(podcast_title)
#%%

def download_unique_mp3s_with_titles(url, download_folder=download_folder, transcript_folder=transcript_folder, podcast_title=podcast_title):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to load page: {response.status_code}")
        return

    html = response.text

    # Find all .mp3 links using regex and keep only unique ones
    raw_links = re.findall(r'https?://[^\s"\']+\.mp3', html)
    unique_links = list(set(raw_links))

    if not unique_links:
        print("No .mp3 links found.")
        return

    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(transcript_folder, exist_ok=True)

    safe_titles = []

    for i, mp3_url in enumerate(unique_links):
        temp_filename = os.path.join(download_folder, f"temp_{i}.mp3")
        print(f"Downloading: {mp3_url}")

        try:
            # Download the MP3
            r = requests.get(mp3_url, stream=True)
            with open(temp_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Extract title from metadata
            audio = MP3(temp_filename, ID3=EasyID3)
            title = audio.get('title', [f'podcast_{i+1}'])[0]
            safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()
            safe_titles.append(safe_title)
            # final_mp3_path = os.path.join(download_folder, f"{safe_title}.mp3")
            final_mp3_path = os.path.join(download_folder, f"{podcast_title}.mp3")

            # Rename file using title
            os.rename(temp_filename, final_mp3_path)
            print(f"Saved as: {final_mp3_path}")

            # Save empty transcript file as a placeholder
            # transcript_path = os.path.join(transcript_folder, f"{safe_title}.txt")
            # with open(transcript_path, 'w') as tf:
            #     tf.write(f"Transcript placeholder for: {safe_title}\n")

        except Exception as e:
            print(f"Error processing {mp3_url}: {e}")
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    return safe_titles

# Example usage:
# podcast_title = download_unique_mp3s_with_titles(podcast_episode_url)[0]
download_unique_mp3s_with_titles(podcast_episode_url)

#%%
file_name = podcast_title
mp3_path_name = os.path.join(download_folder, f"{file_name}.mp3")
transcript_path_name_doc = os.path.join(transcript_folder, f"{file_name}.docx")

# Load Whisper model and transcribe
model = whisper.load_model("base")  # "tiny", "small", "medium", "large" also work
result = model.transcribe(mp3_path_name)

print(result['text'])

# Save transcript to Word document
doc = Document()
doc.add_heading(file_name, level=1)
doc.add_paragraph(result['text'])
doc.save(transcript_path_name_doc)

transcript_path_name_txt= os.path.join(transcript_folder, f"{file_name}.txt")
with open(transcript_path_name_txt, "w", encoding="utf-8") as f:
    f.write(result['text'])

#delete mp3 file
os.remove(mp3_path_name)

#%%
# NEXT STEPS:
# extract title, description, and episode number from the podcast page
#use gpt 4o-mini to clean up the transcript, chunk by chunk
# then, have gpt-4o-mini stitch the chunks together by giving it the last part of the previous chunk and the first part of the next chunk
#or, extract the last ~50 words from the prior chunk trasncript and include that in the prompt for the next chunk. 
#gpt 4o-mini supposedly has 35K input token limit. translates to 25K words. output token limit is 16K, so ~12K words 







#Fetch OpenAI API key
#This key needs to be created on OpenAI's page, then saved as an environmental variable on your computer
api_key = os.getenv("OPENAI_API_KEY")

#%%
# Function to split long transcription into smaller chunks
def split_into_chunks(text, max_tokens=2000):
    encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4's tokenizer
    tokens = encoder.encode(text)
    chunks = []
    
    # Split tokens into chunks that fit the model's token limit
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i+max_tokens]
        chunks.append(encoder.decode(chunk))
    
    return chunks

#%%
# Function to clean up each chunk of transcription using GPT-4 API
def clean_transcription_chunk(raw_transcription_chunk):
    prompt = f"""
    Clean up the following transcription to make it readable, with proper grammar, punctuation, and paragraphs:\n\n{raw_transcription_chunk}.

    Make 
    Format the output as a transcript, like the following:
    Chris: What is your favorite color?
    Joe: My favorite color is blue.
    Chris: Cool.   
    """

    response = openai.Completion.create(
        engine="gpt-4",  # You can also use "gpt-4" or other available variants
        prompt=prompt,
        max_tokens=7000,  # Limit the output to 2000 tokens
        temperature=0.7,  # Adjust temperature for creativity
        top_p=1.0,
        n=1,
        stop=["\n"]
    )
    
    cleaned_text = response.choices[0].text.strip()
    return cleaned_text

# Function to process a long transcription (split into chunks, clean each, and combine them)
def clean_long_transcription(long_transcription, max_tokens=2000):
    # Split transcription into manageable chunks
    chunks = split_into_chunks(long_transcription, max_tokens)
    
    # Clean up each chunk and combine results
    cleaned_chunks = [clean_transcription_chunk(chunk) for chunk in chunks]
    cleaned_transcription = "\n".join(cleaned_chunks)
    
    return cleaned_transcription





#%%

long_transcription = result['text']

cleaned_transcription = clean_long_transcription(long_transcription)
print("Cleaned Transcription:\n", cleaned_transcription)






#%%

# Function to clean up transcription using GPT-4 API
def clean_transcription(raw_transcription):
    prompt = f"Clean up the following transcription to make it readable, with proper grammar, punctuation, and paragraphs:\n\n{raw_transcription}"

    response = openai.Completion.create(
        engine="gpt-4o-mini",  # You can also use "gpt-4" or any other available variant if needed
        prompt=prompt,
        max_tokens=2000,  # Limit the output to 2000 tokens (feel free to adjust)
        temperature=0.7,  # Adjust temperature to control creativity (lower = more deterministic)
        top_p=1.0,
        n=1,
        stop=["\n"]  # End the output after a line break
    )
    
    # Extract the cleaned-up text from the response
    cleaned_text = response.choices[0].text.strip()
    return cleaned_text

# Example usage
raw_transcription = result['text']

cleaned_transcription = clean_transcription(raw_transcription)
print("Cleaned Transcription:\n", cleaned_transcription)

with open(f"{file_name}_cleaned_transcription.txt", "w", encoding="utf-8") as f:
    f.write(result['text'])

