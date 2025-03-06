import validators
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from internal.filters import HasRole, ChatTypeFilter
from internal.keyboards import main_admin_kb, languages_kb, LanguageCbData, issues_kb, IssueCbData, cancel_kb, \
    yes_back_kb, YesBackCbData, custom_inline_kb, back_skip_kb, clients_kb, ClientsPageCbData
from internal.models import User, Language, Role
from internal.utils import CLIENT_LOCALE_MESSAGES
from pkg.config import settings
from pkg.database import session_factory
from pkg.logger import get_logger

logger = get_logger(__name__)

admin_router = Router()
admin_router.message.filter(HasRole(Role.ADMIN), ChatTypeFilter(is_group=False))


@admin_router.message(Command("start"))
async def start_admin(message: Message):
    await message.answer("Здравствуйте, админ", reply_markup=main_admin_kb)


class NotifyClientMessage(StatesGroup):
    message = State()
    button = State()
    submit = State()


@admin_router.message(F.text.lower() == "сделать рассылку клиентам")
@admin_router.message(F.text.lower() == "назад", NotifyClientMessage.button)
async def send_message_to_clients_msg(message: Message, state: FSMContext):
    await state.set_state(NotifyClientMessage.message)
    await message.answer("Введите сообщение для рассылки (можно прикрепить файл или одно медиа-сообщение)", reply_markup=cancel_kb)


@admin_router.message(F.text.lower() == "отмена", StateFilter(NotifyClientMessage))
async def cancel_message_to_clients(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_admin_kb)


@admin_router.message(StateFilter(NotifyClientMessage.message))
async def want_button(message: Message, state: FSMContext):
    await state.update_data(message=message.message_id)
    await state.set_state(NotifyClientMessage.button)
    await message.answer("Введите данные кнопки в формате: `название кнопки - https://ссылка_кнопки`", reply_markup=back_skip_kb, parse_mode=ParseMode.MARKDOWN)


@admin_router.message(NotifyClientMessage.button, F.text.lower() == "пропустить")
async def skip_button_name(message: Message, state: FSMContext):
    await submit_post(message, state)


@admin_router.message(NotifyClientMessage.button)
async def add_button(message: Message, state: FSMContext):
    try:
        button_name, button_url = message.text.split(" - ", maxsplit=1)
        if not validators.url(button_url):
            raise TypeError
        await state.update_data(button_name=button_name, button_url=button_url)

    except ValueError:
        return await message.answer("Неверный формат. Попробуйте еще раз", reply_markup=back_skip_kb)

    except TypeError:
        return await message.answer("Неверная ссылка. Попробуйте еще раз", reply_markup=back_skip_kb)

    await submit_post(message, state)


@admin_router.message(StateFilter(NotifyClientMessage.button))
async def submit_post(message: Message, state: FSMContext):
    await state.set_state(NotifyClientMessage.submit)
    data = await state.get_data()
    if data.get("button_name") and data.get("button_url"):
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=message.chat.id,
            message_id=data.get("message"),
            reply_markup=custom_inline_kb(data.get("button_name"), data.get("button_url"))
        )
    else:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=message.chat.id,
            message_id=data.get("message")
        )
    await message.answer("Вы уверены, что хотите отправить это сообщение?", reply_markup=yes_back_kb)
    temp_msg = await message.answer("del kb", reply_markup=ReplyKeyboardRemove())
    await temp_msg.delete()


@admin_router.callback_query(YesBackCbData.filter(), NotifyClientMessage.submit)
async def submit_post_callback(callback: CallbackQuery, callback_data: YesBackCbData, state: FSMContext):
    data = await state.get_data()
    if not callback_data.yes:
        await state.set_state(NotifyClientMessage.button)
        await callback.message.answer(
            "Введите данные кнопки в формате: `название кнопки - https://ссылка_кнопки`",
            reply_markup=back_skip_kb,
            parse_mode=ParseMode.MARKDOWN
        )
        return await callback.answer()
    with session_factory() as session:
        users = session.query(User).filter(User.role == Role.CLIENT).all()
        for user in users:
            try:
                if data.get("button_name") and data.get("button_url"):
                    await callback.bot.copy_message(
                        chat_id=user.telegram_id,
                        from_chat_id=callback.message.chat.id,
                        message_id=data.get("message"),
                        reply_markup=custom_inline_kb(data.get("button_name"), data.get("button_url"))
                    )
                else:
                    await callback.bot.copy_message(
                        chat_id=user.telegram_id,
                        from_chat_id=callback.message.chat.id,
                        message_id=data.get("message")
                    )

            except Exception as e:
                logger.warning("Error while sending message to user", e)
                continue

    await state.clear()
    await callback.message.answer("Сообщение отправлено", reply_markup=main_admin_kb)
    await callback.answer()


@admin_router.message(F.text.lower() == "клиенты")
async def show_clients(message: Message):
    with session_factory() as session:
        clients_count = session.query(User).filter(User.role == Role.CLIENT).count()

    await message.answer(
        f"Всего найдено клиентов: {clients_count}",
        reply_markup=clients_kb() if clients_count else None
    )


@admin_router.callback_query(ClientsPageCbData.filter())
async def clients_page_callback(callback: CallbackQuery, callback_data: ClientsPageCbData):
    with session_factory() as session:
        clients_count = session.query(User).filter(User.role == Role.CLIENT).count()

    await callback.message.edit_text(
        f"Всего найдено клиентов: {clients_count}",
        reply_markup=clients_kb(callback_data.page) if clients_count else None
    )

client_router = Router()
client_router.message.filter(HasRole(Role.CLIENT), ChatTypeFilter(is_group=False))


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
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
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
            telegram_id=callback.message.from_user.id,
            username=callback.message.from_user.username,
            first_name=callback.message.from_user.first_name,
            last_name=callback.message.from_user.last_name,
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
        user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
        await message.bot.forward_message(
            settings.GROUP_TELEGRAM_ID,
            message_thread_id=user.message_thread_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )


operator_router = Router()

@operator_router.message(ChatTypeFilter(is_group=False), HasRole(Role.OPERATOR))
async def start_operator(message: Message):
    await message.answer("Здравствуйте, оператор")


@operator_router.message(ChatTypeFilter(is_group=True), HasRole(Role.OPERATOR, Role.ADMIN))
async def reply_to_client(message: Message):
    with session_factory() as session:
        user = session.query(User).filter(User.message_thread_id == message.message_thread_id).first()
        if user:
            await message.bot.copy_message(
                user.telegram_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        else:
            await message.answer("Пользователь не найден")
