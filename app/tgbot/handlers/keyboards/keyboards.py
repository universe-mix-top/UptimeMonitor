from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

builder = ReplyKeyboardBuilder()
# builder.button(text='работает ли сайт')
builder.button(text='настройка списка сайтов в списке опроса')
builder.button(text='открыть логи опросов')
builder.button(text='мой список сайтов')
builder.adjust(1, 1, 1, 1)
start_keyboard = builder.as_markup(input_field_placeholder="Выберите действие...", one_time_keyboard=True)

builder = ReplyKeyboardBuilder()
builder.button(text='добавить')
builder.button(text='изменить')
builder.button(text='удалить')
settings_keyboard = builder.as_markup(input_field_placeholder="Выберите действие...", one_time_keyboard=True)

builder = InlineKeyboardBuilder()
builder.button(text='добавить', callback_data='add')
builder.button(text='изменить', callback_data='change')
builder.button(text='удалить', callback_data='del')
settings_inl_keyboard = builder.as_markup()