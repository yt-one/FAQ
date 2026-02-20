from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.repositories.faq_answer_repository import FaqAnswerRepository
from app.repositories.faq_repository import FaqRepository
from app.repositories.faq_tag_repository import FaqTagRepository
from app.repositories.similar_question_repository import SimilarQuestionRepository
from app.schemas.faq import FaqCreate, FaqOut, FaqUpdate


router = APIRouter(prefix="/faqs", tags=["faqs"])


def _to_response(faq) -> FaqOut:
    return FaqOut(
        id=faq.id,
        category_id=faq.category_id,
        standard_question=faq.standard_question,
        effective_start=faq.effective_start,
        effective_end=faq.effective_end,
        similar_questions=[q.question_text for q in faq.similar_questions if q.is_active],
        tag_ids=[item.tag_id for item in faq.faq_tags],
        answers=[
            {
                "id": ans.id,
                "answer_type": ans.answer_type,
                "answer_content": ans.answer_content,
                "card_id": ans.card_id,
                "is_active": ans.is_active,
                "sort_order": ans.sort_order,
            }
            for ans in faq.answers
        ],
    )


@router.post("", response_model=FaqOut, status_code=status.HTTP_201_CREATED)
async def create_faq(payload: FaqCreate, session: AsyncSession = Depends(get_session)) -> FaqOut:
    faq_repo = FaqRepository(session)
    sq_repo = SimilarQuestionRepository(session)
    ft_repo = FaqTagRepository(session)
    ans_repo = FaqAnswerRepository(session)

    faq = await faq_repo.create(
        category_id=payload.category_id,
        standard_question=payload.standard_question,
        effective_start=payload.effective_start,
        effective_end=payload.effective_end,
    )
    await sq_repo.replace_for_faq(faq.id, payload.similar_questions)
    await ft_repo.replace_for_faq(faq.id, payload.tag_ids)
    await ans_repo.replace_for_faq(faq.id, [item.model_dump() for item in payload.answers])
    await session.commit()

    fresh = await faq_repo.get(faq.id)
    return _to_response(fresh)


@router.get("/{faq_id}", response_model=FaqOut)
async def get_faq(faq_id: int, session: AsyncSession = Depends(get_session)) -> FaqOut:
    faq = await FaqRepository(session).get(faq_id)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return _to_response(faq)


@router.get("", response_model=list[FaqOut])
async def list_faqs(
    category_id: int | None = Query(default=None),
    tag_id: int | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[FaqOut]:
    faqs = await FaqRepository(session).list(category_id=category_id, tag_id=tag_id, offset=offset, limit=limit)
    return [_to_response(item) for item in faqs]


@router.put("/{faq_id}", response_model=FaqOut)
async def update_faq(faq_id: int, payload: FaqUpdate, session: AsyncSession = Depends(get_session)) -> FaqOut:
    faq_repo = FaqRepository(session)
    sq_repo = SimilarQuestionRepository(session)
    ft_repo = FaqTagRepository(session)
    ans_repo = FaqAnswerRepository(session)

    faq = await faq_repo.get(faq_id)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")

    updates = payload.model_dump(exclude_unset=True, exclude={"similar_questions", "tag_ids", "answers"})
    if updates:
        await faq_repo.update(faq, fields=updates)

    if payload.similar_questions is not None:
        await sq_repo.replace_for_faq(faq_id, payload.similar_questions)
    if payload.tag_ids is not None:
        await ft_repo.replace_for_faq(faq_id, payload.tag_ids)
    if payload.answers is not None:
        await ans_repo.replace_for_faq(faq_id, [item.model_dump() for item in payload.answers])

    await session.commit()
    fresh = await faq_repo.get(faq_id)
    return _to_response(fresh)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(faq_id: int, session: AsyncSession = Depends(get_session)) -> None:
    repo = FaqRepository(session)
    faq = await repo.get(faq_id)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    await repo.soft_delete(faq)
    await session.commit()
