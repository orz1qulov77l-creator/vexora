"""Barcha bosqichli (FSM) holatlar shu yerda to'plangan."""
from aiogram.fsm.state import State, StatesGroup


class SearchMovie(StatesGroup):
    waiting_code = State()


class AddMovie(StatesGroup):
    code = State()
    title = State()
    description = State()
    video = State()
    poster = State()
    tariff = State()


class EditMovie(StatesGroup):
    waiting_code = State()
    choosing_field = State()
    new_value = State()


class AddChannel(StatesGroup):
    name = State()
    link = State()


class EditChannel(StatesGroup):
    choosing_channel = State()
    choosing_field = State()
    new_value = State()


class TopUpBalance(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()


class GivePremium(StatesGroup):
    waiting_user_id = State()
    waiting_days = State()


class SetPrices(StatesGroup):
    choosing_field = State()
    new_value = State()


class AddAdmin(StatesGroup):
    waiting_user_id = State()
    waiting_level = State()


class EditAdmin(StatesGroup):
    choosing_admin = State()
    choosing_action = State()
    waiting_level = State()


class Broadcast(StatesGroup):
    choosing_audience = State()
    waiting_message = State()
    confirm = State()


class AdSettings(StatesGroup):
    choosing_type = State()
    waiting_content = State()
    waiting_button = State()


class EditTexts(StatesGroup):
    choosing_key = State()
    new_value = State()


class EditStartMessage(StatesGroup):
    waiting_text = State()
