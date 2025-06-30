from datetime import date
from typing import Optional

from pydantic import BaseModel


class LegislativeFile(BaseModel):
    id: str
    source_table: str
    source_id: str
    link: Optional[str] = None
    title: str
    lastpubdate: Optional[date] = None
    details_link: Optional[str] = None
    committee: Optional[str] = None
    rapporteur: Optional[str] = None
    status: Optional[str] = None
    subjects: Optional[list[str]] = None
    key_players: Optional[list[dict]] = None
    key_events: Optional[list[dict]] = None
    documentation_gateway: Optional[list[dict]] = None
    similarity: Optional[float] = None


class LegislativeFileSuggestion(BaseModel):
    id: str
    title: str
    similarity_score: float


class LegislativeFilesResponse(BaseModel):
    legislative_files: list[LegislativeFile]


class LegislativeFileSuggestionResponse(BaseModel):
    data: list[LegislativeFileSuggestion]
