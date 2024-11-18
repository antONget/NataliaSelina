from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import LabeledPrice

from keyboards import user_keyboards as kb
from filter.admin_filter import IsSuperAdmin
from config_data.config import Config, load_config
from database import requests as rq
from filter.filter import validate_russian_phone_number
from services.payments import create_payment, check_payment
from handlers.hadler_calendar import set_calendar
from fluentogram import TranslatorRunner

import re
import logging
import random
import asyncio
router = Router()
# Загружаем конфиг в переменную config
config: Config = load_config()


class User(StatesGroup):
    fullname = State()
    phone = State()
    content = State()


@router.message(CommandStart())
async def process_start_command_user(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
    """
    Пользовательский режим запускается если, пользователь ввел команду /start
     или если администратор ввел команду /user
    1. Добавляем пользователя в БД если его еще нет в ней
    :param message:
    :param state:
    :param i18n:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    # await set_calendar(message=message, state=state)
    # return
    await state.set_state(state=None)
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = "user_name"
    await rq.add_user(tg_id=message.chat.id,
                      data={"tg_id": message.chat.id, "username": username})
    await message.answer(text=f'Добро пожаловать!',
                         reply_markup=kb.keyboard_main_menu())
    await message.answer(text=i18n.start.text(),
                         reply_markup=kb.keyboard_start_menu())
    # await message.answer(text=f'Это официальный бот-ассистент Натальи Селиной 🌱\n\n'
    #                           f'Воспользуйтесь кнопками ниже, чтобы записаться на программу персонального ведения,'
    #                           f' группового ведения, или для того, чтобы зайти в ЛК или задать вопрос ⤵',
    #                      reply_markup=kb.keyboard_start_menu())


@router.callback_query(F.data == 'support')
async def process_question(callback: CallbackQuery, i18n: TranslatorRunner) -> None:
    """
    Обработка обратной связи
    :param callback:
    :param i18n:
    :return:
    """
    logging.info(f'process_question: {callback.message.chat.id}')
    await callback.message.answer(text=i18n.support.text(support_username=config.tg_bot.support_username))
    # await callback.message.answer(text=f'Если у вас возникли вопросы по работе бота или у вас есть предложения,'
    #                                    f' то можете написать {config.tg_bot.support_username}')


@router.callback_query(F.data == 'select_product')
async def process_select_product(callback: CallbackQuery, i18n: TranslatorRunner) -> None:
    """
    Как выбрать программу
    :param callback:
    :param i18n:
    :return:
    """
    logging.info(f'process_question: {callback.message.chat.id}')
    await callback.message.answer(text=i18n.select.programm(),
                                  reply_markup=kb.keyboard_select_programm())


@router.message(F.text == '🏠 Главное меню')
async def process_press_main_menu(message: Message, state: FSMContext, i18n: TranslatorRunner):
    """
    Нажата кнопка "🏠 Главное меню"
    :param message:
    :param state:
    :param i18n:
    :return:
    """
    logging.info(f'process_press_main_menu {message.chat.id}')
    await process_start_command_user(message=message, state=state, i18n=i18n)


@router.callback_query(F.data.endswith('product'))
async def process_product_one_step(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner):
    """
    Первый шаг в приобретение продукт
    :param callback:
    :param state:
    :param bot:
    :param i18n:
    :return:
    """
    logging.info(f'process_product_one_step {callback.message.chat.id}')
    try:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    except:
        pass
    product = callback.data.split('_')[0]
    await state.update_data(product=product)
    if product == 'consultation':
        await callback.message.answer_photo(
            photo='AgACAgIAAxkBAAMhZu_WbD9IYueoX0PynH9dM5c8f1gAAtnmMRuCboBLtu9WsVsODsYBAAMCAAN4AAM2BA',
            caption=i18n.product.consultation(),
            reply_markup=kb.keyboard_consultation())
    elif product == 'wellness':
        await callback.message.answer_photo(
            photo='AgACAgIAAxkBAAMkZu_YC4xAd5STB5P7OwnQjLGFH4cAAvLmMRuCboBL-PiUkB7vfHcBAAMCAAN4AAM2BA',
            caption=i18n.product.wellness(),
            reply_markup=kb.keyboard_wellness())
    elif product == 'weightloss':
        await callback.message.answer_photo(
            photo='AgACAgIAAxkBAAMmZu_Yp37bKoJVfEzvmDJBWoi1NXkAAvTmMRuCboBLi4uieFXeNxEBAAMCAAN5AAM2BA',
            caption=i18n.product.weightloss(),
            reply_markup=kb.keyboard_weightloss())
    else:
        await state.update_data(item='8')
        await callback.message.answer(
            text=i18n.get(f'detailed-description-{8}'),
            reply_markup=kb.keyboard_sign_up())
    await callback.answer()


@router.callback_query(F.data.startswith('item_'))
async def process_sign_up(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner):
    """
    Выводим подробное описание продукта и предлагаем записаться
    :param callback:
    :param state:
    :param bot:
    :param i18n:
    :return:
    """
    logging.info(f'process_sign_up {callback.message.chat.id}')
    item = callback.data.split("_")[-1]
    if item in ['6', '9', '10']:
        await process_sign_up(callback=callback, state=state, bot=bot, i18n=i18n)
        return
    try:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
    except:
        pass

    if item == 'indvidual':
        await callback.message.answer(text=i18n.get(f'detailed-description-{6}'),
                                      reply_markup=kb.keyboard_long_period())
        return

    await state.update_data(item=item)
    await callback.message.answer(text=i18n.get(f'detailed-description-{item}'),
                                  reply_markup=kb.keyboard_sign_up())
    await callback.answer()


@router.callback_query(F.data == 'sign_up')
async def process_sign_up_agreement(callback: CallbackQuery, state: FSMContext, bot: Bot,  i18n: TranslatorRunner):
    """
    Обработка нажатие на кнопку "Записаться"
    :param callback:
    :param state:
    :param bot:
    :param i18n:
    :return:
    """
    await state.update_data(agreement='no')
    data = await state.get_data()
    if data['item'] == '8':
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.message.answer(
            text=i18n.agreement(),
            reply_markup=kb.keyboard_user_agreement(),
            disable_web_page_preview=True)
    else:
        await callback.message.edit_text(text=i18n.agreement(),
                                         reply_markup=kb.keyboard_user_agreement(),
                                         disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data == 'agreement')
async def process_user_agreement(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    """
    Соглашение с пользовательским соглашением
    :param callback:
    :param state:
    :param i18n:
    :return:
    """
    logging.info(f'process_user_agreement {callback.message.chat.id}')
    await state.update_data(agreement='yes')
    await callback.message.edit_text(text=i18n.agreement(),
                                     reply_markup=kb.keyboard_user_agreement_update(),
                                     disable_web_page_preview=True)


@router.callback_query(F.data == 'continue')
async def process_continue(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    """
    Пользователь согласился с пользовательским соглашением
    :param callback:
    :param state:
    :param i18n:
    :return:
    """
    logging.info(f'process_continue {callback.message.chat.id}')
    data = await state.get_data()
    if data['agreement'] == 'no':
        await callback.answer(text=i18n.agreement.requirement(), show_alert=True)
        return
    await callback.message.edit_text(text=i18n.get_fullname(),
                                     reply_markup=None)
    await state.set_state(User.fullname)
    await callback.answer()


@router.message(F.text, StateFilter(User.fullname))
async def process_get_fullname(message: Message, state: FSMContext, i18n: TranslatorRunner):
    """
    Получаем ФИО
    :param message:
    :param state:
    :param i18n:
    :return:
    """
    logging.info(f'process_get_fullname {message.chat.id}')
    name_pattern = re.compile(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$')
    if name_pattern.match(message.text):
        await state.update_data(fullname=message.text)
        await message.answer(text=i18n.get_phone(),
                             reply_markup=kb.keyboards_get_contact())
        await state.set_state(User.phone)
    else:
        await message.answer(text=i18n.get_fullname.error())


@router.message(StateFilter(User.phone))
async def get_phone_user(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
    """
    Получаем номер телефона проверяем его на валидность и заносим его в БД
    :param message:
    :param state:
    :param i18n:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    # если номер телефона отправлен через кнопку "Поделится"
    if message.contact:
        phone = str(message.contact.phone_number)
    # если введен в поле ввода
    else:
        phone = message.text
        # проверка валидности отправленного номера телефона, если не валиден просим ввести его повторно
        if not validate_russian_phone_number(phone):
            await message.answer(text=i18n.get_phone.error())
            return
    # обновляем поле номера телефона
    await state.update_data(phone=phone)
    data = await state.get_data()
    item = data['item']
    # 1 Экспресс -консультация -5000 рублей
    # 2 Консультация с разбором анализов и назначений -12500
    # 3 Составление индивидуальной оздоровительной программы на 3 месяца -30000 рублей
    # 4 ВИП-программа по здоровью - 270000 рублей
    # 5 Ведение в группе онлайн-детокс-10000 рублей
    # 6 Программа похудения на 3 месяца - 90000 рублей
    # 7 Программа похудения на 1 месяц -50000 рублей
    # 8 Менторство врачей -300000 рублей
    type_product = {"1": "Экспресс -консультация",
                    "2": "Онлайн -консультация",
                    "3": "Составление индивидуальной оздоровительной программы на 3 месяца",
                    "4": "ВИП-программа по здоровью",
                    "5": "Ведение в группе онлайн-детокс",
                    "6": "Программа похудения на 3 месяца",
                    "7": "Программа похудения на 1 месяц",
                    "8": "Менторство врачей"}
    item_amount = {"1": "5000", "2": "12500", "3": "30000", "4": "27000",
                   "5": "10000", "6": "90000", "7": "50000", "8": "300000"}
    amount = item_amount[item]
    content = type_product[item]
    # amount = "10"
    await message.answer(text='Отлично, ваши данные успешно записаны!',
                         reply_markup=kb.keyboard_main_menu())
    await state.update_data(content=content)
    await state.update_data(amount=int(amount))
    # await message.answer(text=f'Оплатите продукт "{content}", после оплаты нажмите на кнопку «Проверить оплату» ⬇️ '
    #                           f'для выбора времени консультации',
    #                      reply_markup=kb.keyboard_payment_invoice(amount=amount))
    payment_url, payment_id = create_payment(amount=amount, chat_id=message.chat.id, content=content)
    await message.answer(text=f'Оплатите продукт "{content}", после оплаты нажмите на кнопку «Проверить оплату» ⬇️ '
                              f'для выбора времени консультации',
                         reply_markup=kb.keyboard_payment(payment_url=payment_url,
                                                          payment_id=payment_id,
                                                          amount=amount))


# @router.callback_query(F.data == 'wish_pay')
# async def wish_payment(callback: CallbackQuery, bot: Bot, state: FSMContext):
#     data = await state.get_data()
#     await bot.send_invoice(
#         chat_id=callback.message.chat.id,
#         title='Покупка',
#         description=data['content'],
#         payload=f'pay_{callback.message.chat.id}',
#         provider_token=config.tg_bot.yookassa_id,
#         currency='RUB',
#         start_parameter='test',
#         prices=[LabeledPrice(label="Руб.", amount=data["amount"]*100)]
#     )
#
#
# @router.pre_checkout_query()
# async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
#     logging.info('process_pre_checkout_query')
#     await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)
#
#
# @router.message(F.successful_payment)
# async def process_successful_payment(message: Message, state: FSMContext):
#     if message.successful_payment.invoice_payload == 'pay_{callback.message.chat.id}':
#         await message.answer(text='Платеж прошел успешно')
#         data = await state.get_data()
#         item = data['item']
#         if item == '1':
#             await message.answer(text='Пришлите материалы для консультации\n'
#                                       '📎 Прикрепите фото (можно несколько), видео или документ.')
#             await state.set_state(User.content)
#             await state.update_data(content=[])
#             await state.update_data(count=[])
#         else:
#             await set_calendar(message=message, state=state)
#     else:
#         await message.answer(text='Платеж не прошел')


@router.callback_query(F.data.startswith('payment_'))
async def check_pay(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay {callback.message.chat.id}')
    payment_id = callback.data.split('_')[1]
    result = check_payment(payment_id=payment_id)
    # result = 'succeeded'
    if result == 'succeeded':
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await callback.answer(text='Платеж прошел успешно', show_alert=True)
        data = await state.get_data()
        item = data['item']
        if item == '1':
            await callback.message.answer(text='Пришлите материалы для консультации\n'
                                               '📎 Прикрепите фото (можно несколько), видео или документ.')
            await state.set_state(User.content)
            await state.update_data(content=[])
            await state.update_data(count=[])
        else:
            await set_calendar(message=callback.message, state=state)
    else:
        await callback.message.answer(text='Платеж не подтвержден, если вы совершили платеж, то попробуйте проверить'
                                           ' его немного позднее или обратитесь в Поддержку в разделе Главного меню')
    await callback.answer()


@router.message(StateFilter(User.content), or_f(F.document, F.photo, F.video))
async def request_content_photo_text(message: Message, state: FSMContext):
    """
    Получаем от пользователя контент для публикации
    :param message:
    :param state:
    :return:
    """
    logging.info(f'request_content_photo_text {message.chat.id}')
    await asyncio.sleep(random.random())
    data = await state.get_data()
    list_content = data.get('content', [])
    count = data.get('count', [])
    if message.text:
        await message.answer(text=f'📎 Прикрепите фото (можно несколько), видео или документ.')
        return
    elif message.photo:
        content = message.photo[-1].file_id
        if message.caption:
            caption = message.caption
        else:
            caption = 'None'
        await state.update_data(caption=caption)

    elif message.video:
        content = message.video.file_id
        if message.caption:
            caption = message.caption
        else:
            caption = 'None'
        await state.update_data(caption=caption)

    elif message.document:
        content = message.document.file_id
        if message.caption:
            caption = message.caption
        else:
            caption = 'None'
        await state.update_data(caption=caption)

    list_content.append(content)
    count.append(content)
    await state.update_data(content=list_content)
    await state.update_data(count=count)
    await state.set_state(state=None)
    if len(count) == 1:
        await message.answer(text='Добавить еще материал или отправить?',
                             reply_markup=kb.keyboard_send())


@router.callback_query(F.data.endswith('content'))
async def send_add_content(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info(f'send_add_content {callback.message.chat.id}')
    answer = callback.data.split('_')[0]

    if answer == 'add':
        await state.set_state(User.content)
        await state.update_data(count=[])
        await callback.message.edit_text(text='Пришлите материалы для консультации\n'
                                              '📎 Прикрепите фото (можно несколько), видео или документ.')
    else:
        await callback.message.edit_text(text='Материалы от вас переданы\n\n',
                                         reply_markup=None)
        await set_calendar(message=callback.message, state=state)
        data = await state.get_data()
        content = data['content']

        for admin in config.tg_bot.admin_ids.split(','):
            try:
                # content_list = content.split(',')
                for item in content:
                    try:
                        await bot.send_photo(chat_id=admin,
                                             photo=item)
                    except:
                        try:
                            await bot.send_video(chat_id=admin,
                                                 video=item)
                        except:
                            await bot.send_document(chat_id=admin,
                                                    document=item)
                await bot.send_message(chat_id=admin,
                                       text=f'Пользователь @{callback.from_user.username}'
                                            f' {data["fullname"]} приобрел "Экспресс-консультация"\n'
                                            f'ФИО: {data["fullname"]}\n'
                                            f'Телефон: {data["phone"]}')
            except:
                pass
    await callback.answer()


