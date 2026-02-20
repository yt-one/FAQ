from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import FaqAnswer


class FaqAnswerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_faq(self, faq_id: int) -> Sequence[FaqAnswer]:
        result = await self.session.execute(
            select(FaqAnswer).where(FaqAnswer.faq_id == faq_id).order_by(FaqAnswer.sort_order.asc(), FaqAnswer.id.asc())
        )
        return result.scalars().all()

    async def replace_for_faq(self, faq_id: int, items: list[dict]) -> None:
        await self.session.execute(delete(FaqAnswer).where(FaqAnswer.faq_id == faq_id))
        for payload in items:
            self.session.add(FaqAnswer(faq_id=faq_id, **payload))
