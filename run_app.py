#!/usr/bin/env python3
"""Entry point for the Podcast Transcriber web application."""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", "src/web/app.py"]
    sys.exit(stcli.main())
