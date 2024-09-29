from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from services.googlecalendar import calendarG
from keyboards import calendar_keyboard as kb
import aiogram_calendar
from datetime import datetime, time, timedelta
from config_data.config import Config, load_config
import logging

router = Router()
config: Config = load_config()

class Calendar(StatesGroup):
    start = State()
    feedbak = State()


async def set_calendar(message: Message, state: FSMContext) -> None:
    """
    Подключаем календарь
    :param message:
    :param state:
    :return:
    """
    logging.info(f'set_calendar {message.chat.id}')
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2024, 1, 1), datetime(2030, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%m/%d/%y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await message.answer(
        "Выберите удобную дату для записи:",
        reply_markup=await calendar.start_calendar(year=int('20'+list_date1[2]), month=int(list_date1[0]))
    )
    await state.set_state(Calendar.start)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(Calendar.start))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        data_note = date.strftime("%Y-%m-%d")
        await state.update_data(data_note=date.strftime("%d-%m-%Y"))
        await state.update_data(data_event=data_note)
        event_list = calendarG.get_event(data=data_note)
        if len(event_list) >= 6:
            await callback_query.answer(text=f'На выбранную дату свободных слотов для консультации нет',
                                        show_alert=True)
            await set_calendar(message=callback_query.message, state=state)
            return
        await callback_query.message.answer(text=f'Выберите время для записи на {data_note}',
                                            reply_markup=kb.keyboards_slots(list_event=event_list))
    else:
        await callback_query.answer(text=f'Вы ничего выбрали', show_alert=True)
    await callback_query.answer()


@router.callback_query(lambda callback: 'slot' in callback.data)
async def get_time_slot(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info(f'get_time_slot {callback.message.chat.id}')
    slot_time = callback.data.split('_')[1]
    if slot_time == '❌':
        await callback.answer(text='Это время занято выберите другое время или дату', show_alert=True)
        return
    data = await state.get_data()
    H1 = int(slot_time.split(":")[0])
    M1 = int(slot_time.split(":")[1])
    event_start = time(hour=H1, minute=M1)
    event_finish = (datetime.combine(datetime.today(), event_start) + timedelta(minutes=40)).time()
    event_finish_str = event_finish.strftime("%H:%M")
    H2 = int(event_finish_str.split(":")[0])
    M2 = int(event_finish_str.split(":")[1])
    time_dict = {"H1": H1, "M1": M1, "H2": H2, "M2": M2}
    await state.update_data(time_dict=time_dict)
    await state.update_data(slot_time=slot_time)
    await callback.message.edit_text(text=f'Записать вас на {data["data_note"]} - {slot_time}?',
                                     reply_markup=kb.keyboard_confirm_slot())
    await callback.answer()


@router.callback_query(F.data.startswith('order_'))
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logging.info(f'confirm_order {callback.message.chat.id}')
    answer = callback.data.split('_')[-1]
    if answer == 'change':
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)
        await set_calendar(message=callback.message, state=state)
        await callback.answer()
        return
    data = await state.get_data()
    type_product = {"1": "Экспресс -консультация",
                    "2": "Консультация с разбором анализов и назначений",
                    "3": "Составление индивидуальной оздоровительной программы на 3 месяца",
                    "4": "ВИП-программа по здоровью",
                    "5": "Ведение в группе онлайн-детокс",
                    "6": "Программа похудения на 3 месяца",
                    "7": "Программа похудения на 1 месяц",
                    "8": "Менторство врачей"}
    time_dict = data['time_dict']
    slot_time = data['slot_time']
    data_event = data['data_event']
    calendarG.create_event(summary=f'Пользователь {data["fullname"]} приобрел продукт "{type_product[data["item"]]}"',
                           description=f'ФИО: {data["fullname"]} Телефон: {data["phone"]}',
                           time_dict=time_dict,
                           data_event=data_event)
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_message(chat_id=admin,
                                   text=f'Пользователь @{callback.from_user.username} приобрел продукт '
                                        f'"{type_product[data["item"]]}"\n'
                                        f'ФИО: {data["fullname"]}\n'
                                        f'Телефон: {data["phone"]}\n'
                                        f'Дата консультации: {data["data_note"]}\n'
                                        f'Время консультации: {slot_time}\n\n'
                                        f'Нажмите кнопку "Консультация проведена" для получения отзыва от клиента',
                                   reply_markup=kb.keyboard_feedback(tg_id=callback.message.chat.id))
        except:
            pass
    await callback.message.edit_text(text=f'Вы записаны на {data["data_note"]} - {slot_time}.\n\n'
                                          f'Спасибо! С вами свяжутся',
                                     reply_markup=None)
    await callback.answer()


@router.callback_query(F.data.startswith('feed_back_'))
async def get_feedback(callback: CallbackQuery, bot: Bot):
    logging.info(f'get_feedback {callback.message.chat.id}')
    await callback.message.edit_text(text='Запрос на отзыв направлен клиенту',
                                     reply_markup=None)
    try:
        await bot.send_message(chat_id=callback.data.split('_')[-1],
                               text='Оставьте отзыв о проведенной консультации',
                               reply_markup=kb.keyboard_set_feedback())
    except:
        pass
    await callback.answer()


@router.callback_query(F.data == 'set_feedback')
async def set_feedback(callback: CallbackQuery, state: FSMContext):
    logging.info(f'set_feedback {callback.message.chat.id}')
    await callback.message.edit_text(text='Напишите ваши впечатления',
                                     reply_markup=None)
    await state.set_state(Calendar.feedbak)
    await callback.answer()


@router.message(F.text, StateFilter(Calendar.feedbak))
async def text_feedback(message: Message, state: FSMContext, bot: Bot):
    logging.info(f'text_feedback {message.chat.id}')
    data = await state.get_data()
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_message(chat_id=admin,
                                   text=f'Пользователь @{message.from_user.username}'
                                        f' {data["fullname"]} "\n'
                                        f'ФИО: {data["fullname"]}\n'
                                        f'Телефон: {data["phone"]}\n'
                                        f'Оставил отзыв:\n'
                                        f'{message.text}')
        except:
            pass
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.answer(text=
                         'Благодарю, Ваше мнение нам очень важен и будет полезен для повышения качества наших услуг')
