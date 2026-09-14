from aiogram.fsm.state import State, StatesGroup


class LogState(StatesGroup):
    waiting_for_url = State()


class SettingsState(StatesGroup):
    waiting_for_action = State()

class AddSettingsState(StatesGroup):
    waiting_for_action_param_url = State()
    waiting_for_action_param_timing = State()

class ChangeSettingsState(StatesGroup):
    waiting_for_action_param_url = State()
    waiting_for_action_param_timing = State()

class DelSettingsState(StatesGroup):
    waiting_for_action_param_url = State()