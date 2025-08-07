from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    til_tanalsh = State()
    bosh_sahifa = State()


class Instagram(StatesGroup):
    quality_choice = State()


class Youtube(StatesGroup):
    quality_choice = State()
