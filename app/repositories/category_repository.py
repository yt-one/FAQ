from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, name: str, parent_id: int | None = None, sort_order: int = 0) -> Category:
        item = Category(name=name, parent_id=parent_id, sort_order=sort_order)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item
