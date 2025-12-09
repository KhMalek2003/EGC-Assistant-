import pickle
from pathlib import Path
from typing import List

import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
SOURCE_DIR = DATA_DIR / "source_docs"
PROCESSED_DIR = DATA_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDINGS_PATH = PROCESSED_DIR / "egc_embeddings.faiss"
PASSAGES_PATH = PROCESSED_DIR / "egc_passages.pkl"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_source_texts() -> List[str]:
    texts: List[str] = []
    for file in SOURCE_DIR.glob("*.txt"):
        with file.open("r", encoding="utf-8") as f:
            content = f.read()
            texts.append(content)
    return texts


def simple_chunk(text: str, max_chars: int = 600) -> List[str]:
    """
    Découpe un long texte en morceaux de ~max_chars caractères.
    """
    chunks: List[str] = []
    current = []
    current_len = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if current_len + len(line) > max_chars and current:
            chunks.append(" ".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line) + 1

    if current:
        chunks.append(" ".join(current))

    return chunks


def build_index():
    print("Chargement des textes source...")
    texts = load_source_texts()
    if not texts:
        print("Aucun fichier trouvé dans data/source_docs/*.txt")
        return

    print("Découpage en chunks...")
    passages: List[str] = []
    for t in texts:
        passages.extend(simple_chunk(t))

    print(f"{len(passages)} passages générés.")

    print(f"Chargement du modèle d'embeddings ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Calcul des embeddings...")
    embeddings = model.encode(passages, convert_to_numpy=True, show_progress_bar=True)

    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings.astype("float32"))

    print(f"Enregistrement de l'index FAISS dans {EMBEDDINGS_PATH}...")
    faiss.write_index(index, str(EMBEDDINGS_PATH))

    print(f"Enregistrement des passages dans {PASSAGES_PATH}...")
    with PASSAGES_PATH.open("wb") as f:
        pickle.dump(passages, f)

    print("✅ Index RAG construit avec succès.")


if __name__ == "__main__":
    build_index()
