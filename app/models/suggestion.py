from pydantic import BaseModel


class Suggestion(BaseModel):
    title: str
    similarity_score: float


class SuggestionResponse(BaseModel):
    data: list[Suggestion]
