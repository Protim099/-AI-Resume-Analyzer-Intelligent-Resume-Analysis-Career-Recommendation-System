"""NLP preprocessing with spaCy (graceful fallback if the model is missing)."""
import logging
import re
import unicodedata

logger = logging.getLogger(__name__)
_nlp = None
BULLET_RE = re.compile(r"^\s*[\u2022\u25cf\u25aa\u25e6\u25a0\u25ba\u2023\u2043\u2219\u00b7*\-\u2013\u2014]+\s*")


def get_nlp():
    global _nlp
    if _nlp is not None:
        return _nlp
    import spacy
    try:
        _nlp = spacy.load("en_core_web_sm", disable=["parser"])
        _nlp.max_length = 300_000
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found - run: python -m spacy download en_core_web_sm. "
                       "Using a blank pipeline (name detection falls back to heuristics).")
        _nlp = spacy.blank("en")
    return _nlp


def has_ner() -> bool:
    return "ner" in get_nlp().pipe_names


def clean_text(text: str) -> str:
    """Normalise unicode, bullets and whitespace while keeping line structure."""
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("\r", "\n").replace("\t", " ").replace("\x0c", "\n")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \u00a0]+", " ", line).strip()
        if BULLET_RE.match(line) and len(line) > 2:
            line = "\u2022 " + BULLET_RE.sub("", line)
        lines.append(line)
    out = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def lemmatize_for_similarity(text: str) -> str:
    """Lower-cased lemmas without stop words/punctuation, used for TF-IDF and embeddings."""
    nlp = get_nlp()
    doc = nlp(text[:100_000])
    tokens = [(t.lemma_ or t.text).lower() for t in doc
              if not t.is_stop and not t.is_punct and not t.like_num and len(t.text) > 1 and not t.is_space]
    return " ".join(tokens)
