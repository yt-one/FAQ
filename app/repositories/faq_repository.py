from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Faq, FaqTag


class FaqRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, category_id: int, standard_question: str, effective_start=None, effective_end=None) -> Faq:
        payload = {
            "category_id": category_id,
            "standard_question": standard_question,
        }
        if effective_start is not None:
            payload["effective_start"] = effective_start
        if effective_end is not None:
            payload["effective_end"] = effective_end

        faq = Faq(**payload)
        self.session.add(faq)
        await self.session.flush()
        await self.session.refresh(faq)
        return faq

    async def get(self, faq_id: int) -> Faq | None:
        stmt = (
            select(Faq)
            .where(Faq.id == faq_id, Faq.is_deleted.is_(False))
            .execution_options(populate_existing=True)
            .options(
                selectinload(Faq.similar_questions),
                selectinload(Faq.faq_tags).selectinload(FaqTag.tag),
                selectinload(Faq.answers),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, *, category_id: int | None = None, tag_id: int | None = None, offset: int = 0, limit: int = 20) -> Sequence[Faq]:
        stmt = (
            select(Faq)
            .where(Faq.is_deleted.is_(False))
            .execution_options(populate_existing=True)
            .order_by(Faq.id.desc())
            .offset(offset)
            .limit(limit)
            .options(
                selectinload(Faq.similar_questions),
                selectinload(Faq.faq_tags).selectinload(FaqTag.tag),
                selectinload(Faq.answers),
            )
        )
        if category_id is not None:
            stmt = stmt.where(Faq.category_id == category_id)
        if tag_id is not None:
            stmt = stmt.join(FaqTag, FaqTag.faq_id == Faq.id).where(FaqTag.tag_id == tag_id)

        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def update(self, faq: Faq, *, fields: dict) -> Faq:
        for key, value in fields.items():
            setattr(faq, key, value)

        await self.session.flush()
        await self.session.refresh(faq)
        return faq

    async def soft_delete(self, faq: Faq) -> None:
        faq.is_deleted = True
        await self.session.flush()
