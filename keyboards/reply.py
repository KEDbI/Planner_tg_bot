from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_RU


def _check_buttons(button_names: tuple) -> bool:
    for i in button_names:
        if i in LEXICON_RU:
            continue
        else:
            return False
    return True


def get_reply_keyboard(*button_names: str) -> ReplyKeyboardMarkup:
    if _check_buttons(button_names):
        builder = ReplyKeyboardBuilder()
        for i in button_names:
            builder.add(KeyboardButton(text=LEXICON_RU[i]))
        builder.row(width=4)
        kb = builder.as_markup(one_time_keyboard=True, resize_keyboard=True)
        return kb
