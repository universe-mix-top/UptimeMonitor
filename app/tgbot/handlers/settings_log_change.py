import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.modules.foreground.foreground import get_timings, URL_REG, IP_ADDR_REG, parse_timings, is_timing_link, TIMING_DESCRIPTION, \
    change_user_monitor, timing_id_by_description, is_addr_link, parse_address_list, get_user_addr_list
from .states.states import ChangeSettingsState, SettingsState
from .keyboards.keyboards import start_keyboard

router = Router()

logger = logging.getLogger(__name__)

# обработчики настроек по действию
@router.callback_query(F.data == 'change', SettingsState.waiting_for_action)
async def settings_log_change(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChangeSettingsState.waiting_for_action_param_url)

    addr_list = await get_user_addr_list(callback.from_user.id)
    await state.update_data(addr_list=addr_list)
    await callback.message.answer('какой сайт вы хотите изменить\n'
                         f'{parse_address_list(addr_list)}')


# обработчики настроек по url
@router.message(F.text.isdecimal(), ChangeSettingsState.waiting_for_action_param_url)
@router.message(F.text.regexp(URL_REG), ChangeSettingsState.waiting_for_action_param_url)
@router.message(F.text.regexp(IP_ADDR_REG), ChangeSettingsState.waiting_for_action_param_url)
async def settings_log_waiting_url_change(message: types.Message, state: FSMContext):
    addr_list = await state.get_value('addr_list')
    addr = is_addr_link(message.text.lower(), addr_list)
    if not addr:
        return await incorrect_url(message)

    await message.answer(f'адрес сайта: {addr}')
    await state.update_data(url=addr)
    await state.set_state(ChangeSettingsState.waiting_for_action_param_timing)

    timings = await get_timings()
    parsed_timings = parse_timings(timings)

    await state.update_data(timings=timings)
    await message.answer('раз в какое время вы хотите опрашивать сайт\n'
                         f'выбери номер опроса:\n{parsed_timings}')

@router.message(ChangeSettingsState.waiting_for_action_param_url)
async def incorrect_url(message: types.Message):
    await message.answer('некорректный ввод\n'
                         'введите адрес сайта или его номер,\n'
                        r'чтобы отменить выбор введите /q')


# обработчики настроек по таймингу
@router.message(F.text.isdecimal(), ChangeSettingsState.waiting_for_action_param_timing)
@router.message(F.text.regexp(TIMING_DESCRIPTION), ChangeSettingsState.waiting_for_action_param_timing)
async def settings_log_waiting_timing_change(message: types.Message, state: FSMContext):
    timings = await state.get_value('timings')
    timing = is_timing_link(message.text, timings)
    if not timing:
        return await incorrect_timing(message)

    timing_id = timing_id_by_description(timing, timings)

    tg_id = message.from_user.id
    url = await state.get_value('url')
    await state.clear()
    try:
        res = await change_user_monitor(tg_id, url, timing_id)
    except ValueError:
        return await message.answer('у вас нет этого сайта в списке сайтов\n'
                                    'воспользуйтесь функцией "добавить"', reply_markup=start_keyboard)
    if not res:
        return await message.answer('у вас уже есть этот сайт в списке опроса\n'
                                    'настройки опроса не изменены', reply_markup=start_keyboard)

    await message.answer('настройки сохранены', reply_markup=start_keyboard)


@router.message(ChangeSettingsState.waiting_for_action_param_timing)
async def incorrect_timing(message: types.Message):
    await message.answer('некорректный ввод\n'
                         'введите номер тайминга,\n'
                        r'чтобы отменить выбор введите /q')