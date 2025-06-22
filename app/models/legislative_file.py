from datetime import date
from typing import Optional

from pydantic import BaseModel


class LegislativeFile(BaseModel):
    reference: str
    source_table: str
    source_id: str
    link: Optional[str] = None
    title: str
    lastpubdate: Optional[date] = None
    committee: Optional[str] = None
    rapporteur: Optional[str] = None
    similarity: Optional[float] = None


class LegislativeFilesResponse(BaseModel):
    legislative_files: list[LegislativeFile]
