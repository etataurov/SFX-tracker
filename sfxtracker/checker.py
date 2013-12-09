import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
import requests

from .config import *


logging.basicConfig(format=u'%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)


class Checker:
    def __init__(self, url, to_email):
        self.url = url
        self.to_email = to_email
        self.changes = {}

    def make_message(self, changes):
        message = []
        for date in sorted(self.changes.keys(), key=lambda x: time.strptime(x, '%Y-%m-%d %H:%M:%S')):
            message.append("<p>{}: {}</p>".format(date, self.changes[date]))
        for new_date, new_event in changes:
            message.append("<p><b>{}</b>: {}</p>".format(new_date, new_event))
        return '\n'.join(message)

    def send_new_changes(self, changes):
        msg = MIMEMultipart('alternative')

        msg['Subject'] = 'New parcel event!'
        msg['From'] = FROM_EMAIL
        msg['To'] = self.to_email

        text = MIMEText(self.make_message(changes), 'html')
        msg.attach(text)

        s = smtplib.SMTP(SMTP_SERVER, port=SMTP_PORT)
        s.login(LOGIN, PASSWORD)
        try:
            log.debug('sending new mail to {}'.format(self.to_email))
            s.sendmail(FROM_EMAIL, [self.to_email], msg.as_string())
        finally:
            s.quit()

    def parse_content(self, content):
        parsed = BeautifulSoup(content)
        new_changes = []
        for status_div in parsed.find_all('div', class_='status')[:0:-1]:  # newer events are higher
            date = status_div.find('div', class_='date').text
            event = status_div.find('div', class_='description').text
            if date not in self.changes:
                new_changes.append((date, event))
                log.info('new event [{}]: {}'.format(date, event))
        if new_changes:
            self.send_new_changes(new_changes)
            self.save_changes(new_changes)
        else:
            log.info('no new events')

    def check_status(self):
        log.debug('checking parcel status')
        response = requests.get(self.url)
        self.parse_content(response.content)

    def start(self):
        self.check_status()

    def save_changes(self, changes):
        for date, event in changes:
            self.changes[date] = event
