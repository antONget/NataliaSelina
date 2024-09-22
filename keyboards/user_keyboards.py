from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_start_menu():
    logging.info("keyboard_start_menu")
    button_1 = InlineKeyboardButton(text='Консультация',  callback_data=f'consultation_product')
    button_2 = InlineKeyboardButton(text='Оздоровительная программа', callback_data=f'wellness_product')
    button_3 = InlineKeyboardButton(text='Программа похудения', callback_data=f'weightloss_product')
    button_6 = InlineKeyboardButton(text='Менторство врачей', callback_data=f'mentoring_product')
    button_4 = InlineKeyboardButton(text='👤/👥 КАК ВЫБРАТЬ ПРОГРАММУ?', callback_data=f'select_product')
    button_5 = InlineKeyboardButton(text='👩‍💻 ПОДДЕРЖКА', callback_data=f'support')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_6], [button_4], [button_5]],)
    return keyboard


def keyboard_consultation():
    logging.info("keyboard_consultation")
    button_1 = InlineKeyboardButton(text='Экспресс -консультация',  callback_data=f'item_1')
    button_2 = InlineKeyboardButton(text='Консультация с разбором анализов и назначений', callback_data=f'item_2')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_wellness():
    logging.info("keyboard_wellness")
    button_1 = InlineKeyboardButton(text='Индивидуальная оздоровительная программа',  callback_data=f'item_3')
    button_2 = InlineKeyboardButton(text='ВИП-программа по здоровью', callback_data=f'item_4')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
    return keyboard


def keyboard_weightloss():
    logging.info("keyboard_wellness")
    button_1 = InlineKeyboardButton(text='Группа онлайн-детокс',  callback_data=f'item_5')
    button_2 = InlineKeyboardButton(text='Программа на 3 месяца', callback_data=f'item_6')
    button_3 = InlineKeyboardButton(text='Программа на 1 месяц', callback_data=f'item_7')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]],)
    return keyboard


def keyboard_main_menu():
    logging.info("keyboard_main_menu")
    button_1 = KeyboardButton(text='🏠 Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard


def keyboard_sign_up():
    logging.info("keyboard_sign_up")
    button_1 = InlineKeyboardButton(text='Записаться',  callback_data=f'sign_up')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]], )
    return keyboard


def keyboard_user_agreement() -> InlineKeyboardMarkup:
    logging.info("keyboard_user_agreement")
    button_1 = InlineKeyboardButton(text='☑️ Соглашаюсь', callback_data='agreement')
    button_2 = InlineKeyboardButton(text='>> ПРОДОЛЖИТЬ', callback_data='continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_user_agreement_update() -> InlineKeyboardMarkup:
    logging.info("keyboard_user_agreement_update")
    button_1 = InlineKeyboardButton(text='✅ Соглашаюсь', callback_data=' ')
    button_2 = InlineKeyboardButton(text='>> ПРОДОЛЖИТЬ', callback_data='continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_get_contact() -> ReplyKeyboardMarkup:
    logging.info("keyboards_get_contact")
    button_1 = KeyboardButton(text='Отправить свой контакт ☎️',
                              request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True
    )
    return keyboard


def keyboard_payment(payment_url: str, payment_id: int, amount: str) -> None:
    logging.info("keyboard_select_period_sales")
    button_1 = InlineKeyboardButton(text='Проверить оплату', callback_data=f'payment_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=f'https://yookassa.ru/')
    # button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=f'{payment_url}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard