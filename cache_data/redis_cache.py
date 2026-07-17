import redis.asyncio as aiosync
from PersonalNews.config import settings
from redis.typing import EncodableT, FieldT
from typing import Mapping
import json
import sys 
import os 

class CacheData():
	def __init__(self, host=None, port=None, db=None):
		self.redis = aiosync.Redis(
			host=host or settings.REDIS_HOST,
      port=port or settings.REDIS_PORT,
      db=db or settings.REDIS_DB,
      decode_responses=True
			)
		
	def _generatekey(self, user_id: int, topic: str):
		return f"user:{user_id}:topic:{topic}"


	async def cache_article(self, user_id, articles: list, topic):
		key = self._generatekey(user_id, topic)
		await self.redis.set(ex=3600, name=key, value=json.dumps(articles))
	

	async def get_cached_article(self, user_id, topic: str) -> list:
		key = self._generatekey(user_id, topic)
		data = await self.redis.get(key)
		if data:
			return json.loads(data)
		return []
	

cache_info = CacheData()

		
	