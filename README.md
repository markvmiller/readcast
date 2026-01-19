# Podcast Transcriber

A professional web application that transforms podcast episodes into clean, readable transcripts with speaker identification and automatic Word document generation.

## Features

- **Simple Web Interface**: Minimalist browser-based UI with just a URL input and download button
- **Automatic Transcription**: Uses OpenAI Whisper for high-quality audio transcription
- **Speaker Identification**: Automatically identifies hosts, co-hosts, and guests using OpenAI
- **Smart Cleaning**: Refines transcripts using AI for better readability
- **Word Document Export**: Generates formatted Word documents with speaker labels
- **Error Handling**: Comprehensive error handling for invalid URLs, API failures, etc.
- **Modular Design**: Clean, maintainable codebase suitable for cloud deployment

## Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **FFmpeg** installed for audio processing
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
2. **Enter a podcast episode URL** (Apple Podcasts, Spotify, or direct MP3 links)
3. **Click "Generate Transcript"** to start processing
4. **Wait for processing** to complete (progress will be shown)
5. **Download the results**:
   - Raw transcript (direct Whisper output)
   - Cleaned transcript (AI-refined with speaker labels)

## Project Structure

```
readcast/
├── src/
│   ├── core/                    # Core processing modules
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

## Supported Sources

- **Apple Podcasts**: Full episode pages
- **Spotify**: Podcast episode pages
- **Direct MP3 URLs**: Any direct audio file links

## Error Handling

The application handles various error scenarios:

- Invalid URLs
- Network connectivity issues
- Audio download failures
- Transcription errors
- OpenAI API rate limits
- File system permissions

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

- **Whisper Model**: Use `base` for balance of speed/accuracy, `large` for best quality
- **Token Limits**: Adjust `MAX_TOKENS_INPUT` based on your OpenAI model limits
- **GPU Support**: Install PyTorch with CUDA for faster transcription

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure the `OPENAI_API_KEY` environment variable is set
   - Check for typos in your API key

2. **"No .mp3 links found"**
   - Verify the podcast URL is correct
   - Try a different podcast source (Apple Podcasts works best)

3. **"FFmpeg not found"**
   - Install FFmpeg: `brew install ffmpeg` (macOS) or `choco install ffmpeg` (Windows)

4. **Slow transcription**
   - Consider using a smaller Whisper model (`tiny` or `base`)
   - Ensure you have sufficient disk space for downloads

### Logs and Debugging

The application provides detailed console output during processing. Check the terminal where you ran `python run_app.py` for error messages and progress updates.

## License

This project is provided as-is for educational and personal use. Please ensure you comply with the terms of service of podcast platforms and OpenAI when using this application.

## Contributing

Feel free to submit issues and enhancement requests! Key areas for improvement:

- Support for additional podcast platforms
- Real-time processing status updates
- Batch processing of multiple episodes
- Additional output formats (PDF, plain text)
- Speaker diarization improvements
