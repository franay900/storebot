import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from backend.models import Category
from asgiref.sync import sync_to_async

# Объект бота
bot = Bot(token="6827932092:AAGjXfkoOyWEcAKhKbuJnw_OjhgiqS5PNWA")
# Диспетчер
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, это бот!")


@dp.message(Command("stop"))
async def cmd_start(message: types.Message):
    await message.answer("Пока")


@dp.message(Command("categories"))
async def cmd_categories(message: types.Message):
    categories = Category.objects.all()
    builder = InlineKeyboardBuilder()

    async for category in categories:
        builder.add(
            InlineKeyboardButton(text=category.name, callback_data=str(category.id)),
            InlineKeyboardButton(text='✏️ редактировать', callback_data=f'edit_{category.id}'),
            InlineKeyboardButton(text='❌ удалить', callback_data=f'delete_{category.id}'),

        )

    builder.add(InlineKeyboardButton(text='📝 Добавить категорию', callback_data='add_category'))
    builder.add(InlineKeyboardButton(text='◀️ Назад', callback_data='back_category'))

    await message.answer("Список категорий", reply_markup=builder.adjust(3).as_markup())


@dp.callback_query(F.data.startswith('delete_'))
async def delete_cetagory(callback: types.CallbackQuery):
    id = callback.data[7:]
    instance = await Category.objects.aget(id=id)
    await instance.adelete()

    await callback.message.delete()
    await cmd_categories(callback.message)

class CategoryState(StatesGroup):
    name = State()

class CategoryUpdateState(StatesGroup):
    name = State()


@dp.callback_query(F.data.startswith('edit_'))
async def edit_cetagory(callback: types.CallbackQuery, state: FSMContext):
    id = callback.data[5:]
    await state.set_state(CategoryUpdateState.name)
    await state.update_data(id=id)

    await callback.message.answer("Введите новое наименование категории")


@dp.message(CategoryUpdateState.name)
async def update_category_name(message: types.Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    id = data['id']
    instance = await Category.objects.aget(id=id)
    instance.name = message.text

    await instance.asave()
    await state.clear()

    await message.answer("Категория успешно обновлена!")
    await cmd_categories(message)



@dp.callback_query(F.data == 'add_category')
async def cmd_add_category(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CategoryState.name)
    await callback.message.answer("Введите название категории:")



@dp.message(CategoryState.name)
async def set_category_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await Category.objects.acreate(name=name)
    await message.answer("Категория успешно создана!")
    await cmd_categories(message)


async def main():
    await dp.start_polling(bot)
