import fitz  # PyMuPDF
import faiss
import numpy as np
import os
import json
from txtai.embeddings import Embeddings

# Initialize txtai embeddings
embeddings_model = Embeddings()

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text_chunks = [page.get_text("text") for page in doc]
    return text_chunks

def get_embedding(text):
    """Generate embedding using txtai."""
    return embeddings_model.transform(text).tolist()

def store_embeddings(text_chunks, pdf_path, index_dir="index_files"):
    """Generate embeddings and store them in FAISS index, differentiating by PDF name."""
    
    os.makedirs(index_dir, exist_ok=True)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]  # Get the name of the PDF file without extension
    index_path = os.path.join(index_dir, f"{pdf_name}_vector.index")
    meta_path = os.path.join(index_dir, f"{pdf_name}_meta.json")
    
    embeddings = [get_embedding(chunk) for chunk in text_chunks if chunk.strip()]
    if not embeddings:
        print("Error: No valid embeddings generated. Check PDF content.")
        return
    
    embeddings = np.array(embeddings, dtype=np.float32)
    d = embeddings.shape[1]  # Embedding dimension
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    faiss.write_index(index, index_path)

    with open(meta_path, "w") as f:
        json.dump(text_chunks, f)
    
    print(f"Embeddings for {pdf_name} stored successfully.")

def load_index(pdf_name, index_dir="index_files"):
    index_path = os.path.join(index_dir, f"{pdf_name}_vector.index")
    meta_path = os.path.join(index_dir, f"{pdf_name}_meta.json")

    print(f"Loading index from: {index_path}")  # Print the path

    if not os.path.exists(index_path): # added to check if path exist
        print("path error")
        raise FileNotFoundError(f"Index file not found at: {index_path}")
    
    index = faiss.read_index(index_path)
    with open(meta_path, "r") as f:
        text_chunks = json.load(f)
    return index, text_chunks

def search(query, pdf_name, top_k=2, index_dir="index_files"):
    """Search for the most relevant text chunks using FAISS, based on a specific PDF."""
    index, text_chunks = load_index(pdf_name, index_dir)
    query_embedding = np.array([get_embedding(query)], dtype=np.float32)
    distances, indices = index.search(query_embedding, top_k)
    return [text_chunks[i] for i in indices[0]]

# ... (rest of the embedding and search functions: extract_text_from_pdf, get_embedding, store_embeddings, load_index, search - these are the same as in your original code)