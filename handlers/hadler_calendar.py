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
        # await callback_query.answer(text=f'Вы выбрали {data_note}', show_alert=True)
        event_list = calendarG.get_event(data=data_note)
        await callback_query.message.answer(text='Выберите время для записи',
                                            reply_markup=kb.keyboards_slots(list_event=event_list))
    else:
        await callback_query.answer(text=f'Вы ничего выбрали', show_alert=True)
    await callback_query.answer()


@router.callback_query(lambda callback: 'slot' in callback.data)
async def get_time_slot(callback: CallbackQuery, state: FSMContext, bot: Bot):
    slot_time = callback.data.split('_')[1]
    data = await state.get_data()
    type_product = {"1": "Экспресс -консультация",
                    "2": "Консультация с разбором анализов и назначений",
                    "3": "Составление индивидуальной оздоровительной программы на 3 месяца",
                    "4": "ВИП-программа по здоровью",
                    "5": "Ведение в группе онлайн-детокс",
                    "6": "Программа похудения на 3 месяца",
                    "7": "Программа похудения на 1 месяц",
                    "8": "Менторство врачей"}
    H1 = int(slot_time.split(":")[0])
    M1 = int(slot_time.split(":")[1])
    event_start = time(hour=H1, minute=M1)
    event_finish = (datetime.combine(datetime.today(), event_start) + timedelta(minutes=40)).time()
    event_finish_str = event_finish.strftime("%H:%M")
    H2 = int(event_finish_str.split(":")[0])
    M2 = int(event_finish_str.split(":")[0])
    time_dict = {"H1": H1, "M1": M1, "H2": H2, "M2": M2}
    calendarG.create_event(summary=f'Пользователь {data["fullname"]} приобрел продукт "{type_product[data["item"]]}"',
                           description=f'ФИО: {data["fullname"]}\nТелефон: {data["phone"]}',
                           time_dict=time_dict)
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_message(chat_id=admin,
                                   text=f'Пользователь {data["fullname"]} приобрел продукт'
                                        f' "{type_product[data["item"]]}"\n'
                                        f'ФИО: {data["fullname"]}\nТелефон: {data["phone"]}')
        except:
            pass
    await callback.answer()
