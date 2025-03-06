from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder

from internal.models import Language, Issue, User
from internal.utils import CLIENT_LOCALE_MESSAGES, get_clients, get_clients_count
from pkg.config import settings

main_admin_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сделать рассылку клиентам"),
                KeyboardButton(text="Клиенты")
            ],
            [
                KeyboardButton(text="Админка")
            ]
        ],
        resize_keyboard=True
    )


class LanguageCbData(CallbackData, prefix="lang"):
    language: Language


languages_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Українська", callback_data=LanguageCbData(language=Language.UA).pack()),
            InlineKeyboardButton(text="Русский", callback_data=LanguageCbData(language=Language.RU).pack())
        ]
    ]
)


class IssueCbData(CallbackData, prefix="issue"):
    issue: Issue


def issues_kb(language: Language) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=CLIENT_LOCALE_MESSAGES[language]["sale"],
                            callback_data=IssueCbData(issue=Issue.SALE).pack()
                        ),
                        InlineKeyboardButton(
                            text=CLIENT_LOCALE_MESSAGES[language]["support"],
                            callback_data=IssueCbData(issue=Issue.SUPPORT).pack()
                        )
                    ]
                ]
            )


class MuteClientCbData(CallbackData, prefix="mute"):
    user_id: int


def mute_client_kb(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔇 Заглушить",
                    callback_data=MuteClientCbData(user_id=user.id).pack()
                )
            ]
        ]
    )


cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена")
        ]
    ],
    resize_keyboard=True
)


add_skip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить")
        ],
        [
            KeyboardButton(text="Пропустить")
        ]
    ],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

class YesBackCbData(CallbackData, prefix="yes_back"):
    yes: bool


yes_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=YesBackCbData(yes=True).pack()),
            InlineKeyboardButton(text="Назад", callback_data=YesBackCbData(yes=False).pack())
        ]
    ]
)

def custom_inline_kb(name: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, url=url)]
        ]
    )


back_skip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пропустить")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

class ClientsPageCbData(CallbackData, prefix="page"):
    page: int


def calc_clients_page(current_page: int = 1, is_next: bool = True) -> int:
    max_page = (get_clients_count() + settings.PAGE_SIZE - 1) // settings.PAGE_SIZE
    if is_next:
        if current_page < max_page:
            return current_page + 1
        return 1
    else:
        if current_page > 1:
            return current_page - 1
        return max_page


def clients_kb(page: int = 1) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    limit = settings.PAGE_SIZE * page
    offset = limit - settings.PAGE_SIZE
    clients = get_clients(offset, limit)
    for client in clients:
        kb.row(
            InlineKeyboardButton(
                text=f"{client.id}. {client.full_name} [{client.language.value.upper()}|{client.issue.value.upper()}]",
                url=f"{settings.GROUP_TELEGRAM_URL}/{client.message_thread_id}"
            )
        )

    kb.row(
        InlineKeyboardButton(
            text="⬅️",
            callback_data=ClientsPageCbData(page=calc_clients_page(page, is_next=False)).pack()
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=ClientsPageCbData(page=calc_clients_page(page, is_next=True)).pack()
        )
    )
    return kb.as_markup()
