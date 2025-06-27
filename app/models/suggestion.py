from pydantic import BaseModel


class Suggestion(BaseModel):
    title: str
    similarity_score: float


class LegislationSuggestion(BaseModel):
    reference: str
    title: str
    similarity_score: float


class SuggestionResponse(BaseModel):
    data: list[Suggestion]


class LegislationSuggestionResponse(BaseModel):
    data: list[LegislationSuggestion]
