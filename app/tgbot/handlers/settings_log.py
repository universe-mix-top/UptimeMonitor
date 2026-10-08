import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.modules.foreground import get_user_monitors_presets, parse_monitors_preset
from .keyboards.keyboards import settings_inl_keyboard, start_keyboard
from .states.states import SettingsState

router = Router()

logger = logging.getLogger(__name__)

@router.message(F.text == 'мой список сайтов')
async def settings_log(massage: types.Message, state: FSMContext):
    monitors_preset = await get_user_monitors_presets(massage.from_user.id)
    parsed_monitors_preset = parse_monitors_preset(monitors_preset)
    await state.clear()

    if parsed_monitors_preset:
        return await massage.answer(parsed_monitors_preset, reply_markup=start_keyboard)

    await massage.answer('ваш список сайтов пуст', reply_markup=start_keyboard)


@router.message(F.text == 'настройка списка сайтов в списке опроса')
async def settings_log_action(massage: types.Message, state: FSMContext):
    await state.set_state(SettingsState.waiting_for_action)
    await massage.answer('выбери действие', reply_markup=settings_inl_keyboard)
