from aiogram.filters import BaseFilter
from aiogram.types import Message

from internal.models import User, Role
from pkg.database import session_factory


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        with session_factory() as session:
            user = session.query(User).filter(
                User.telegram_id == message.chat.id,
                User.role == Role.ADMIN
            ).first()
            return user is not None
