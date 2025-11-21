from aiogram.fsm.state import State,StatesGroup


class LoginState(StatesGroup):
    waiting_username = State()
    waiting_password = State()
