# Transcript Generator

A professional web application that transforms podcasts and YouTube videos into clean, readable transcripts with speaker identification and automatic Word document generation.

## Features

- **Dual Source Support**: Process both podcast episodes and YouTube videos
- **Simple Web Interface**: Minimalist browser-based UI with source toggle and URL input
- **Automatic Transcription**: Uses OpenAI Whisper for podcasts, built-in transcripts for YouTube
- **Speaker Identification**: Automatically identifies hosts, co-hosts, and guests using OpenAI
- **Smart Cleaning**: Refines transcripts using AI for better readability
- **Word Document Export**: Generates formatted Word documents with speaker labels
- **Modular Architecture**: Clean, maintainable codebase with abstract source pattern
- **Error Handling**: Comprehensive error handling for invalid URLs, API failures, etc.

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **FFmpeg** installed for audio processing (podcasts only)
3. **OpenAI API key** for transcription cleaning and speaker identification

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   *Note: On Windows, use `set OPENAI_API_KEY=your-openai-api-key-here`*

4. **Run the application**:
   ```bash
   python run_app.py
   ```

The application will open in your web browser at `http://localhost:8501`

## Usage

1. **Open the web interface** in your browser
2. **Choose your source**:
   - Click **🎧 Podcast** for podcast episodes
   - Click **📺 YouTube** for YouTube videos
3. **Enter the URL** for your content
4. **Click "Generate Transcript"** to start processing
5. **Wait for processing** to complete (progress will be shown)
6. **Download the results**:
   - Raw transcript (direct output)
   - Cleaned transcript (AI-refined with speaker labels)

## Supported Sources

### Podcast Episodes
- **Apple Podcasts**: Full episode pages
- **Spotify**: Podcast episode pages  
- **Direct MP3 URLs**: Any direct audio file links

### YouTube Videos
- **YouTube**: All standard YouTube video URLs
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`

## Architecture

The application uses a modular, source-agnostic architecture:

```
src/
├── core/
│   ├── transcript_source.py     # Abstract base class for sources
│   ├── podcast_source.py        # Podcast implementation (Whisper)
│   ├── youtube_source.py        # YouTube implementation (transcript API)
│   ├── podcast_processor.py     # Main orchestrator (supports both)
│   ├── speaker_identifier.py    # Shared speaker identification
│   ├── transcript_cleaner.py    # Shared transcript cleaning
│   └── document_generator.py   # Shared document generation
└── web/
    └── app.py                  # Streamlit web interface with source toggle
```

### Processing Pipeline

Both sources follow the same pipeline:

1. **Source Extraction**: Extract transcript and metadata from source
2. **Speaker Identification**: Identify speakers using OpenAI
3. **Transcript Cleaning**: Apply AI-powered cleaning and formatting
4. **Document Generation**: Create Word documents with metadata
5. **Download**: Provide both raw and cleaned transcripts

## Project Structure

```
readcast/
├── src/
│   ├── core/                    # Core processing modules
│   │   ├── transcript_source.py  # Abstract source interface
│   │   ├── podcast_source.py     # Podcast implementation
│   │   ├── youtube_source.py     # YouTube implementation
│   │   ├── config.py           # Application configuration
│   │   ├── metadata_extractor.py # Podcast metadata extraction
│   │   ├── speaker_identifier.py  # Speaker identification
│   │   ├── audio_downloader.py    # Audio file downloading
│   │   ├── transcriber.py         # Whisper transcription
│   │   ├── transcript_cleaner.py  # AI-powered transcript cleaning
│   │   ├── document_generator.py  # Word document generation
│   │   └── podcast_processor.py   # Main orchestrator
│   └── web/
│       └── app.py              # Streamlit web interface
├── downloads/                  # Temporary audio files
├── transcripts/                # Generated Word documents
├── static/                     # Static web assets
├── requirements.txt            # Python dependencies
├── run_app.py                 # Application entry point
└── README.md                  # This file
```

## Configuration

The application can be configured by modifying `src/core/config.py`:

- **WHISPER_MODEL**: Whisper model size (`tiny`, `base`, `small`, `medium`, `large`)
- **OPENAI_MODEL**: OpenAI model for cleaning (`gpt-4o-mini` recommended)
- **MAX_TOKENS_INPUT/OUTPUT**: Token limits for processing chunks
- **File paths**: Download and transcript folders

## Error Handling

The application handles various error scenarios:

- **Invalid URLs**: Validates URLs for each source type
- **Network connectivity issues**: Handles download failures gracefully
- **Audio download failures**: Podcast-specific error handling
- **Transcription errors**: Both Whisper and YouTube transcript API errors
- **OpenAI API rate limits**: Proper error messages and retry suggestions
- **YouTube transcript unavailable**: Clear error messages for disabled transcripts
- **File system permissions**: Handles directory creation and file access issues

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"

# Run the app
python run_app.py
```

### Cloud Deployment (Optional)

The application is designed for easy deployment to cloud platforms:

1. **Heroku**: Add a `Procfile` with `web: streamlit run src/web/app.py`
2. **Railway**: Deploy as a Python web service
3. **AWS/GCP**: Containerize with Docker

## Performance Tips

- **Podcasts**: Use `base` Whisper model for balance of speed/accuracy, `large` for best quality
- **YouTube**: No audio processing needed - much faster than podcasts
- **Token Limits**: Adjust `MAX_TOKENS_INPUT` based on your OpenAI model limits
- **GPU Support**: Install PyTorch with CUDA for faster podcast transcription

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure the `OPENAI_API_KEY` environment variable is set
   - Check for typos in your API key

2. **"No .mp3 links found" (Podcasts)**
   - Verify the podcast URL is correct
   - Try a different podcast source (Apple Podcasts works best)

3. **"Transcripts are disabled for this video" (YouTube)**
   - The video doesn't have available transcripts
   - Try a different YouTube video

4. **"FFmpeg not found" (Podcasts only)**
   - Install FFmpeg: `brew install ffmpeg` (macOS) or `choco install ffmpeg` (Windows)
   - Not needed for YouTube videos

5. **Slow transcription (Podcasts only)**
   - Consider using a smaller Whisper model (`tiny` or `base`)
   - Ensure you have sufficient disk space for downloads
   - YouTube videos process much faster

### Logs and Debugging

The application provides detailed console output during processing. Check the terminal where you ran `python run_app.py` for error messages and progress updates.

## Key Differences Between Sources

| Feature | Podcasts | YouTube |
|---------|-----------|---------|
| **Transcription Method** | Whisper (audio processing) | Built-in transcript API |
| **Processing Speed** | Slower (audio download + transcription) | Fast (direct transcript access) |
| **Requirements** | FFmpeg required | No additional requirements |
| **Audio Quality** | Depends on audio source | Depends on YouTube's transcript |
| **Reliability** | High (works with any audio) | Medium (requires available transcript) |

## License

This project is provided as-is for educational and personal use. Please ensure you comply with the terms of service of podcast platforms, YouTube, and OpenAI when using this application.

## Contributing

Feel free to submit issues and enhancement requests! Key areas for improvement:

- Support for additional video platforms (Vimeo, etc.)
- Real-time processing status updates
- Batch processing of multiple episodes
- Additional output formats (PDF, plain text)
- Enhanced speaker diarization
- Language support for non-English content
