from PersonalNews.database.db import create_db, SessionDep
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from PersonalNews.routers.subscriptions import subscription_router
from PersonalNews.routers.users import users_router 
from PersonalNews.routers.articles import articles_router
import time 
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
@asynccontextmanager
async def lifespan(app:FastAPI):
	async with create_db() as db:
		yield db 

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
	client_version = request.headers.get("x-client-version")
	print(client_version)
	start_time = time.perf_counter()
	response = await call_next(request)
	process_time = time.perf_counter() - start_time
	response.headers["X-Process-Time"] = str(process_time)
	print(f"{request.method}, {request.url.path} -> {response.status_code} {process_time}, {request.client}")
	return response

# class AuthMiddleware(BaseHTTPMiddleware):
# 	async def dispatch(self, request: Request, call_next):
# 		token = request.cookies.get("access_token")
# 		if not token:
# 			return Response("Unathorized_my_way", status_code=402)
# 		response = await call_next(request)
# 		return response

# app.add_middleware(AuthMiddleware)
app.add_middleware(CORSMiddleware, expose_headers=["X-Process-Time"])


app.include_router(subscription_router)
app.include_router(users_router)
app.include_router(articles_router)