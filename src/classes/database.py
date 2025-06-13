from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

if TYPE_CHECKING:
    from ..bot import FashionThing


class DatabaseManager:
    def __init__(self, bot: FashionThing, uri: str) -> None:
        self.client = AsyncIOMotorClient(uri, tls=True)
        self.db = self.client["fashionist"]
        self.leaderboard = self.db["leaderboard"]
        self.month = self.db["month"]

    async def submit_score(self, username: str, score: int) -> None:
        now = datetime.now(timezone.utc)
        await self.leaderboard.update_one(
            {"username": username},
            {"$inc": {"score": score}, "$set": {"updated_at": now}},
            upsert=True,
        )

    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        cursor = (
            self.leaderboard.find({}, {"_id": False})
            .sort("score", DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_user_rank(self, username: str) -> Optional[int]:
        user = await self.leaderboard.find_one({"username": username}, {"score": True})
        if not user:
            return None

        higher_count = await self.leaderboard.count_documents(
            {"score": {"$gt": user["score"]}}
        )
        return higher_count + 1

    async def update_month(self, month: str):
        month = await self.month.update_one(
            {"_id": "current"},

            {"$set": {"value": month}},
            upsert=True
        )
        return month 

    async def get_month(self):
        return await self.month.find({"_id": "current"}).to_list()
    
    async def reset(self) -> None:
        await self.leaderboard.delete_many({})
