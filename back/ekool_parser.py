import requests
from datetime import datetime
import json
import os
import hashlib
from back.ekool_types import AssignmentTimeframe, Assignment, Feed, FeedItem, EData
from datetime import datetime, timedelta
from pprint import pprint

class EkoolParser():
    def __init__(self, login, password) -> None:
        self.logged_in = False
        self.access_token = None
        self.refresh_token = None
        self.person_info = None
        self.student_id = None
        self.parents = None

        self.username = login
        self.password = password
        # Logime eKooli sisse
    
    def login(self):
        query_base = {
            'grant_type': "password",
            'client_id': 'mKool',
            'username': self.username,
            'password': self.password
        }

        headers = {
            'Authorization': 'Basic bUtvb2w6azZoOTdoYWZzcnZvbzNzZDEzZ21kdXE4YjZ0YnM1czE2anFtYTZydThmajN0dWVhdG5lOGE4amxtN2Jt',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.post(EData.SERVER_ROOT_URL + 'auth/oauth/token', data=query_base, headers=headers)
        login_state = r.json()
        if r.status_code == 200:
            self.logged_in = True
            self.access_token = login_state["access_token"]
            self.refresh_token = login_state["refresh_token"]
            self.get_person_data()
            return True
        else:
            return False

    def data_mine(self, pathElements):
        key = ''
        for element in pathElements:
            key += '/' + str(element)
        query_base = self.stampTheBase(self.get_query_base())

        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json;charset=UTF-8'
        }
        r = requests.post(EData.API_URL + key, data=json.dumps(query_base), headers=headers)
        if r.status_code == 200:
            return r.json()

    @staticmethod
    def get_query_base():
        push_settings = [True, True, True, True, True]
        return {
            'langCode': 'et',
            'version': "4.6.6",
            'deviceId': "1234567",
            'userAgent': "Google Chrome",
            'checksum': None,
            'pushType': '1',
            'localTime': str(int(datetime.timestamp(datetime.now()))),
            'gradePush': push_settings[0],
            'absencePush': push_settings[1],
            'noticePush': push_settings[2],
            'todoPush': push_settings[3],
            'messagePush': push_settings[4]
        }

    @staticmethod
    def format_date_for_ekool(date):
        date_str = str(date.day).zfill(2) + "." + str(date.month).zfill(2) + "." + str(date.year)
        return date_str

    @staticmethod
    def stampTheBase(query_base):
        str = ''
        str += query_base['langCode'] or ''
        str += query_base['version'][::-1] or ''
        str += query_base['deviceId'] or ''
        str += query_base['userAgent'] or ''
        str += query_base['pushType'] or ''
        str += query_base['version'] or ''
        str += query_base['localTime'] or ''
        query_base["checksum"] = hashlib.md5(str.encode('utf-8')).hexdigest()
        return query_base

    def get_assignments_for_timeframe(self, startingDate, endDate):
        starting_str = self.format_date_for_ekool(startingDate)
        end_str = self.format_date_for_ekool(endDate)

        raw_data = self.data_mine(
            ['todolist', str(self.student_id), starting_str, end_str])
        return AssignmentTimeframe(raw_data)

    # Võtame sisse logitud inimese kohta infot.
    def get_person_data(self):
        self.person_info = self.data_mine(['person'])
        self.student_id = str(self.person_info["roles"][0]["studentId"])
        return self.person_info

    # Vanemate võtmine
    def get_parents(self):
        '''
         {'students': [{'name1': 'NAME', 'name2': 'LASTNAME', 'profileImgFn': 'REDACTED'}], 'parents': [{'name1': 'PARENTNAME', 'name2': 'PARENTLASTNAME', 'profileImgFn': None}, {'name1': 'PARENTNAME', 'name2': 'PARENTLASTNAME', 'profileImgFn': None}]}
        :return:
        '''
        self.parents = self.data_mine(['family'])["parents"]
        return self.parents

    def get_feed_item(self, event_id):
        return self.data_mine(['feeditem',self.student_id, event_id])

    # Terve voo saamine
    def get_feed(self):
        return Feed(self.data_mine(['feed', self.student_id]))

    def toggle_task_done(self, task_obj):
        done = task_obj.is_done
        id = task_obj.id

        now = datetime.strptime(task_obj.deadLine, '%d.%m.%Y')
        monday = now - timedelta(days = now.weekday())
        friday = now - timedelta(days = now.weekday()) + timedelta(days=5)

        query_base = self.stampTheBase(self.get_query_base())
        query_base['studentId'] = self.student_id
        query_base['todo'] = done
        query_base['todoId'] = str(id)

        startDate = self.format_date_for_ekool(monday)
        endDate = self.format_date_for_ekool(friday)

        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json;charset=UTF-8'
        }
        print(EData.API_URL + '/todoChange/' + startDate + '/' + endDate)
        pprint(query_base)
 
        r = requests.post(EData.API_URL + '/todoChange/' + startDate + '/' + endDate, data=json.dumps(query_base), headers=headers)
        print(r.text)
