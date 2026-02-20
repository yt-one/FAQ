from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    parent: Mapped["Category | None"] = relationship("Category", remote_side=[id], backref="children")


class Faq(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    standard_question: Mapped[str] = mapped_column(String(500), nullable=False)
    effective_start: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    effective_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[Category] = relationship("Category")
    similar_questions: Mapped[list["SimilarQuestion"]] = relationship(
        "SimilarQuestion", back_populates="faq", cascade="all, delete-orphan"
    )
    faq_tags: Mapped[list["FaqTag"]] = relationship("FaqTag", back_populates="faq", cascade="all, delete-orphan")
    answers: Mapped[list["FaqAnswer"]] = relationship("FaqAnswer", back_populates="faq", cascade="all, delete-orphan")


class SimilarQuestion(Base):
    __tablename__ = "similar_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    faq_id: Mapped[int] = mapped_column(ForeignKey("faqs.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    faq: Mapped[Faq] = relationship("Faq", back_populates="similar_questions")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class FaqTag(Base):
    __tablename__ = "faq_tags"

    faq_id: Mapped[int] = mapped_column(ForeignKey("faqs.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    faq: Mapped[Faq] = relationship("Faq", back_populates="faq_tags")
    tag: Mapped[Tag] = relationship("Tag")


class FaqAnswer(Base):
    __tablename__ = "faq_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    faq_id: Mapped[int] = mapped_column(ForeignKey("faqs.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    answer_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    card_id: Mapped[int | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    faq: Mapped[Faq] = relationship("Faq", back_populates="answers")
