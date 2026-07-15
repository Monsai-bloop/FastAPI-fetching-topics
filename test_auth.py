import pytest
from unittest.mock import patch
from redis import asyncio as aioredis
from unittest.mock import AsyncMock
from PersonalNews.cache_data.redis_cache import cache_info
from typing import cast, Dict, Any
from PersonalNews.fetch_api.news_fetch import news_api_data

@pytest.mark.asyncio
async def test_client_register(client):
	response = await client.post("/user/create", json={"name": "monsai", "password": "123", "email": "hello@comma.com"})
	assert response.status_code == 201


@pytest.mark.asyncio
async def test_client_login(client):
	await client.post("/user/create", json={"name": "monsai", "password": "123", "email": "hello@comma.com"})
	response = await client.post("/user/token", data={"username": "monsai", "password": "123"})
	assert response.status_code == 200


@pytest.mark.asyncio
async def test_subscription(client):
	await client.post("/user/create", json={"name": "monsai", "password": "123", "email": "hello@comma.com"})
	token_response = await client.post("/user/token", data={"username": "monsai", "password": "123"}) # which datatype does it return?
	token_data = token_response.json()
	access_token = token_data["access_token"]
	header = {"Authorization": f"Bearer {access_token}"}
	response = await client.post("/subscription/subscribe", json={"topic": "python"}, headers=header)
	assert response.status_code == 201


@pytest.mark.asyncio
async def test_redis_cache(mocker):
	mock_redis = mocker.patch("PersonalNews.cache_data.redis_cache.cache_info.get_cached_article", new_callable=AsyncMock)
	mock_redis.return_value = {"user_id": 1, "topic": "python"}
	assert await cache_info.get_cached_article(1, "python") == {"user_id": 1, "topic": "python"}


@pytest.mark.asyncio
async def test_fetch_article(client, mocker):
	await client.post("/user/create", json={"name": "monsai", "password": "123", "email": "hello@comma.com"})

	token_response = await client.post("/user/token", data={"username": "monsai", "password": "123"})

	data = token_response.json()
	access_token = data["access_token"]
	header = {"Authorization": f"Bearer {access_token}"}
	await client.post("/subscription/subscribe", json={"topic": "python"}, headers=header)

	mocked_fetching = mocker.patch("PersonalNews.routers.articles.news_api_data.fetch_topics", new_callable=AsyncMock, return_value=[{"title": "Test article"}])

	mocker.patch.object(cache_info, "cache_article", new_callable=AsyncMock)
	mocker.patch.object(cache_info, "get_cached_article", new_callable=AsyncMock, return_value=None)

	result = await client.get("/article/feed", headers=header)
	assert result.status_code == 200
	assert mocked_fetching.called

	mocked_fetching.assert_called()
	mocked_fetching.assert_awaited()
	

@pytest.mark.asyncio
async def test_fetching_articles(mocker):
	mock_fetching_topic = mocker.patch(
    "PersonalNews.fetch_api.news_fetch.news_api_data.fetch_topics", 
    side_effect=["Success", Exception("something went wrong")]
	)
	result1 = await news_api_data.fetch_topics("'python'")
	assert result1 == "Success"

	with pytest.raises(Exception, match="something went wrong"):
		await news_api_data.fetch_topics("'python'")


@pytest.mark.asyncio
async def test_errors(mocker):
	mock_fetching_topic = mocker.patch(
    "PersonalNews.fetch_api.news_fetch.news_api_data.fetch_topics", 
    side_effect=["Success", Exception("something went wrong")]
	)