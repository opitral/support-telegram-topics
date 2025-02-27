from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from internal.models import Language, Issue
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
