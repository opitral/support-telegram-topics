from aiogram.filters import BaseFilter
from aiogram.types import Message

from internal.models import User, Role
from pkg.database import session_factory


class HasRole(BaseFilter):
    def __init__(self, *roles: Role):
        self.roles = roles

    async def __call__(self, message: Message) -> bool:
        with session_factory() as session:
            user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
            if user and user.role in self.roles:
                return True
            return False


class ChatTypeFilter(BaseFilter):
    def __init__(self, is_group: bool):
        self.is_group = is_group

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in ["group", "supergroup"] if self.is_group else message.chat.type == "private"
