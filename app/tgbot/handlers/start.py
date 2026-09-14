import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from .keyboards.keyboards import start_keyboard
from app.modules.foreground.foreground import user_registration

router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start(message: types.Message):
    res = await user_registration(message.from_user.id)
    if res: #  выводится только если пользователь реально новый
        logger.info(f'новый пользователь {message.from_user.username} зарегистрирован')
    await message.answer(f'это бот для регулярного опроса сайтов\n'
                         f'ты можешь \n'
                         f'          узнать работает ли сайт сейчас\n'
                         f'          добавить сайт в список фонового опроса\n'
                         f'          узнать логи сайта из списка опроса\n', reply_markup=start_keyboard)


# выход
@router.message(Command('q'))
async def base_exit(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('выход в главное меню', reply_markup=start_keyboard)
