"""Resume <-> Job Description matching: skill overlap + semantic similarity + TF-IDF keyword similarity."""
import logging
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..config import settings
from .preprocessing import lemmatize_for_similarity
from .skill_extractor import extract_skills

logger = logging.getLogger(__name__)
_model = None
_model_failed = False


def _get_model():
    global _model, _model_failed
    if _model is not None or _model_failed or not settings.USE_EMBEDDINGS:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    except Exception as exc:  # offline / not installed
        logger.warning("Sentence-Transformers unavailable (%s). Falling back to TF-IDF similarity.", exc)
        _model_failed = True
    return _model


def _chunks(text: str, size: int = 160) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [text]


def _embed(text: str) -> np.ndarray:
    vecs = _get_model().encode(_chunks(text)[:12], normalize_embeddings=True)
    mean = vecs.mean(axis=0)
    return mean / (np.linalg.norm(mean) or 1.0)


def semantic_similarity(a: str, b: str) -> tuple[float, str]:
    """Return (score 0..1, method). Raw MiniLM cosine for related docs is ~0.3-0.75, so it is rescaled."""
    if _get_model() is not None:
        sim = float(np.dot(_embed(a), _embed(b)))
        return float(np.clip((sim - 0.15) / 0.6, 0, 1)), "sentence-transformers"
    return tfidf_similarity(a, b)[0], "tfidf-fallback"


def tfidf_similarity(a: str, b: str) -> tuple[float, list[str]]:
    la, lb = lemmatize_for_similarity(a), lemmatize_for_similarity(b)
    if not la.strip() or not lb.strip():
        return 0.0, []
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    m = vec.fit_transform([lb, la])  # row 0 = JD, row 1 = resume
    sim = float(cosine_similarity(m[0], m[1])[0][0])
    terms = np.array(vec.get_feature_names_out())
    jd_w, cv_w = m[0].toarray()[0], m[1].toarray()[0]
    idx = [i for i in np.argsort(-jd_w) if jd_w[i] > 0 and cv_w[i] == 0 and " " not in terms[i]
           and not re.search(r"\d", terms[i])][:15]
    return float(np.clip(sim / 0.5, 0, 1)), [str(terms[i]) for i in idx]


def match_resume_to_job(resume_text: str, resume_skills: list[str], jd_text: str) -> dict:
    jd_skills = extract_skills(jd_text)
    jd_names = [s["name"] for s in jd_skills]
    have = {s.lower() for s in resume_skills}
    matched = [s for s in jd_skills if s["name"].lower() in have]
    missing = [s for s in jd_skills if s["name"].lower() not in have]
    skill_tokens = {t for n in jd_names for t in re.split(r"[^a-z0-9]+", n.lower()) if t}
    generic = {"hire", "hiring", "strong", "build", "work", "team", "experience", "looking", "join", "candidate",
               "ability", "role", "job", "position", "required", "skill", "knowledge", "understanding", "using"}
    skill_score = len(matched) / len(jd_names) if jd_names else None
    semantic, method = semantic_similarity(resume_text, jd_text)
    keyword, missing_keywords = tfidf_similarity(resume_text, jd_text)
    missing_keywords = [k for k in missing_keywords if len(k) > 3 and k not in skill_tokens and k not in generic][:10]
    if skill_score is None:
        final = 0.65 * semantic + 0.35 * keyword
    else:
        final = 0.45 * skill_score + 0.35 * semantic + 0.20 * keyword
    return {
        "job_match_score": round(final * 100, 1),
        "skill_match_score": None if skill_score is None else round(skill_score * 100, 1),
        "semantic_score": round(semantic * 100, 1),
        "keyword_score": round(keyword * 100, 1),
        "similarity_method": method,
        "matched_skills": matched, "missing_skills": missing,
        "missing_keywords": missing_keywords, "jd_skills": jd_names,
    }
