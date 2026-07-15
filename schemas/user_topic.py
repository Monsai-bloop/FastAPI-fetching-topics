from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
# User models


class SubscriptionCreate(SQLModel):
	topic: str 



class Subscription(SubscriptionCreate, table=True):
	id: int | None = Field(default=None, primary_key=True)
	user_id: int | None = Field(default=None, foreign_key="user.id")


class UserBase(SQLModel):
	name: str
	email: str


class User(UserBase, table=True):
	id: int | None = Field(default=None, primary_key=True)
	password: str


class UserCreate(UserBase): # fastapi dev PersonalNews/main.py
	password: str 


class ReadHistory(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	user_id: int = Field(foreign_key="user.id")
	article_title: str
	article_url: str = Field(unique=True)
	read_at: datetime 
