from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from internal.filters import IsAdminFilter, ChatTypeFilter
from internal.keyboards import main_admin_kb, languages_kb, LanguageCbData, issues_kb, IssueCbData
from internal.models import User, Language
from internal.utils import CLIENT_LOCALE_MESSAGES
from pkg.config import settings
from pkg.database import session_factory

admin_router = Router()
admin_router.message.filter(IsAdminFilter())


@admin_router.message(Command("start"))
async def start_admin(message: Message):
    await message.answer("Здравствуйте, админ", reply_markup=main_admin_kb)


client_router = Router()
client_router.message.filter(~IsAdminFilter())


class ClientRegistrationState(StatesGroup):
    language = State()
    issue = State()


@client_router.message(StateFilter(ClientRegistrationState.language))
async def message_set_language(message: Message):
    await message.answer(CLIENT_LOCALE_MESSAGES[Language.RU]["choose_language"], reply_markup=languages_kb)


@client_router.message(StateFilter(ClientRegistrationState.issue))
async def message_set_issue(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        CLIENT_LOCALE_MESSAGES[data.get("language")]["choose_issue"],
        reply_markup=issues_kb(data.get("language"))
    )


@client_router.message(Command("start"))
async def start_client(message: Message, state: FSMContext):
    with session_factory() as session:
        user = session.query(User).filter(User.telegram_id == message.chat.id).first()
        if not user:
            await state.set_state(ClientRegistrationState.language)
            return await message.answer("Выберите язык", reply_markup=languages_kb)

    await message.answer(CLIENT_LOCALE_MESSAGES[user.language]["start"])


@client_router.callback_query(LanguageCbData.filter(), StateFilter(ClientRegistrationState.language))
async def callback_set_language(callback: CallbackQuery, callback_data: LanguageCbData, state: FSMContext):
    await state.update_data(language=callback_data.language)
    await state.set_state(ClientRegistrationState.issue)
    data = await state.get_data()
    await callback.message.edit_text(
        CLIENT_LOCALE_MESSAGES[data.get("language")]["choose_issue"],
        reply_markup=issues_kb(data.get("language"))
    )
    await callback.answer()


@client_router.callback_query(IssueCbData.filter(), StateFilter(ClientRegistrationState.issue))
async def callback_set_issue(callback: CallbackQuery, callback_data: IssueCbData, state: FSMContext):
    data = await state.get_data()
    language = data.get("language")
    issue = callback_data.issue
    with session_factory() as session:
        user = User(
            telegram_id=callback.message.chat.id,
            username=callback.message.chat.username,
            first_name=callback.message.chat.first_name,
            last_name=callback.message.chat.last_name,
            language=language,
            issue=issue
        )
        session.add(user)
        session.commit()

        topic = await callback.bot.create_forum_topic(
            settings.GROUP_TELEGRAM_ID,
            f"{user.full_name} {user.language.value.upper()} {user.issue.value.upper()} "
            f"#{(8 - len(str(user.id))) * '0'}{user.id}"
        )

        await callback.bot.send_message(
            chat_id=settings.GROUP_TELEGRAM_ID,
            text=f"{user.language.value.upper()} {user.issue.value.upper()}\n"
                 f"<a href='{settings.GROUP_TELEGRAM_URL}/{topic.message_thread_id}'>"
                 f"#{(8 - len(str(user.id))) * '0'}{user.id}</a>\n"
                 f"{'<a href=\"tg://user?id=' + str(user.telegram_id) + '\">' + user.full_name + '</a>'}",
            parse_mode=ParseMode.HTML
        )
        session.query(User).filter(User.id == user.id).update({User.message_thread_id: topic.message_thread_id})
        session.commit()

    await callback.message.edit_text(CLIENT_LOCALE_MESSAGES[language]["start"])
    await state.clear()
    await callback.answer()


@client_router.message(ChatTypeFilter(is_group=False))
async def send_message_to_forum(message: Message):
    with session_factory() as session:
        user = session.query(User).filter(User.telegram_id == message.chat.id).first()
        await message.bot.forward_message(
            settings.GROUP_TELEGRAM_ID,
            message_thread_id=user.message_thread_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
