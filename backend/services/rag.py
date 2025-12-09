import pickle
from pathlib import Path
from typing import List

import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

EMBEDDINGS_PATH = PROCESSED_DIR / "egc_embeddings.faiss"
PASSAGES_PATH = PROCESSED_DIR / "egc_passages.pkl"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_model = None
_index = None
_passages: List[str] | None = None


def _ensure_loaded():
    global _model, _index, _passages
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    if _index is None or _passages is None:
        if not EMBEDDINGS_PATH.exists() or not PASSAGES_PATH.exists():
            # Pas d'index: on laisse RAG désactivé silencieusement
            return
        _index = faiss.read_index(str(EMBEDDINGS_PATH))
        with PASSAGES_PATH.open("rb") as f:
            _passages = pickle.load(f)


def retrieve_relevant_chunks(query: str, top_k: int = 4) -> List[str]:
    _ensure_loaded()
    if _index is None or _passages is None:
        return []

    query_vec = _model.encode([query], convert_to_numpy=True)
    query_vec = query_vec.astype("float32")

    distances, indices = _index.search(query_vec, top_k)
    idxs = indices[0]

    chunks: List[str] = []
    for idx in idxs:
        if 0 <= idx < len(_passages):
            chunks.append(_passages[idx])

    return chunks
