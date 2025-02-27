from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from internal.filters import IsAdminFilter
from internal.keyboards import main_admin_kb

admin_router = Router()
admin_router.message.filter(IsAdminFilter())


@admin_router.message(Command("start"))
async def start_admin(message: Message):
    await message.answer("Здравствуйте, админ", reply_markup=main_admin_kb)
