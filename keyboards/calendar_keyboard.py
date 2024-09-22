from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import time, timedelta, datetime
import logging


def keyboards_slots(list_event: list):
    """
    Клавиатура для вывода свободных слотов
    :param list_orders:
    :param block:
    :param status_order:
    :return:
    """
    logging.info(f"keyboards_slots")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    hour = 14
    minute = 0
    my_time = time(hour=hour, minute=minute)
    time_stop = time(hour=18, minute=0)
    while True:
        for event in list_event:
            dateTime = event['start']['dateTime']
            Time = dateTime.split('T')[1]
            hour_event = Time.split(":")[0]
            minute_event = Time.split(":")[1]
            time_event = time(hour=int(hour_event), minute=int(minute_event))
            if time_event == my_time:
                my_time = (datetime.combine(datetime.today(), my_time) + timedelta(minutes=40)).time()
                break
        else:
            text = f'{my_time.strftime("%H:%M")}'
            button = f'slot_{text}'
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
            # Увеличиваем время на 40 минут
            my_time = (datetime.combine(datetime.today(), my_time) + timedelta(minutes=40)).time()
            if my_time > time_stop:
                break
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup()