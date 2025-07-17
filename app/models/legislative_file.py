from datetime import date
from typing import Optional

from pydantic import BaseModel


class Rapporteur(BaseModel):
    name: str
    link: Optional[str] = None


class Reference(BaseModel):
    text: Optional[str] = None
    link: Optional[str] = None


class KeyPlayer(BaseModel):
    institution: str
    committee: str
    committee_full: Optional[str] = None
    committee_link: Optional[str] = None
    rapporteurs: Optional[list[Rapporteur]] = None
    shadow_rapporteurs: Optional[list[Rapporteur]] = None


class KeyEvent(BaseModel):
    date: Optional[str] = None
    event: Optional[str] = None
    summary: Optional[str] = None
    reference: Optional[Reference] = None


class DocumentationGateway(BaseModel):
    date: Optional[str] = None
    summary: Optional[str] = None
    reference: Optional[Reference] = None
    document_type: Optional[str] = None


class LegislativeFile(BaseModel):
    id: str
    source_table: Optional[str] = None
    source_id: Optional[str] = None
    link: Optional[str] = None
    title: str
    lastpubdate: Optional[date | str] = None
    details_link: Optional[str] = None
    committee: Optional[str] = None
    rapporteur: Optional[str] = None
    status: Optional[str] = None
    subjects: Optional[list[str]] = None
    key_players: Optional[list[KeyPlayer]] = None
    key_events: Optional[list[KeyEvent]] = None
    documentation_gateway: Optional[list[DocumentationGateway]] = None
    similarity: Optional[float] = None
    subscribed: Optional[bool] = None


class LegislativeFileSuggestion(BaseModel):
    id: str
    title: str
    similarity_score: float


class LegislativeFilesResponse(BaseModel):
    data: list[LegislativeFile]


class LegislativeFileResponse(BaseModel):
    legislative_file: LegislativeFile


class LegislativeFileSuggestionResponse(BaseModel):
    data: list[LegislativeFileSuggestion]


class LegislativeFileUniqueValuesResponse(BaseModel):
    years: list[str]
    committees: list[str]
    statuses: list[str]
