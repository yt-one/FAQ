from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import SimilarQuestion


class SimilarQuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_faq(self, faq_id: int) -> Sequence[SimilarQuestion]:
        result = await self.session.execute(
            select(SimilarQuestion)
            .where(SimilarQuestion.faq_id == faq_id, SimilarQuestion.is_active.is_(True))
            .order_by(SimilarQuestion.id.asc())
        )
        return result.scalars().all()

    async def replace_for_faq(self, faq_id: int, questions: list[str]) -> None:
        await self.session.execute(delete(SimilarQuestion).where(SimilarQuestion.faq_id == faq_id))
        for question in dict.fromkeys(questions):
            self.session.add(SimilarQuestion(faq_id=faq_id, question_text=question, is_active=True, created_by="manual"))
