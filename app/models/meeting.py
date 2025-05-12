from pydantic import BaseModel
from datetime import date
from typing import List


class Meeting(BaseModel):
    date: date
    name: str
    tags: List[str]
