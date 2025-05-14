# readcast

This Python script automates the process of downloading, transcribing, and cleaning up podcast episodes to generate readable, dialogue-formatted transcripts.

## What It Does
Given a podcast episode URL, the script:

    Downloads the episode audio

    Transcribes it using OpenAI Whisper

    Cleans and formats the transcript

        Applies proper grammar, punctuation, and paragraphing

        Attempts to distinguish between two speakers and formats the result as a readable dialogue

        Produces output like:

        Host: What’s your take on this?  
        Guest: I think it’s important to look at the data.  

    Note: Speaker detection is only designed for two-speaker podcasts. Results may be inaccurate for group discussions.

## Why Use This?

    Surprisingly effective for turning raw audio into clean transcripts

    Much more cost-effective than subscribing to AI-powered transcription platforms

    No monthly fee – just pay for OpenAI API usage when transcribing

    Open and extensible – built in Python for easy tinkering

## Work In Progress

While functional, this repository is still evolving. Planned improvements include:

    - Creating a lightweight, local RAG (Retrieval-Augmented Generation) engine to let you query the episode ("What did they say about glucose metabolism?")

    - Smarter chunking and context tracking

Feel free to fork, customize, or suggest improvements.
