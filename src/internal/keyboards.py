from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from internal.models import Language, Issue, User
from internal.utils import CLIENT_LOCALE_MESSAGES

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

