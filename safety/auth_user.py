from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Security, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, ValidationError
from PersonalNews.schemas.user_topic import UserBase, User
from sqlmodel import select
from PersonalNews.database.db import SessionDep
from typing import Optional
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class OAuth2PassowordBearerWithCookie(OAuth2PasswordBearer):
	async def __call__(self, request: Request) -> Optional[str]:
		token_cookie = request.cookies.get("access_token")
		if token_cookie:
			if token_cookie.startswith("Bearer "):
				return token_cookie.split(" ")[1]
			return token_cookie


		return await super().__call__(request) # супер я бабуга лох и его мама тупая!!!

oauth2_sceme2 = OAuth2PassowordBearerWithCookie(tokenUrl="/user/token",scopes={"user": "add articles and read", "admin": "delete user's articles and subscriptions also delete a user himself"})

class Token(BaseModel):
	access_token: str
	token_type: str 


class TokenData(BaseModel):
	username: str
	scopes: list[str] = []


password_hasher = PasswordHash.recommended()

DUMMY_HASH = password_hasher.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token", scopes={"user": "add articles and read", "admin": "delete user's articles and subscriptions also delete a user itself"})

app = FastAPI()


def verify_password(password, hashed_password):
	return password_hasher.verify(password, hashed_password)


def get_cached_password(password):
	return password_hasher.hash(password)


async def get_user(username: str, session: SessionDep):
	statement = select(User).where(User.name == username)
	user = await session.exec(statement)
	if user:
			result = user.first()
			return result
	else:
		raise HTTPException(status_code=404, detail="User not found")


async def authenticate_user(username: str, password: str, session: SessionDep):
	user = await get_user(username, session)
	if not user:
		verify_password(password, DUMMY_HASH)
		return False
	if not verify_password(password, user.password):
		return False
	return user


def create_access_token(data: dict, expire_delta: timedelta | None = None):
	to_encode = data.copy()
	if expire_delta:
		expire = datetime.now(timezone.utc) + expire_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=15)

	to_encode.update({"exp": expire})
	encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  
	return encode_jwt


async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_sceme2)],session:SessionDep):
	# use scopes
	if security_scopes.scopes:
		authenticate_value = f'Bearer scopes="{security_scopes.scope_str}"'
	else:
		authenticate_value = "Bearer"	


	credentials_exceptions = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	try:
		# verify JWT token and username
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username = payload.get("sub")
		if username is None:
			raise credentials_exceptions
		scope: str = payload.get("scope", "")
		token_scopes = scope.split(" ")
		token_data = TokenData(username=username, scopes=token_scopes)
	except (InvalidTokenError, ValidationError):
		raise credentials_exceptions
	
	#verify scopes
	user = await get_user(token_data.username, session)
	if user is None:
		raise credentials_exceptions
	for scope in security_scopes.scopes:
		if scope not in token_data.scopes:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Not enough permissions",
				headers={"WWW-Auntenticate": authenticate_value}
			)
	return user 


async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session:SessionDep, response: Response):
	user = await authenticate_user(form_data.username, form_data.password, session)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password or username", headers={"WWW-Authenticate": "Bearer"})
	access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(data={"sub": user.name, "scope": " ".join(form_data.scopes)}, expire_delta=access_token_expire)
	response.set_cookie(
		key="access_token",
		value=f"Bearer {access_token}",
		httponly=True,
		secure=False, # timeable 
		samesite="lax"
	)
	return Token(access_token=access_token, token_type="bearer")
