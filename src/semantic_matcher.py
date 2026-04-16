from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")


def compute_semantic_score(resume_text: str, job_text: str) -> float:
    embeddings = model.encode([resume_text, job_text])
    resume_emb = np.array(embeddings[0]).reshape(1, -1)
    job_emb = np.array(embeddings[1]).reshape(1, -1)
    score = cosine_similarity(resume_emb, job_emb)[0][0]
    return round(float(score) * 100, 2)