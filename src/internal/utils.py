from enum import Enum

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from internal.models import User, Role, Language
from pkg.config import settings
from pkg.database import session_factory


def create_admin_if_not_exist():
    with session_factory() as session:
        if not session.query(User).filter(User.telegram_id == settings.ADMIN_TELEGRAM_ID).first():
            session.add(
                User(
                    telegram_id=settings.ADMIN_TELEGRAM_ID,
                    username=settings.ADMIN_USERNAME,
                    first_name=settings.ADMIN_FIRST_NAME,
                    last_name=settings.ADMIN_LAST_NAME,
                    role=Role.ADMIN
                )
            )
        session.commit()
        session.close()


def get_admins_telegram_id():
    with session_factory() as session:
        admins_telegram_id = [user.telegram_id for user in session.query(User).filter(User.role == Role.ADMIN).all()]
        return admins_telegram_id


def get_operators_telegram_id():
    with session_factory() as session:
        operators_telegram_id = [user.telegram_id for user in
                                 session.query(User).filter(User.role == Role.OPERATOR).all()]
        return operators_telegram_id


def get_clients_telegram_id():
    with session_factory() as session:
        clients_telegram_id = [user.telegram_id for user in
                               session.query(User).filter(User.role == Role.CLIENT).all()]
        return clients_telegram_id


CLIENT_LOCALE_MESSAGES = {
    Language.UA: {
        "start": "Напишіть свій запит, і я передам його адміністраторам.\n\nℹ️ Щоб ми могли швидше та точніше опрацювати Ваш запит, будь ласка, вкажіть у зверненні, про який чат або місто йдеться.",
        "choose_language": "Select a language?",
        "choose_issue": "Оберіть тему звернення",
        "sale": "📢Замовити рекламу📢",
        "support": "📩Зв'язатися з адміністрацією📩 ",
    },
    Language.RU: {
        "start": "Напишите свой запрос, и я передам его администраторам.\n\nℹ️ Чтобы мы могли быстрее и точнее обработать Ваш запрос, пожалуйста, укажите в обращении, о каком чате или городе идет речь.",
        "choose_language": "Select a language?",
        "choose_issue": "Выберите тему обращения",
        "sale": "📢Заказать рекламу📢",
        "support": "📩Связаться с администрацией📩",
    }
}


class TargetRecipient(Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    CLIENT = "client"


async def notify(bot: Bot, target_recipients: list[TargetRecipient], message: str = None, media: str = None,
                 keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup = None):
    receivers = []
    if TargetRecipient.ADMIN in target_recipients:
        admins_telegram_id = get_admins_telegram_id()
        receivers.extend(admins_telegram_id)
    if TargetRecipient.OPERATOR in target_recipients:
        operators_telegram_id = get_operators_telegram_id()
        receivers.extend(operators_telegram_id)
    if TargetRecipient.CLIENT in target_recipients:
        clients_telegram_id = get_clients_telegram_id()
        receivers.extend(clients_telegram_id)

    for receiver in receivers:
        if media:
            await bot.send_photo(receiver, media, caption=message, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        if message:
            await bot.send_message(receiver, message, parse_mode=ParseMode.HTML, reply_markup=keyboard)


def get_clients(offset: int = 0, limit: int = 10) -> list[User]:
    with session_factory() as session:
        clients = session.query(User).filter(User.role == Role.CLIENT).offset(offset).limit(limit).all()
        return clients


def get_clients_count() -> int:
    with session_factory() as session:
        clients_count = session.query(User).filter(User.role == Role.CLIENT).count()
        return clients_count


def get_operators(offset: int = 0, limit: int = 10) -> list[User]:
    with session_factory() as session:
        operators = session.query(User).filter(User.role == Role.OPERATOR).offset(offset).limit(limit).all()
        return operators


def get_operators_count() -> int:
    with session_factory() as session:
        operators_count = session.query(User).filter(User.role == Role.OPERATOR).count()
        return operators_count
