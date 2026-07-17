from fastapi import APIRouter, Depends
from typing import Annotated
from PersonalNews.schemas.user_topic import *
from PersonalNews.fetch_api.news_fetch import news_api_data
from PersonalNews.cache_data.redis_cache import cache_info
from PersonalNews.safety.auth_user import get_current_user
from PersonalNews.database.db import SessionDep
from sqlmodel import select
import asyncio
from datetime import datetime

articles_router = APIRouter(
	prefix="/article",
	tags=["articles"],
	dependencies=[Depends(get_current_user)]
)


async def fetch_singe_topic(topic: str):
	q = f'"{topic}"'
	q = f"'{q}'"
	print(q)
	data = await news_api_data.fetch_topics(q)
	if isinstance(data, dict) and "articles" in data:
		return data["articles"]
	return []



@articles_router.get("/feed")
async def get_articles(current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
	results = await session.exec(select(Subscription).where(Subscription.user_id == current_user.id))
	topics = [sub.topic for sub in results]

	if not topics:
		return {"articles": []}
	
	cache_tasks = [cache_info.get_cached_article(current_user.id, topic) for topic in topics]
	cached_results = await asyncio.gather(*cache_tasks, return_exceptions=True)

	final_articles = []
	api_tasks = []
	topics_to_fetch = []

	for topic, cached_data in zip(topics, cached_results):
		if cached_data and not isinstance(cached_data, BaseException):
			final_articles.extend(cached_data)
		else:
			topics_to_fetch.append(topic)
			api_tasks.append(fetch_singe_topic(topic))

	if api_tasks:
		api_result = await asyncio.gather(*api_tasks, return_exceptions=True)

		save_tasks = []
		for topic, api_data in zip(topics_to_fetch, api_result):
			if api_data and not isinstance(api_data, BaseException):
				final_articles.extend(api_data)
				save_tasks.append(cache_info.cache_article(current_user.id, api_data, topic))
	
		if save_tasks:
			await asyncio.gather(*save_tasks, return_exceptions=True)

	return {"articles": final_articles}

		