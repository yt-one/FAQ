from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import FaqTag


class FaqTagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_tag_ids(self, faq_id: int) -> Sequence[int]:
        result = await self.session.execute(select(FaqTag.tag_id).where(FaqTag.faq_id == faq_id))
        return result.scalars().all()

    async def replace_for_faq(self, faq_id: int, tag_ids: list[int]) -> None:
        await self.session.execute(delete(FaqTag).where(FaqTag.faq_id == faq_id))
        for tag_id in set(tag_ids):
            self.session.add(FaqTag(faq_id=faq_id, tag_id=tag_id))
