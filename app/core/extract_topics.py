import logging

import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

from app.core.supabase_client import supabase
from app.models.topic import Topic

logger = logging.getLogger(__name__)

# Exclude these generic words from the beginning
EXCLUDED_WORDS = {
    "committee",
    "meeting",
    "digital",
    "subcommittee",
    "eu",
    "european",
    "party",
    "ordinary",
    "democrats",
    "alliance",
    "group",
    "progressive",
    "delegation",
    "preparatory",
    "socialists",
    "parliament",
    "public",
    "subtitles",
    "europe",
    "act",
    "patriots",
    "en",
}

TABLE_NAME = "meeting_topics"

BATCH_SIZE = 500


def fetch_meetings_batch(offset: int, batch_size: int = BATCH_SIZE):
    """
    Fetch a batch of meetings from v_meetings.
    """
    resp = supabase.table("v_meetings").select("*").range(offset, offset + batch_size - 1).execute()
    return resp.data if resp.data else []


def extract_topics_from_meetings(n_clusters=15, top_n_keywords=20):
    """
    Extracts topics from all meetings in the database by:
    - Fetching meetings in batches
    - Extracting keywords from meeting texts
    - Clustering keyword embeddings to find representative topics
    - Storing the resulting topics in the meeting_topics table
    """
    offset = 0
    all_texts = []

    # Fetch meetings in batches
    while True:
        batch = fetch_meetings_batch(offset)
        if not batch:
            break

        texts = [
            f"{m.get('title', '')}. {m.get('description', '')}".strip()
            for m in batch
            if m.get("title") or m.get("description")
        ]
        all_texts.extend(texts)
        offset += BATCH_SIZE

    if not all_texts:
        return []

    # Extract keywords from all meetings
    kw_model = KeyBERT("all-MiniLM-L6-v2")
    all_keywords = []
    for text in all_texts:
        keywords = kw_model.extract_keywords(
            text, keyphrase_ngram_range=(1, 1), stop_words="english", top_n=top_n_keywords
        )
        all_keywords.extend([kw for kw, _ in keywords if kw.lower() not in EXCLUDED_WORDS])

    if not all_keywords:
        return []

    # Embed keywords and cluster them
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(all_keywords)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(embeddings)

    # Get a representative keyword for each cluster
    labels = kmeans.labels_
    for i in range(n_clusters):
        indices = np.where(labels == i)[0]
        if len(indices) > 0:
            topic = all_keywords[indices[0]].capitalize()
            try:
                supabase.table(TABLE_NAME).upsert(
                    Topic(
                        topic=topic,
                    ).model_dump()
                ).execute()
            except Exception as e:
                logger.error(f"Error storing entry in Supabase: {e}")
