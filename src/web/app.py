"""Streamlit web application for podcast and YouTube transcription."""

import streamlit as st
import os
import time
from typing import Optional

# Add the src directory to the path so we can import modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.podcast_processor import TranscriptProcessor
from core.config import Config


class TranscriptApp:
    """Main Streamlit application class supporting multiple transcript sources."""
    
    def __init__(self):
        self.processor = None
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Transcript Generator",
            page_icon="🎙️",
            layout="centered",
            initial_sidebar_state="expanded"
        )
    
    def run(self):
        """Run the main application."""
        st.title("🎙️ Transcript Generator")
        st.markdown("Transform podcasts and YouTube videos into clean, readable transcripts with speaker identification.")
        
        # Initialize session state
        self._initialize_session_state()
        
        # Sidebar with configuration and status
        self.render_sidebar()
        
        # Main content
        if not st.session_state.processing:
            self.render_input_form()
        else:
            self.render_processing_status()
        
        # Display results if available
        if st.session_state.result:
            self.render_results()
    
    def _initialize_session_state(self):
        """Initialize session state variables."""
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'result' not in st.session_state:
            st.session_state.result = None
        if 'source_type' not in st.session_state:
            st.session_state.source_type = "podcast"
    
    def render_sidebar(self):
        """Render sidebar with configuration and status."""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Check API key
            if not Config.OPENAI_API_KEY:
                st.error("❌ OpenAI API key not found!")
                st.markdown("Please set the `OPENAI_API_KEY` environment variable.")
                return
            
            st.success("✅ OpenAI API key configured")
            
            # Model settings
            st.subheader("Model Settings")
            st.info(f"Whisper Model: `{Config.WHISPER_MODEL}`")
            st.info(f"OpenAI Model: `{Config.OPENAI_MODEL}`")
            
            # Token limits
            st.subheader("Processing Limits")
            st.info(f"Max Input Tokens: `{Config.MAX_TOKENS_INPUT}`")
            st.info(f"Max Output Tokens: `{Config.MAX_TOKENS_OUTPUT}`")
            
            # Storage info
            st.subheader("Storage")
            st.info(f"Downloads: `{Config.DOWNLOAD_FOLDER}`")
            st.info(f"Transcripts: `{Config.TRANSCRIPT_FOLDER}`")
            
            # Supported sources
            if self.processor:
                st.subheader("Supported Sources")
                for source_type, description in self.processor.get_supported_sources().items():
                    st.info(f"**{source_type.title()}**: {description}")
    
    def render_input_form(self):
        """Render the main input form with source toggle."""
        st.header("📝 Input Content URL")
        
        # Source selection toggle
        col1, col2 = st.columns(2)
        with col1:
            podcast_selected = st.button(
                "🎧 Podcast", 
                type="primary" if st.session_state.source_type == "podcast" else "secondary",
                use_container_width=True
            )
        with col2:
            youtube_selected = st.button(
                "📺 YouTube", 
                type="primary" if st.session_state.source_type == "youtube" else "secondary",
                use_container_width=True
            )
        
        # Update source type based on button clicks
        if podcast_selected:
            st.session_state.source_type = "podcast"
            st.rerun()
        elif youtube_selected:
            st.session_state.source_type = "youtube"
            st.rerun()
        
        # Show current selection
        source_type = st.session_state.source_type
        if source_type == "podcast":
            st.info("🎧 **Podcast Mode**: Apple Podcasts, Spotify, or direct MP3 links")
            placeholder = "https://podcasts.apple.com/us/podcast/episode-id"
            help_text = "Enter the URL of the podcast episode you want to transcribe"
        else:
            st.info("📺 **YouTube Mode**: YouTube video URLs")
            placeholder = "https://www.youtube.com/watch?v=VIDEO_ID"
            help_text = "Enter the URL of the YouTube video you want to transcribe"
        
        with st.form("transcript_form"):
            url = st.text_input(
                f"{source_type.title()} URL",
                placeholder=placeholder,
                help=help_text
            )
            
            submitted = st.form_submit_button(
                "🚀 Generate Transcript",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                if not url.strip():
                    st.error("Please enter a valid URL")
                    return
                
                # Initialize processor if needed
                if not self.processor:
                    self.processor = TranscriptProcessor()
                
                # Validate URL
                if not self.processor.validate_url(source_type, url):
                    st.error(f"Please enter a valid {source_type} URL")
                    return
                
                # Start processing
                st.session_state.source_type = source_type
                st.session_state.url = url
                st.session_state.processing = True
                st.session_state.result = None
                st.rerun()
    
    def render_processing_status(self):
        """Render processing status with progress indicators."""
        st.header("⏳ Processing Content")
        
        # Show what we're processing
        source_type = st.session_state.get('source_type', 'content')
        url = st.session_state.get('url', '')
        
        st.info(f"Processing {source_type}: {url[:100]}{'...' if len(url) > 100 else ''}")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize processor
            status_text.text("Initializing processor...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            if not self.processor:
                self.processor = TranscriptProcessor()
            
            # Process the transcript
            status_text.text("Extracting transcript and metadata...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            status_text.text("Identifying speakers...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("Cleaning transcript...")
            progress_bar.progress(70)
            time.sleep(2.0)
            
            status_text.text("Generating documents...")
            progress_bar.progress(90)
            time.sleep(0.5)
            
            # Final processing
            raw_doc_path, cleaned_doc_path = self.processor.process_transcript(
                st.session_state.source_type, st.session_state.url
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Processing completed!")
            
            # Store results
            st.session_state.result = {
                'raw_doc_path': raw_doc_path,
                'cleaned_doc_path': cleaned_doc_path,
                'success': True,
                'source_type': st.session_state.source_type
            }
            st.session_state.processing = False
            
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            progress_bar.progress(0)
            status_text.text("❌ Processing failed!")
            st.error(f"Error: {str(e)}")
            
            st.session_state.result = {
                'success': False,
                'error': str(e),
                'source_type': st.session_state.source_type
            }
            st.session_state.processing = False
            
            if st.button("🔄 Try Again"):
                st.session_state.result = None
                st.rerun()
    
    def render_results(self):
        """Render processing results."""
        if not st.session_state.result:
            return
        
        result = st.session_state.result
        source_type = result.get('source_type', 'content')
        
        if result['success']:
            st.header("✅ Processing Complete!")
            st.success(f"Your {source_type} transcript has been generated successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 Raw Transcript")
                raw_path = result['raw_doc_path']
                filename = os.path.basename(raw_path)
                
                if os.path.exists(raw_path):
                    with open(raw_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download Raw Transcript",
                            data=f.read(),
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Raw transcript file not found")
            
            with col2:
                st.subheader("🧹 Cleaned Transcript")
                cleaned_path = result['cleaned_doc_path']
                filename = os.path.basename(cleaned_path)
                
                if os.path.exists(cleaned_path):
                    with open(cleaned_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download Cleaned Transcript",
                            data=f.read(),
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Cleaned transcript file not found")
            
            # New transcript button
            if st.button("🆕 Process Another", use_container_width=True):
                st.session_state.result = None
                st.session_state.url = None
                st.rerun()
        
        else:
            st.header("❌ Processing Failed")
            st.error(f"An error occurred: {result['error']}")
            
            if st.button("🔄 Try Again", use_container_width=True):
                st.session_state.result = None
                st.rerun()


def main():
    """Main entry point for the Streamlit app."""
    app = TranscriptApp()
    app.run()


if __name__ == "__main__":
    main()
