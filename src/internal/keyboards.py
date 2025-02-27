from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup


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
