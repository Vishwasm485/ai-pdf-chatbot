import faiss
import numpy as np
import pickle

def create_faiss_index(vectors):
    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors))
    return index

def save_index(index, chunks, path="data/index/index.pkl"):
    with open(path, "wb") as f:
        pickle.dump((index, chunks), f)

def load_index(path="data/index/index.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)

def search(index, query_vector, k=3):
    D, I = index.search(np.array([query_vector]), k)
    return I[0]