#%%
import os, chromadb
from docx import Document
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from typing import List


#%%
#Define parameters
transcript_folder = "transcripts"
# transcript_file_name = '#914 , Dr Ethan Kross , How To Stop Feeling Negative Emotions All The Time - CLEANED.docx' 
transcript_file_name = '#914 , Dr Ethan Kross , How To Stop Feeling Negative Emotions All The Time.docx' 
openai_model="gpt-4o-mini"

#Fetch OpenAI API key
api_key = os.getenv("OPENAI_API_KEY") #This key needs to be created on OpenAI's page, then saved as an environmental variable on your computer
if not api_key:
    raise RuntimeError("OpenAI API key must be supplied (env var or argument).")

max_tokens_input=8000 #determines the token size of transcription chunks to be fed into OpenAI's API at a time. Must be under input token limit.
max_tokens_output = max_tokens_input+4000

#%%
# Step 1: Extract text from Word doc
def extract_text(file_path):
    from docx import Document
    doc = Document(file_path)
    
    paragraphs = []
    for para in doc.paragraphs:
        # Split by newline if needed
        lines = para.text.strip().split('\n')
        for line in lines:
            if line.strip():
                paragraphs.append(line.strip())
    return paragraphs

paragraphs = extract_text(f"{transcript_folder}/{transcript_file_name}")
print(paragraphs)
#%%
from langchain.text_splitter import RecursiveCharacterTextSplitter

full_text = extract_text(f"{transcript_folder}/{transcript_file_name}")[0]  # first item if there's no paragraph breaks

# Initialize text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # tokens or characters (if not token-aware)
    chunk_overlap=100,    # preserve a bit of context between chunks
    separators=["\n\n", "\n", ".", "!", "?", " "]  # try to split at logical breaks
)

chunks = splitter.split_text(full_text)
#%%
# Step 2: Initialize ChromaDB
# Remove what is in the db, for developing purposes
import shutil
shutil.rmtree("./chroma_db", ignore_errors=True)

#%%
# New persistent client (this is the recommended approach now)
chroma_client = PersistentClient(path="./chroma_db")

# Set up embedding function
sentence_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or load a collection
collection = chroma_client.get_or_create_collection(
    name="docs",
    embedding_function=sentence_embedder
)

# %%
# Step 3: Add document text
# metadatas = [{"source": f"{transcript_file_name}.docx", "position": idx} for idx in range(len(paragraphs))]
# ids = [f"chunk-{idx}" for idx in range(len(paragraphs))]
metadatas = [{"source": f"{transcript_file_name}.docx", "position": idx} for idx in range(len(chunks))]
ids = [f"chunk-{idx}" for idx in range(len(chunks))]

collection.add(
    documents=chunks, #paragraphs, 
    metadatas=metadatas, ids=ids)

#%%
#test:
question = "What role does Ethan Kross suggest culture plays in regulating our emotions?"

# Perform semantic search
results = collection.query(
    query_texts=[question],
    n_results=5
)

# The result contains the most relevant chunks
relevant_chunks = results['documents'][0]

for chunk in relevant_chunks:
    print(chunk)

#%%

# You can now pass these chunks to your LLM (e.g., OpenAI or local model)
context = "\n".join(relevant_chunks)
prompt = f"Answer the question using the context below:\n\n{context}\n\nQuestion: {question}"

# Now pass this prompt to an LLM to get the answer

#%%
"""
Next steps:

"""