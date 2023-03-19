from back.ekool_parser import EkoolParser
from datetime import datetime, timedelta
import shutil
from rich.console import Console
from rich.table import Table
from bs4 import BeautifulSoup
import sys

class EkoolPrompt():
    def __init__(self, cfg) -> None:
        self.con = Console()
        self.cfg = cfg

        self.logged_in = False
        self.parsed_info = {
            'next_tasks': None,
            'feed': None
        }
        self.logged_in_as = ''
        self.cmd_keys = {
            'h': self.help, 
            'l': self.login,
            'hn': self.next_homework,
            'lg': self.last_feed,
            'q': self.quit,
            'r': self.reload
            }

        self.weekday = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: None,
            6: None
        }
    
    def reload(self):
        self.parsed_info = {
            'next_tasks': None,
            'feed': None
        }

    def quit(self):
        sys.exit()

    @staticmethod
    def get_dates_list():
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        delta = end_date - start_date 
        days = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
        return list(map(lambda n: n.strftime("%d.%m.%Y"), days))

    def get_next_days(self):
        now = datetime.now()
        last = now + timedelta(days=7)
        homework = self.ekool.get_assignments_for_timeframe(now, last).assignments
        next_days = []
        for i in homework:
            similar_is = False
            for x in next_days:
                if x['day'] == i.deadLine:
                    x['assignments'].append(i)
                    similar_is = True
            if similar_is == False:
                next_days.append({
                    'day': i.deadLine,
                    'assignments': [i]
                    })
        next_days.sort(key = lambda x: datetime.strptime(x['day'], '%d.%m.%Y'))
        self.parsed_info['next_tasks'] = next_days

    def get_credentials(self):
        self.cred_login = self.cfg['username']
        self.cred_pass = self.cfg['password']

    def prompt_cycle(self):
        while True:
            self.width, self.height = shutil.get_terminal_size((50, 20))
            self.con.print('')
            prompt = f"[bold] EKool {self.logged_in_as} > [/]"
            inp = self.con.input(prompt=prompt)
            self.con.print('')
            self.argos = inp.split(' ')
            self.argos[:] = [item for item in self.argos if item != '']
            if len(self.argos) > 0:
                self.parse_prompt()
            else:
                print('Not enough args')

    def parse_prompt(self):
        if self.argos[0] not in list(self.cmd_keys.keys()):
            print('Wrong first argument!')
            return
        
        self.cmd_keys[self.argos[0]]()

    def help(self):
        pass

    def login(self):
        if self.logged_in == True:
            print("You're already logged in!")

        self.get_credentials()
        
        self.ekool = EkoolParser(self.cred_login, self.cred_pass)
        if self.ekool.login() == True:
            self.logged_in_as = '[' + self.cred_login + ']'
            print(f'Logged in as [{self.cred_login}]')
            self.logged_in = True
        else:
            print('Failed to log in!')
            self.logged_in = False

    def next_homework(self):
        if self.logged_in == False:
            print('You aren\'t logged in!')
            return
        
        if not self.parsed_info['next_tasks']:
            self.get_next_days()

        if len(self.argos) > 1:
            if len(self.argos) > 2:
                if len(self.argos) > 3:
                    self.work_update(self.argos[1], self.argos[2], self.argos[3])
                else:
                    self.print_one_entry(self.argos[1], self.argos[2])
            else:
                self.print_one_day(self.argos[1])
        else:
            self.print_all_homework()
    
    def work_update(self, arg1, arg2, arg3):
        next_days = self.parsed_info['next_tasks']
        try:
            day = int(arg1)
            entry = int(arg2)
        except ValueError:
            print('Wrong type!')
            return

        if int(day) - 1 not in range(8):
            return

        num = self.get_dates_list()[int(day) - 1] 
        found = None
        for u in next_days:
            if u['day'] == num:
                found = u
        if found:
            pass
        else:
            print('\tNo homework today!')
            return

        if entry not in range(1, len(found['assignments']) + 1):
            print('Entry out of range!')

        info = found['assignments'][entry - 1]
        if arg3 == 'done':
            self.ekool.toggle_task_done(info)
            print('Ok?')


    def print_one_day(self, arg1):
        next_days = self.parsed_info['next_tasks']
        day = arg1
        if not isinstance(day, str):
            return
        if int(day) - 1 not in range(8):
            return

        num = self.get_dates_list()[int(day) - 1]
        weekday = self.weekday[datetime.strptime(num, '%d.%m.%Y').weekday()]
        found = None
        for u in next_days:
            if u['day'] == num:
                found = u
        if found:
            self.con.print(self.get_day_table(weekday, found['assignments'])) 
        else:
            print(weekday + ':\n\tNo homework today!')
            return

    def print_one_entry(self, arg1, arg2):
        next_days = self.parsed_info['next_tasks']
        try:
            day = int(arg1)
            entry = int(arg2)
        except ValueError:
            print('Wrong type!')
            return

        if int(day) - 1 not in range(8):
            return

        num = self.get_dates_list()[int(day) - 1] 
        found = None
        for u in next_days:
            if u['day'] == num:
                found = u
        if found:
            pass
        else:
            print('\tNo homework today!')
            return

        if entry not in range(1, len(found['assignments']) + 1):
            print('Entry out of range!')

        info = found['assignments'][entry - 1]
        self.print_entry_table(info)

    def print_all_homework(self):
        next_days = self.parsed_info['next_tasks']
        ts = Table(show_header=False, expand=True)
        ts.add_column()
        for index, i in enumerate(self.get_dates_list()):
            weekday = self.weekday[datetime.strptime(i, '%d.%m.%Y').weekday()]
            if not weekday:
                continue
            found = None
            for x in next_days:
                if x['day'] == i:
                    found = x
            if found:
                self.con.print(self.get_day_table(f'{index + 1}: ' + weekday, found['assignments'])) 
            else:
                self.con.print(weekday + ':\n\tNo homework today!')
                continue

    def get_day_table(self, day, t_data):
        t = Table(title=day, title_style='bright_white bold', title_justify='left', expand=True)
        t.add_column(width=1, style='gold1')
        t.add_column('D', width=1, style='deep_sky_blue1')
        t.add_column('Subject', width=25, style='orange_red1')
        t.add_column('Title', ratio=1, style='bright_white')
        t.add_column('C', width=1, style='magenta1')
        t.add_column('Id', style='green')
        t.add_column('Teacher', width=25, style='green3')

        for e, u in enumerate(t_data):
            done = ''
            c = ''
            if u.is_done == True:
                done = '+'
            else:
                done = '-'
            if u.content != '':
                c = '+'
            else:
                c = '-'
            t.add_row(str(e + 1), done, u.subject_name, u.title, c, str(u.id), u.author)
        return t

    def print_entry_table(self, td):
        soup = BeautifulSoup(td.content, 'lxml')    
        content = ''
        for i in soup.get_text('\n').split('\n'):
            if i != '' and i != ' ':
                content += '\n' + i
        self.con.print(td.deadLine + '\n' + td.title, style='red')
        done = False
        if td.is_done == True:
            done = True
        self.con.print('Done: ' + str(done), style='gold1')
        graded = False
        if td.is_graded == True:
            graded = True
        self.con.print('Graded: ' + str(graded), style='yellow1')
        test = False
        if td.is_test == True:
            test = True
        self.con.print('Test: ' + str(test), style='yellow1')
        if td.content != '':
            self.con.print(content, style='green')
        self.con.print('\n' + td.author, style='cyan')
        if td.teacher_attachments: 
            self.con.print('Attachments:', style='blue')
            for attachment in td.teacher_attachments:
                self.con.print('[yellow]' + attachment['fileName'] + ': [blue]https://ekool.eu' + attachment['url'])

    def get_feed(self):
        feed = self.ekool.get_feed().feed
        self.parsed_info['feed'] = feed

    def last_feed(self):
        if self.logged_in == False:
            print('You aren\'t logged in!')
            return
        
        if not self.parsed_info['feed']:
            self.get_feed()

        if len(self.argos) > 2:
            self.print_feed_item()
        else:
            self.print_feed()

    def print_feed(self):
        t = Table(expand=True, show_lines=True)
        t.add_column(width=2)
        t.add_column('Grade', max_width=5, style='gold1')
        t.add_column('Type', max_width=18, style='bright_red')
        t.add_column('Subject', max_width=20, style='bright_blue')
        t.add_column('Author', style='bright_magenta')
        t.add_column('Message', style='bright_cyan', ratio=1)
        t.add_column('Date', style='bright_green', width=16)
        try:
            num = int(self.argos[1])
        except:
            print('Invalid second argument!')
            return

        if num > 59 and num < 1:
            num = 59

        for index, y in enumerate(self.parsed_info['feed'][0:num]):
            item_type = ''
            subject_name = ''
            content = ''
            grade = ''
            author = y.author_name
            modified = y.last_modified
            if y.item_type == 1:
                subject_name = y.subject_name
                grade = str(y.grade)
                if y.grade_type_id == 1:
                    item_type = 'Lesson grade'
                    if y.text_content:
                        content = y.text_content
                elif y.grade_type_id == 2:
                    item_type = 'Term grade'
                elif y.grade_type_id == 4:
                    item_type = 'Annual grade'
                elif y.grade_type_id == 5:
                    item_type = 'Assessment grade'
                    if y.test == True:
                        item_type = 'Test grade'
                    if y.text_content:
                        content = y.text_content
                elif y.grade_type_id == 6:
                    item_type = 'Behaviour annual'
                elif y.grade_type_id == 7:
                    item_type = 'Diligence annual'
                elif y.grade_type_id == 8:
                    item_type = 'Behaviour term'
                elif y.grade_type_id == 9:
                    item_type = 'Diligence term'
                else:
                    continue
            elif y.item_type == 2:
                item_type = 'Comment'
                content = y.text_content
            elif y.item_type == 5:
                item_type = 'Message'
                bs = BeautifulSoup(y.content, 'lxml')
                conts = []
                for i in bs.get_text('\n').split('\n'):
                    if i != '' and i != ' ':
                        conts.append(i)
                bs_content = '\n'.join(conts)
                if y.title != '':
                    content = f'[bold]{y.title}[/bold]\n{bs_content}'
                else:
                    content = f'{bs_content}'

            else:
                continue
            t.add_row(str(index + 1), grade, item_type, subject_name, author, content, modified)

        self.con.print(t)

    def print_feed_item(self):
        pass
