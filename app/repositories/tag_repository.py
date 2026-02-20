from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Tag


class TagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, tag_id: int) -> Tag | None:
        return await self.session.get(Tag, tag_id)

    async def list_all(self) -> Sequence[Tag]:
        result = await self.session.execute(select(Tag).order_by(Tag.name.asc()))
        return result.scalars().all()

    async def create(self, name: str) -> Tag:
        tag = Tag(name=name)
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag
