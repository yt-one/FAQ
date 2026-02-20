from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FaqAnswerIn(BaseModel):
    answer_type: Literal["text", "rich_text", "card"]
    answer_content: str | None = None
    card_id: int | None = None
    is_active: bool = True
    sort_order: int = 0


class FaqCreate(BaseModel):
    category_id: int
    standard_question: str = Field(min_length=1, max_length=500)
    effective_start: datetime | None = None
    effective_end: datetime | None = None
    similar_questions: list[str] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)
    answers: list[FaqAnswerIn] = Field(default_factory=list)


class FaqUpdate(BaseModel):
    category_id: int | None = None
    standard_question: str | None = Field(default=None, min_length=1, max_length=500)
    effective_start: datetime | None = None
    effective_end: datetime | None = None
    similar_questions: list[str] | None = None
    tag_ids: list[int] | None = None
    answers: list[FaqAnswerIn] | None = None


class FaqAnswerOut(BaseModel):
    id: int
    answer_type: str
    answer_content: str | None
    card_id: int | None
    is_active: bool
    sort_order: int


class FaqOut(BaseModel):
    id: int
    category_id: int
    standard_question: str
    effective_start: datetime
    effective_end: datetime | None
    similar_questions: list[str]
    tag_ids: list[int]
    answers: list[FaqAnswerOut]
