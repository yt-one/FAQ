import asyncio
import os
import unittest

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_faq_api.db"

from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.main import app
from app.models.entities import Category, Tag


async def reset_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def seed_base_data() -> tuple[int, int, int]:
    async with AsyncSessionLocal() as session:
        category = Category(name="General", sort_order=0)
        tag_a = Tag(name="billing")
        tag_b = Tag(name="technical")
        session.add_all([category, tag_a, tag_b])
        await session.commit()
        await session.refresh(category)
        await session.refresh(tag_a)
        await session.refresh(tag_b)
        return category.id, tag_a.id, tag_b.id


class TestFaqCrudApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()
        asyncio.run(engine.dispose())

    def setUp(self) -> None:
        asyncio.run(reset_db())
        self.category_id, self.tag_a, self.tag_b = asyncio.run(seed_base_data())

    def _create_faq(self, question: str = "How to reset password?") -> int:
        payload = {
            "category_id": self.category_id,
            "standard_question": question,
            "similar_questions": ["Forgot password", "Cannot login"],
            "tag_ids": [self.tag_a],
            "answers": [
                {
                    "answer_type": "text",
                    "answer_content": "Use the reset link",
                    "sort_order": 1,
                }
            ],
        }
        resp = self.client.post("/faqs", json=payload)
        self.assertEqual(resp.status_code, 201, resp.text)
        return resp.json()["id"]

    def test_create_and_get_faq(self) -> None:
        faq_id = self._create_faq()

        resp = self.client.get(f"/faqs/{faq_id}")
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()

        self.assertEqual(body["id"], faq_id)
        self.assertEqual(body["category_id"], self.category_id)
        self.assertEqual(body["standard_question"], "How to reset password?")
        self.assertEqual(body["similar_questions"], ["Forgot password", "Cannot login"])
        self.assertEqual(body["tag_ids"], [self.tag_a])
        self.assertEqual(len(body["answers"]), 1)
        self.assertEqual(body["answers"][0]["answer_type"], "text")

    def test_list_faqs_with_filters(self) -> None:
        first_id = self._create_faq("How to pay invoice?")

        second_payload = {
            "category_id": self.category_id,
            "standard_question": "How to change email?",
            "similar_questions": ["update email"],
            "tag_ids": [self.tag_b],
            "answers": [{"answer_type": "text", "answer_content": "Go to profile"}],
        }
        resp = self.client.post("/faqs", json=second_payload)
        self.assertEqual(resp.status_code, 201, resp.text)

        list_by_tag = self.client.get(f"/faqs?tag_id={self.tag_a}")
        self.assertEqual(list_by_tag.status_code, 200, list_by_tag.text)
        data = list_by_tag.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], first_id)

    def test_update_faq_replace_nested_fields(self) -> None:
        faq_id = self._create_faq()

        update_payload = {
            "standard_question": "How to reset account password?",
            "similar_questions": ["password reset", "account locked"],
            "tag_ids": [self.tag_b],
            "answers": [
                {
                    "answer_type": "rich_text",
                    "answer_content": "<p>Use security center</p>",
                    "sort_order": 1,
                }
            ],
        }
        resp = self.client.put(f"/faqs/{faq_id}", json=update_payload)
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()

        self.assertEqual(body["standard_question"], "How to reset account password?")
        self.assertEqual(body["similar_questions"], ["password reset", "account locked"])
        self.assertEqual(body["tag_ids"], [self.tag_b])
        self.assertEqual(body["answers"][0]["answer_type"], "rich_text")

    def test_delete_faq_soft_delete(self) -> None:
        faq_id = self._create_faq()

        del_resp = self.client.delete(f"/faqs/{faq_id}")
        self.assertEqual(del_resp.status_code, 204, del_resp.text)

        get_resp = self.client.get(f"/faqs/{faq_id}")
        self.assertEqual(get_resp.status_code, 404, get_resp.text)

        list_resp = self.client.get("/faqs")
        self.assertEqual(list_resp.status_code, 200, list_resp.text)
        self.assertEqual(list_resp.json(), [])


if __name__ == "__main__":
    unittest.main()
