"""Streamlit web application for podcast transcription."""

import streamlit as st
import os
import time
from typing import Optional

# Add the src directory to the path so we can import modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.podcast_processor import PodcastProcessor
from core.config import Config


class PodcastTranscriberApp:
    """Main Streamlit application class."""
    
    def __init__(self):
        self.processor = None
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=Config.WEB_TITLE,
            page_icon="🎙️",
            layout="centered",
            initial_sidebar_state="expanded"
        )
    
    def run(self):
        """Run the main application."""
        st.title("🎙️ Podcast Transcriber")
        st.markdown("Transform podcast episodes into clean, readable transcripts with speaker identification.")
        
        # Initialize session state
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'result' not in st.session_state:
            st.session_state.result = None
        
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
    
    # def render_input_form(self):
    #     """Render the main input form."""
    #     st.header("📝 Input Podcast URL")
        
    #     with st.form("podcast_form"):
    #         url = st.text_input(
    #             "Podcast Episode URL",
    #             placeholder="https://podcasts.apple.com/us/podcast/episode-id",
    #             help="Enter the URL of the podcast episode you want to transcribe"
    #         )
            
    #         submitted = st.form_submit_button(
    #             "🚀 Generate Transcript",
    #             type="primary",
    #             use_container_width=True
    #         )
            
    #         if submitted:
    #             if not url.strip():
    #                 st.error("Please enter a valid URL")
    #                 return
                
    #             if not self._validate_url(url):
    #                 st.error("Please enter a valid podcast URL")
    #                 return
                
    #             # Start processing
    #             st.session_state.processing = True
    #             st.session_state.result = None
    #             st.rerun()
    
    def render_input_form(self):
        """Render the main input form."""
        st.header("📝 Input Podcast URL")
        
        with st.form("podcast_form"):
            url = st.text_input(
                "Podcast Episode URL",
                placeholder="https://podcasts.apple.com/us/podcast/episode-id",
                help="Enter the URL of the podcast episode you want to transcribe"
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
                
                if not self._validate_url(url):
                    st.error("Please enter a valid podcast URL")
                    return
                
                # Store URL and start processing
                st.session_state.podcast_url = url
                st.session_state.processing = True
                st.session_state.result = None
                st.rerun()

    def render_processing_status(self):
        """Render processing status with progress indicators."""
        st.header("⏳ Processing Podcast")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize processor
            status_text.text("Initializing processor...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            if not self.processor:
                self.processor = PodcastProcessor()
            
            # Process the podcast
            status_text.text("Processing podcast URL...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            # Get URL from session state (we need to store it)
            if 'podcast_url' not in st.session_state:
                st.error("No URL found in session state")
                st.session_state.processing = False
                st.rerun()
                return
            
            url = st.session_state.podcast_url
            
            # Process with progress updates
            status_text.text("Extracting metadata...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            status_text.text("Identifying speakers...")
            progress_bar.progress(40)
            time.sleep(0.5)
            
            status_text.text("Downloading audio...")
            progress_bar.progress(50)
            time.sleep(1.0)
            
            status_text.text("Transcribing audio...")
            progress_bar.progress(70)
            time.sleep(2.0)
            
            status_text.text("Cleaning transcript...")
            progress_bar.progress(85)
            time.sleep(1.0)
            
            status_text.text("Generating documents...")
            progress_bar.progress(95)
            time.sleep(0.5)
            
            # Final processing
            raw_doc_path, cleaned_doc_path = self.processor.process_podcast(url)
            
            progress_bar.progress(100)
            status_text.text("✅ Processing completed!")
            
            # Store results
            st.session_state.result = {
                'raw_doc_path': raw_doc_path,
                'cleaned_doc_path': cleaned_doc_path,
                'success': True
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
                'error': str(e)
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
        
        if result['success']:
            st.header("✅ Processing Complete!")
            st.success("Your podcast transcript has been generated successfully!")
            
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
            if st.button("🆕 Process Another Podcast", use_container_width=True):
                st.session_state.result = None
                st.session_state.podcast_url = None
                st.rerun()
        
        else:
            st.header("❌ Processing Failed")
            st.error(f"An error occurred: {result['error']}")
            
            if st.button("🔄 Try Again", use_container_width=True):
                st.session_state.result = None
                st.rerun()
    
    def _validate_url(self, url: str) -> bool:
        """Basic URL validation."""
        if not url:
            return False
        
        url = url.strip()
        return (
            url.startswith('http://') or 
            url.startswith('https://') and
            ('podcasts.apple.com' in url or 'spotify.com' in url or url.endswith('.mp3'))
        )


def main():
    """Main entry point for the Streamlit app."""
    app = PodcastTranscriberApp()
    
    # Store URL in session state when form is submitted
    if 'podcast_url' not in st.session_state:
        st.session_state.podcast_url = None
    
    # Capture URL from form submission
    # url_input = st.text_input(
    #     "Podcast Episode URL",
    #     placeholder="https://podcasts.apple.com/us/podcast/episode-id",
    #     help="Enter the URL of the podcast episode you want to transcribe",
    #     key="url_input"
    # )
    
    # if st.button("🚀 Generate Transcript", type="primary", use_container_width=True):
    #     if url_input.strip() and app._validate_url(url_input):
    #         st.session_state.podcast_url = url_input
    #         st.session_state.processing = True
    #         st.session_state.result = None
    #         st.rerun()
    #     elif url_input.strip():
    #         st.error("Please enter a valid podcast URL")
    
    # Run the main app logic
    app.run()


if __name__ == "__main__":
    main()
