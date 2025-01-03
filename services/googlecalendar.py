import pprint
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build



# calendarId = 'YS5sLnBvbm9tYXJldjE5ODlAZ21haWwuY29t8@group.calendar.google.com'
# SERVICE_ACCOUNT_FILE = 'credentials.json'


class GoogleCalendar(object):
    # CALENDAR_ID = 'a.l.ponomarev1989@gmail.com'
    CALENDAR_ID = 'detox.tour.turkey@gmail.com'
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    # FILE_PATH = 'credentials.json'
    FILE_PATH = 'services/credentials.json'


    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH,
            scopes=self.SCOPES)
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }
        return self.service.calendarList().insert(
            body=calendar_list_entry).execute()

    def create_event(self,  summary: str, description: str, time_dict: dict, data_event: str):
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': f'{data_event}T{time_dict["H1"]}:{time_dict["M1"]}:00+03:00',
                'timeZone': 'Europe/Moscow'
            },
            'end': {
                'dateTime': f'{data_event}T{time_dict["H2"]}:{time_dict["M2"]}:00+03:00',
                'timeZone': 'Europe/Moscow'
            },
        }
        return self.service.events().insert(calendarId=self.CALENDAR_ID,
                                            body=event).execute()

    def get_event(self, data: str, event_time: str = '18:00'):
        list_event = self.service.events().list(calendarId=self.CALENDAR_ID).execute()
        filter_event = []
        for event in list_event['items']:
            if 'dateTime' in event['start'].keys():
                if data in event['start']['dateTime']:
                    filter_event.append(event)
        count_event = 0
        if filter_event:
            for event in filter_event:
                hour = event['start']['dateTime'].split('T')[1].split(':')[0]
                minute = event['start']['dateTime'].split('T')[1].split(':')[1]
                s2 = f'{hour}:{minute}'
                FMT = '%H:%M'
                tdelta = datetime.strptime(event_time, FMT) - datetime.strptime(s2, FMT)
                if event_time == '18:00':
                    if 0 < (tdelta.seconds / 3600) and (tdelta.seconds / 3600) <= 4:
                        count_event += 1
                elif event_time == '20:00':
                    if 0 < (tdelta.seconds / 3600) and (tdelta.seconds / 3600) <= 2:
                        count_event += 1
        return filter_event, count_event




calendarG = GoogleCalendar()

# pprint.pprint(calendarG.get_calendar_list())
# calendar_id = 'a.l.ponomarev1989@gmail.com'
# calendarG.add_calendar(calendar_id='detox.tour.turkey@gmail.com')

# time_dict = {"H1": 14, "M1": 40, "H2": 15, "M2": 20}
# calendarG.create_event(time_dict=time_dict,
#                        summary='Записи на консультацию Тестовая',
#                        description='Проверка работы',
#                        data_event='2024-09-26')
# pprint.pprint(calendarG.get_calendar_list())
# event = calendarG.get_event(data='2024-09-24')
# print(event)

