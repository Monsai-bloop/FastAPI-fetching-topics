import httpx
from PersonalNews.config import settings
import asyncio
import traceback
class NewsApiData():
	def __init__(self):
		self.api_key = settings.API_KEY
		self.current_link = settings.CURRENT_URL

	async def fetch_topics(self, q: str):
		news_url = f"{self.current_link}/v2/everything"

		headers = {"X-Api-Key": self.api_key}
		params = {"q": q}

		try:
			async with httpx.AsyncClient(timeout=15) as client:
				response = await client.get(news_url, params=params, headers=headers)
				response.raise_for_status()
				data = response.json()
				return data 
		except Exception as e:
			print(f"some exception occurs {e}")
			traceback.print_exc()
			return {"articles": [], "error": str(e)}



news_api_data = NewsApiData()