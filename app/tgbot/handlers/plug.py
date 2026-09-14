import logging

from aiogram.fsm.context import FSMContext
from aiogram import Router, types

router = Router()

logger = logging.getLogger(__name__)

@router.message()
async def plug(message: types.Message, state: FSMContext):
    logger.warning(f'plug triggered. message.text: {message.text}, state: {await state.get_state()}')
    await message.answer('не корректное сообщение')