import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.modules.foreground.foreground import get_timings, URL_REG, IP_ADDR_REG, parse_timings, is_timing_link, TIMING_DESCRIPTION, \
    set_user_monitor, timing_id_by_description
from .keyboards.keyboards import start_keyboard
from .states.states import AddSettingsState, SettingsState

router = Router()

logger = logging.getLogger(__name__)



# обработчики настроек по действию
@router.callback_query(F.data == 'add', SettingsState.waiting_for_action)
async def settings_log_add(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddSettingsState.waiting_for_action_param_url)
    await callback.message.answer('какой сайт вы хотите добавить')


# обработчики настроек по url
@router.message(F.text.regexp(URL_REG), AddSettingsState.waiting_for_action_param_url)
@router.message(F.text.regexp(IP_ADDR_REG), AddSettingsState.waiting_for_action_param_url)
async def settings_log_waiting_url_add(message: types.Message, state: FSMContext):
    await message.answer(f'адрес сайта: {message.text.lower()}')
    await state.update_data(url=message.text.lower())
    await state.set_state(AddSettingsState.waiting_for_action_param_timing)

    timings = await get_timings()
    parsed_timings = parse_timings(timings)

    await state.update_data(timings=timings)
    await message.answer('раз в какое время вы хотите опрашивать сайт\n'
                         f'выбери номер опроса:\n{parsed_timings}')

@router.message(AddSettingsState.waiting_for_action_param_url)
async def incorrect_url(message: types.Message):
    await message.answer('некорректный ввод\n'
                         'введите адрес сайта,\n'
                        r'чтобы отменить выбор введите /q')


# обработчики настроек по таймингу
@router.message(F.text.isdecimal(), AddSettingsState.waiting_for_action_param_timing)
@router.message(F.text.regexp(TIMING_DESCRIPTION), AddSettingsState.waiting_for_action_param_timing)
async def settings_log_waiting_timing_add(message: types.Message, state: FSMContext):
    timings = await state.get_value('timings')
    timing = is_timing_link(message.text, timings)
    if not timing:
        return await incorrect_timing(message)

    timing_id = timing_id_by_description(timing, timings)

    tg_id = message.from_user.id
    url = await state.get_value('url')
    res = await set_user_monitor(tg_id, url, timing_id)
    await state.clear()

    if not res:
        return await message.answer('у вас уже есть этот сайт в списке опроса\n'
                                    'настройки опроса не изменены', reply_markup=start_keyboard)

    await message.answer('настройки сохранены', reply_markup=start_keyboard)


@router.message(AddSettingsState.waiting_for_action_param_timing)
async def incorrect_timing(message: types.Message):
    await message.answer('некорректный ввод\n'
                         'введите номер тайминга,\n'
                        r'чтобы отменить выбор введите /q')