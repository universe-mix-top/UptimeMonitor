import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.modules.foreground import URL_REG, IP_ADDR_REG, is_addr_link, del_user_monitor, get_user_addr_list, parse_address_list
from .keyboards.keyboards import start_keyboard
from .states.states import DelSettingsState, SettingsState

router = Router()

logger = logging.getLogger(__name__)

# обработчики настроек по действию
@router.callback_query(F.data == 'del', SettingsState.waiting_for_action)
async def settings_log_add(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DelSettingsState.waiting_for_action_param_url)

    addr_list = await get_user_addr_list(callback.from_user.id)
    await state.update_data(addr_list=addr_list)
    await callback.message.answer('какой сайт вы хотите удалить\n'
                         f'{parse_address_list(addr_list)}')


# обработчики настроек по url
@router.message(F.text.isdecimal(), DelSettingsState.waiting_for_action_param_url)
@router.message(F.text.regexp(URL_REG), DelSettingsState.waiting_for_action_param_url)
@router.message(F.text.regexp(IP_ADDR_REG), DelSettingsState.waiting_for_action_param_url)
async def settings_log_waiting_url_add(message: types.Message, state: FSMContext):
    addr_list = await state.get_value('addr_list')
    addr = is_addr_link(message.text.lower(), addr_list)
    if not addr:
        return await incorrect_url(message)

    tg_id = message.from_user.id
    url = addr
    res = await del_user_monitor(tg_id, url)
    await state.clear()

    if res is None:
        return await message.answer(f'сайт {addr} не найден в списке сайтов', reply_markup=start_keyboard)

    await message.answer(f'сайт {addr} удален из списка сайтов', reply_markup=start_keyboard)

@router.message(DelSettingsState.waiting_for_action_param_url)
async def incorrect_url(message: types.Message):
    await message.answer('некорректный ввод\n'
                         'введите адрес сайта или его номер,\n'
                        r'чтобы отменить выбор введите /q')

