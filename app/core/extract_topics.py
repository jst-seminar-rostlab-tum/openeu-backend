import logging

import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.supabase_client import supabase
from app.models.meeting import Meeting

logger = logging.getLogger(__name__)

TOPICS_TABLE = "meeting_topics"
ASSIGNMENTS_TABLE = "meeting_topic_assignments"
OTHER_TOPIC = "Other"
SIMILARITY_THRESHOLD = 0.1
BATCH_SIZE = 500


def clear_assignments():
    """
    Clears all entries in the meeting_topic_assignments tables.
    """
    supabase.table(ASSIGNMENTS_TABLE).delete().not_.is_("id", None).execute()


def fetch_meetings_batch(offset: int, batch_size: int = BATCH_SIZE) -> list[Meeting]:
    """
    Fetch a batch of meetings from v_meetings.
    """
    resp = supabase.table("v_meetings").select("*").range(offset, offset + batch_size - 1).execute()
    return [Meeting(**item) for item in resp.data]


def fetch_and_prepare_meetings() -> list[Meeting]:
    """
    Fetches all meetings in batches from the database.

    Returns:
        A list of all Meeting objects.
    """
    offset = 0
    all_meetings: list[Meeting] = []
    while True:
        batch: list[Meeting] = fetch_meetings_batch(offset)
        if not batch:
            break
        for m in batch:
            all_meetings.append(m)
        offset += BATCH_SIZE
    return all_meetings


def add_other_topic() -> int | None:
    """
    Ensures the 'Other' topic exists in the topics table and returns its id.
    """
    try:
        topic_data = {"topic": OTHER_TOPIC}
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

    def assign_meeting_to_topic(self, meeting: Meeting):
        """
        Assigns a single meeting to the closest existing topic based on cosine similarity.

        If the similarity is below a threshold, it assigns the meeting to the 'Other' topic.
        The assignment is then stored in the database.
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

    def reassign_all_meetings(self):
        """
        Orchestrates the process of assigning all meetings to predefined topics.

        This function clears all existing topic assignments, fetches all meetings,
        and then iterates through each meeting to assign it to the most relevant topic.
        """
        clear_assignments()
        all_meetings = fetch_and_prepare_meetings()
        for meeting in all_meetings:
            self.assign_meeting_to_topic(meeting)
