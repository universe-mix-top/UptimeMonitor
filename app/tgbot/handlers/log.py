import logging
from aiogram import Router, types, F
from app.modules.foreground.foreground import get_user_addr_list, get_user_logs, URL_REG, IP_ADDR_REG, parse_logs, is_addr_link, parse_address_list
from aiogram.fsm.context import FSMContext
from .states.states import LogState
from .keyboards.keyboards import start_keyboard

router = Router()

logger = logging.getLogger(__name__)

# вход
@router.message(F.text == F'открыть логи опросов')
async def catalog_url_logs(message: types.Message, state: FSMContext):
    addr_list = await get_user_addr_list(message.from_user.id)
    parsed_addr_list = parse_address_list(addr_list)

    await state.update_data(addr_list=addr_list)
    await state.set_state(LogState.waiting_for_url)

    if parsed_addr_list:
        await message.answer(f"выбери логи:\n{parsed_addr_list}")
    else:
        await state.clear()
        await message.answer(f"вы не добавляли сайты в список опроса", reply_markup=start_keyboard)


# обработка вывода лога по url
@router.message(F.text.isdecimal(), LogState.waiting_for_url)
@router.message(F.text.regexp(URL_REG), LogState.waiting_for_url)
@router.message(F.text.regexp(IP_ADDR_REG), LogState.waiting_for_url)
async def check_logs(message: types.Message, state: FSMContext):
    addr = is_addr_link(message.text, await state.get_value('addr_list'))
    if not addr:
        return await incorrect(message)

    tg_id = message.from_user.id
    logs = await get_user_logs(tg_id, addr)
    parsed_logs = parse_logs(logs)

    await state.clear()
    if parsed_logs:
        await message.answer(parsed_logs, reply_markup=start_keyboard)

    await message.answer('еще нет логов', reply_markup=start_keyboard)


# обработка ошибки ввода
@router.message(LogState.waiting_for_url)
async def incorrect(message: types.Message):
    await message.answer('некорректный ввод\n'
                         'введите номер адреса или его имя,\n'
                        r'чтобы отменить выбор лога введите /q')
