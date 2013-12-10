import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
import requests

from .config import *

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)


class Checker:
    def __init__(self, url, to_email, last_change_date=None):
        self.url = url
        self.to_email = to_email
        self.last_change_date = last_change_date

    def make_message(self, changes):
        message = []
        for new_date, new_event in changes:
            message.append("<p><b>{}</b>: {}</p>".format(new_date, new_event))
        message.append('<a href="{}">Предыдущие события</a>'.format(self.url))
        return '\n'.join(message)

    def send_new_changes(self, changes):
        msg = MIMEMultipart('alternative')

        msg['Subject'] = 'SFX: Обновление статуса посылки'
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
        for status_div in parsed.find_all('div', class_='status')[1:]:  # newer events are higher
            date = status_div.find('div', class_='date').text
            event = status_div.find('div', class_='description').text
            if self.last_change_date is None or self.last_change_date != date:
                new_changes.append((date, event))
                log.info('new event [{}]: {}'.format(date, event))
        if new_changes:
            self.send_new_changes(new_changes)
        else:
            log.info('no new events')

    def check_status(self):
        log.debug('checking parcel status')
        response = requests.get(self.url)
        self.parse_content(response.content)

    def start(self):
        self.check_status()
