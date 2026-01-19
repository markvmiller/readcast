import streamlit as st
import os
import time
from io import BytesIO
from typing import Tuple, Optional
from src.podcast_processor import PodcastProcessor
from src.config import Config
from src.utils import validate_url, format_file_size


# Configure Streamlit page
st.set_page_config(
    page_title="Podcast Transcriber",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .url-input {
        margin: 1rem 0;
    }
    .processing-status {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'processor' not in st.session_state:
        try:
            st.session_state.processor = PodcastProcessor()
        except Exception as e:
            st.error(f"Failed to initialize podcast processor: {e}")
            st.stop()
    
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    if 'results' not in st.session_state:
        st.session_state.results = None


def display_header():
    """Display the application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ Podcast Transcriber</h1>
        <p>Transform podcast episodes into clean, readable transcripts with speaker identification</p>
    </div>
    """, unsafe_allow_html=True)


def display_url_input():
    """Display the URL input section."""
    st.markdown("### Enter Podcast Episode URL")
    st.markdown("Paste the URL of a podcast episode (Apple Podcasts, Spotify, or other platforms)")
    
    url = st.text_input(
        "Podcast URL",
        placeholder="https://podcasts.apple.com/us/podcast/episode-id",
        key="podcast_url",
        help="Enter the full URL of the podcast episode you want to transcribe"
    )
    
    return url


def validate_and_process_url(url: str) -> bool:
    """Validate URL and start processing if valid."""
    if not url:
        st.warning("Please enter a podcast URL")
        return False
    
    if not validate_url(url):
        st.error("Please enter a valid URL")
        return False
    
    # Start processing
    st.session_state.processing = True
    st.session_state.results = None
    
    return True


def display_processing_status():
    """Display processing status and progress."""
    if not st.session_state.processing:
        return
    
    st.markdown('<div class="processing-status info">', unsafe_allow_html=True)
    st.markdown("### 🔄 Processing Podcast")
    st.markdown("Please wait while we process your podcast episode...")
    
    # Create a placeholder for status updates
    status_placeholder = st.empty()
    
    try:
        processor = st.session_state.processor
        
        # Update status
        status_placeholder.markdown("1️⃣ Extracting podcast metadata...")
        time.sleep(0.5)
        
        status_placeholder.markdown("2️⃣ Downloading audio file...")
        time.sleep(0.5)
        
        status_placeholder.markdown("3️⃣ Transcribing audio with Whisper...")
        time.sleep(1.0)
        
        status_placeholder.markdown("4️⃣ Identifying speakers...")
        time.sleep(0.5)
        
        status_placeholder.markdown("5️⃣ Cleaning and formatting transcript...")
        time.sleep(1.0)
        
        status_placeholder.markdown("6️⃣ Generating documents...")
        time.sleep(0.5)
        
        # Process the podcast
        cleaned_doc_path, raw_doc_path = processor.process_podcast_url(st.session_state.podcast_url)
        
        # Store results
        st.session_state.results = {
            'cleaned_doc_path': cleaned_doc_path,
            'raw_doc_path': raw_doc_path,
            'success': True
        }
        
        st.session_state.processing = False
        
        # Clear the status
        status_placeholder.empty()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show success message
        st.markdown('<div class="processing-status success">', unsafe_allow_html=True)
        st.success("✅ Podcast processing completed successfully!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Rerun to show results
        st.rerun()
        
    except Exception as e:
        st.session_state.processing = False
        st.session_state.results = {'success': False, 'error': str(e)}
        
        status_placeholder.empty()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="processing-status error">', unsafe_allow_html=True)
        st.error(f"❌ Processing failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


def display_results():
    """Display processing results and download options."""
    if not st.session_state.results or not st.session_state.results.get('success'):
        return
    
    results = st.session_state.results
    cleaned_doc_path = results['cleaned_doc_path']
    raw_doc_path = results['raw_doc_path']
    
    st.markdown("### 📄 Download Transcripts")
    
    # Create columns for download buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Clean transcript download
        if os.path.exists(cleaned_doc_path):
            with open(cleaned_doc_path, 'rb') as f:
                bytes_data = f.read()
            
            st.download_button(
                label="📥 Download Clean Transcript",
                data=bytes_data,
                file_name=os.path.basename(cleaned_doc_path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                help="Download the cleaned and formatted transcript with speaker identification"
            )
            
            # Show file info
            file_size = format_file_size(len(bytes_data))
            st.caption(f"File size: {file_size}")
    
    with col2:
        # Raw transcript download
        if os.path.exists(raw_doc_path):
            with open(raw_doc_path, 'rb') as f:
                bytes_data = f.read()
            
            st.download_button(
                label="📥 Download Raw Transcript",
                data=bytes_data,
                file_name=os.path.basename(raw_doc_path),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                help="Download the raw transcription without cleaning"
            )
            
            # Show file info
            file_size = format_file_size(len(bytes_data))
            st.caption(f"File size: {file_size}")
    
    st.markdown("---")
    st.markdown("### 📋 Processing Summary")
    
    # Display processing info
    processor = st.session_state.processor
    info = processor.get_processing_info()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Whisper Model", info['whisper_model'])
    
    with col2:
        st.metric("OpenAI Model", info['openai_model'])
    
    with col3:
        st.metric("Max Tokens", f"{info['max_tokens_input']:,}")


def display_sidebar():
    """Display sidebar information."""
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown("""
        This application transforms podcast episodes into clean, readable transcripts with:
        
        - 🎯 **Speaker Identification**: Automatically identifies hosts and guests
        - 🧹 **Smart Cleaning**: Uses AI to clean and format transcripts
        - 📄 **Word Documents**: Downloads as professional Word documents
        - 🚀 **Fast Processing**: Optimized pipeline for quick results
        """)
        
        st.markdown("### 🛠️ Configuration")
        try:
            processor = st.session_state.processor
            info = processor.get_processing_info()
            
            st.markdown(f"""
            - **Whisper Model**: {info['whisper_model']}
            - **OpenAI Model**: {info['openai_model']}
            - **Max Input Tokens**: {info['max_tokens_input']:,}
            - **Max Output Tokens**: {info['max_tokens_output']:,}
            """)
        except:
            st.markdown("Configuration not available")
        
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. **Enter URL**: Paste a podcast episode URL
        2. **Click Process**: Start the transcription process
        3. **Wait**: Processing takes 2-5 minutes
        4. **Download**: Get your Word documents
        
        **Note**: Make sure you have your OpenAI API key set as an environment variable.
        """)


def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # URL input section
    url = display_url_input()
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button(
            "🚀 Process Podcast",
            type="primary",
            disabled=st.session_state.processing,
            use_container_width=True
        )
    
    # Handle button click
    if process_button:
        if validate_and_process_url(url):
            st.rerun()
    
    # Display processing status
    display_processing_status()
    
    # Display results
    display_results()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<center><p>Made with ❤️ using Streamlit, Whisper, and OpenAI</p></center>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
