from fastapi import APIRouter, Depends, Security, Response, Header
from typing import Annotated
from PersonalNews.schemas.user_topic import *
from PersonalNews.safety.auth_user import login_for_access_token, Token, get_current_user, oauth2_scheme, get_cached_password
from PersonalNews.database.db import SessionDep
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

users_router = APIRouter(
	prefix="/user",
	tags=["users"]
)


auth_users_router = APIRouter(dependencies=[Depends(get_current_user)])


@users_router.post("/create", status_code=201)
async def create_user(user: UserCreate, session: SessionDep):
	user_db = user.model_dump()
	user_db["password"] = get_cached_password(user.password)
	user_in_db = User.model_validate(user_db)
	
	try:
		session.add(user_in_db)
		await session.commit()
		await session.refresh(user_in_db)
		return user_in_db
	except Exception as e:
		print(f"there are some errors: {e}")


@users_router.post("/token", response_model=Token, status_code=200)
async def login(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	session: SessionDep, response: Response
):
	user = await login_for_access_token(form_data, session, response)
	return user 



@auth_users_router.get("/user")
async def get_user_data(current_user: Annotated[User, Depends(get_current_user)], response: Response):
	response.headers["X-Client-Version"] = "hello"
	return current_user




@auth_users_router.delete("/delete")
async def delete_user(current_user: Annotated[User, Security(get_current_user, scopes=["admin"])], session: SessionDep, id: int):
	try:
		statement = await session.exec(select(User).where(User.id == id))
		user = statement.first()
		await session.delete(user)
		await session.commit()
		return {"deleted": "True"}
	except Exception:
		return {"deleted": "False."}
	


users_router.include_router(auth_users_router)	