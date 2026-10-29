import re
from pathlib import Path


# --------------------------------------------------
# POLICY DOCUMENT LOCATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
POLICY_FILE = BASE_DIR / "data" / "student_policy.txt"


# --------------------------------------------------
# TEXT PREPARATION
# --------------------------------------------------

def normalise(text):
    """Convert text to lowercase and remove extra whitespace."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def split_into_chunks(text, max_chars=700):
    """Split the policy document into smaller chunks."""

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []

    for paragraph in paragraphs:

        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue

        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        current = ""

        for sentence in sentences:

            if len(current) + len(sentence) + 1 <= max_chars:
                current = f"{current} {sentence}".strip()

            else:
                if current:
                    chunks.append(current)

                current = sentence

        if current:
            chunks.append(current)

    return chunks


def query_terms(question):
    """Extract meaningful words from the question."""

    stop_words = {
        "a", "an", "the", "is", "are", "was", "were",
        "i", "my", "me", "we", "our", "you", "your",
        "what", "how", "when", "where", "why", "do",
        "does", "did", "should", "can", "could", "would",
        "please", "if", "for", "to", "of", "in", "on",
        "at", "and", "or", "be", "about", "tell",
        "explain", "current",
    }

    words = re.findall(r"[a-z0-9]+", normalise(question))

    return [
        word for word in words
        if word not in stop_words and len(word) > 1
    ]


# --------------------------------------------------
# POLICY SEARCH
# --------------------------------------------------

def search_policy(question, top_k=3):
    """
    Search the policy document and return the most relevant chunks.

    Each result contains text and a chunk ID.
    """

    if not POLICY_FILE.exists():
        raise FileNotFoundError(
            f"Policy document not found: {POLICY_FILE}"
        )

    text = POLICY_FILE.read_text(encoding="utf-8").strip()

    if not text:
        return []

    chunks = split_into_chunks(text)

    if not chunks:
        return []

    terms = query_terms(question)

    if not terms:
        return []

    scored_chunks = []

    for index, chunk in enumerate(chunks):

        chunk_text = normalise(chunk)
        score = 0

        for term in terms:
            if re.search(
                rf"\b{re.escape(term)}\b",
                chunk_text,
            ):
                score += 1

        if score > 0:
            scored_chunks.append(
                {
                    "text": chunk,
                    "score": score,
                    "chunk_id": index,
                }
            )

    scored_chunks.sort(
        key=lambda item: (item["score"], -item["chunk_id"]),
        reverse=True,
    )

    return [
        {
            "text": item["text"],
            "chunk_id": item["chunk_id"],
        }
        for item in scored_chunks[:max(1, top_k)]
    ]