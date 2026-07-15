from fastapi import APIRouter, Depends, Security
from typing import Annotated
from PersonalNews.schemas.user_topic import *
from PersonalNews.safety.auth_user import get_current_user
from PersonalNews.database.db import SessionDep
subscription_router = APIRouter(
	prefix="/subscription",
	tags=["subscriptions"],
	dependencies=[Depends(get_current_user)]
)


@subscription_router.post('/subscribe', status_code=201)
async def subscribe_topic(current_user: Annotated[User, Security(get_current_user, scopes=["user"])], subscribe: SubscriptionCreate, session: SessionDep):
	subscribe_db = Subscription(
		user_id=current_user.id,
		topic=subscribe.topic
	)

	session.add(subscribe_db)
	await session.commit()
	await session.refresh(subscribe_db)

	return subscribe_db