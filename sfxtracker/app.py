import os
import logging
import asyncio
from vase import Vase
from jinja2 import Environment, FileSystemLoader
from wtforms import Form, StringField, validators
from .tracker import Tracker
from .config import TIMEOUT, URL_TIMEOUT, LOG_LEVEL

app = Vase(__name__)
tracker = Tracker(URL_TIMEOUT, TIMEOUT)

TEMPLATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)


class AddForm(Form):
    url = StringField('Ссылка с трекингом', [
        validators.InputRequired(message='Обязательное поле'),
        validators.URL(message='Неверный формат ссылки')])
    email = StringField('Почта для уведомлений', [
        validators.InputRequired(message='Обязательное поле'),
        validators.Length(min=6, message='Слишком короткий адрес'),
        validators.Email(message='Неверный формат адреса')
    ])


@app.route(path="/")
def index(request):
    log.debug('new request: {}'.format(request.ENV))
    form = AddForm(request.POST)
    if request.method == 'POST' and form.validate():
        email = form.data.get('email')
        url = form.data.get('url')
        try:
            yield from tracker.add_task(url, email)
        except Exception as exc:
            return str(exc)
        else:
            return "OK"
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('index.html')
    return template.render(form=form)


def main(host='127.0.0.1', port=3000):
    loop = asyncio.get_event_loop()
    loop.call_soon(tracker.run)
    app.run(host=host, port=port)
