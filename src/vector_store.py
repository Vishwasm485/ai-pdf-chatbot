import os
import pickle
import faiss
import numpy as np

INDEX_FILE = "data/faiss.index"
META_FILE = "data/meta.pkl"


# -------- CREATE INDEX --------
def create_faiss_index(vectors):

    vectors = np.array(vectors).astype("float32")

    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(vectors)

    return index


# -------- SAVE INDEX --------
def save_index(index, data):

    os.makedirs("data", exist_ok=True)

    faiss.write_index(index, INDEX_FILE)

    with open(META_FILE, "wb") as f:
        pickle.dump(data, f)


# -------- LOAD INDEX --------
def load_index():

    if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
        raise ValueError("Index not created yet. Upload and process a PDF first.")

    index = faiss.read_index(INDEX_FILE)

    with open(META_FILE, "rb") as f:
        data = pickle.load(f)

    return index, data


# -------- SEARCH --------
def search(index, query_vector, k=3):

    query_vector = np.array([query_vector]).astype("float32")

    D, I = index.search(query_vector, k)

    return I[0]