import logging

import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from app.core.supabase_client import supabase
from app.models.meeting import Meeting
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
    "romanian",
}

TOPICS_TABLE = "meeting_topics"
ASSIGNMENTS_TABLE = "meeting_topic_assignments"
OTHER_TOPIC = "Other"
SIMILARITY_THRESHOLD = 0.4
BATCH_SIZE = 500


def clear_topics_and_assignments():
    """
    Clears all entries in the meeting_topics and meeting_topic_assignments tables.
    """
    supabase.table(ASSIGNMENTS_TABLE).delete().not_.is_("id", None).execute()
    supabase.table(TOPICS_TABLE).delete().not_.is_("id", None).execute()


def fetch_meetings_batch(offset: int, batch_size: int = BATCH_SIZE) -> list[Meeting]:
    """
    Fetch a batch of meetings from v_meetings.
    """
    resp = supabase.table("v_meetings").select("*").range(offset, offset + batch_size - 1).execute()
    return [Meeting(**item) for item in resp.data]


def fetch_and_prepare_meetings() -> tuple[list[str], list[Meeting]]:
    """
    Fetches up to 500 meetings and prepares their text for topic extraction.
    Returns a tuple of (list of texts, list of Meeting objects).
    """
    batch: list[Meeting] = fetch_meetings_batch(0, batch_size=BATCH_SIZE)
    all_texts: list[str] = []
    all_meetings: list[Meeting] = []
    for m in batch:
        text = m.title
        if m.description:
            text = f"{text}. {m.description}"
        text = text.strip()
        all_texts.append(text)
        all_meetings.append(m)
    return all_texts, all_meetings


def add_other_topic() -> int | None:
    """
    Ensures the 'Other' topic exists in the topics table and returns its id.
    """
    try:
        topic_data = Topic(topic=OTHER_TOPIC).model_dump()
        resp = supabase.table(TOPICS_TABLE).upsert(topic_data).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        logger.error(f"Error storing Other topic: {e}")
        return None


class TopicExtractor:
    _sentence_model = None
    _keybert_model = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if TopicExtractor._sentence_model is None:
            TopicExtractor._sentence_model = SentenceTransformer(model_name)
        if TopicExtractor._keybert_model is None:
            TopicExtractor._keybert_model = KeyBERT(model_name)
        self.model = TopicExtractor._sentence_model
        self.kw_model = TopicExtractor._keybert_model

    def extract_keywords_from_texts(self, all_texts: list[str], top_n_keywords: int) -> list[str]:
        """
        Extracts keywords from a list of texts using KeyBERT, excluding generic words.
        """
        all_keywords: list[str] = []
        for text in all_texts:
            keywords = self.kw_model.extract_keywords(
                text, keyphrase_ngram_range=(1, 1), stop_words="english", top_n=top_n_keywords
            )
            all_keywords.extend([kw for kw, _ in keywords if kw.lower() not in EXCLUDED_WORDS])
        return all_keywords

    def cluster_keywords_and_store_topics(self, all_keywords: list[str], n_clusters: int) -> None:
        """
        Clusters keyword embeddings and stores topics in the database.
        """
        embeddings = self.model.encode(all_keywords)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(embeddings)
        labels = kmeans.labels_
        topic_keywords: list[str] = []
        topic_ids = []
        for i in range(n_clusters):
            indices = np.where(labels == i)[0]
            if len(indices) > 0:
                topic = all_keywords[indices[0]].capitalize()
                try:
                    topic_data = Topic(topic=topic).model_dump()
                    resp = supabase.table(TOPICS_TABLE).upsert(topic_data).execute()
                    topic_id = resp.data[0]["id"] if resp.data else None
                    topic_keywords.append(topic)
                    topic_ids.append(topic_id)
                except Exception as e:
                    logger.error(f"Error storing entry in Supabase: {e}")
                    topic_keywords.append(topic)
                    topic_ids.append(None)
        add_other_topic()

    def assign_meeting_to_topic(self, meeting: Meeting):
        """
        Assigns a single meeting to the closest topic (or 'Other') using cosine similarity.
        """
        resp = supabase.table(TOPICS_TABLE).select("id,topic").execute()
        topics = resp.data
        if not topics:
            return {
                "source_id": meeting.source_id,
                "source_table": meeting.source_table,
                "topic_id": None,
            }

        topic_keywords = [t["topic"].lower().strip() for t in topics]
        topic_ids = [t["id"] for t in topics]
        other_id = next((t["id"] for t in topics if t["topic"] == OTHER_TOPIC), None)

        topic_embeddings = self.model.encode(topic_keywords, normalize_embeddings=True)
        meeting_text = f"{meeting.title or ''}. {meeting.description or ''}".strip()
        meeting_emb = self.model.encode([meeting_text], normalize_embeddings=True)
        sims = cosine_similarity(meeting_emb, topic_embeddings)[0]
        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])

        assigned_topic_id = (
            topic_ids[best_idx] if topic_ids[best_idx] is not None and best_score >= SIMILARITY_THRESHOLD else other_id
        )

        try:
            supabase.table(ASSIGNMENTS_TABLE).upsert(
                {
                    "source_id": meeting.source_id,
                    "source_table": meeting.source_table,
                    "topic_id": assigned_topic_id,
                }
            ).execute()
        except Exception as e:
            logger.error(f"Error storing meeting-topic assignments: {e}")

    def extract_topics_from_meetings(self, n_clusters=15, top_n_keywords=20):
        """
        Orchestrates the extraction of topics and assignment of meetings to topics.
        """
        clear_topics_and_assignments()
        all_texts, all_meetings = fetch_and_prepare_meetings()
        if not all_texts:
            return []
        all_keywords = self.extract_keywords_from_texts(all_texts, top_n_keywords)
        if not all_keywords:
            return []
        self.cluster_keywords_and_store_topics(all_keywords, n_clusters)
        for meeting in all_meetings:
            self.assign_meeting_to_topic(meeting)
