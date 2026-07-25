from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"

embedding_model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    embedding = embedding_model.encode(text)
    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = embedding_model.encode(texts)
    return embeddings.tolist()