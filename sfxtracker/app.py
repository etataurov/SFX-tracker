import os
import asyncio
from vase import Vase
from jinja2 import Environment, FileSystemLoader
from .tracker import Tracker

app = Vase(__name__)
tracker = Tracker(5, 10)

TEMPLATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')


@app.route(path="/")
def index(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        url = request.POST.get('url')
        yield from tracker.add_task(url, email)
        return "OK"
    else:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template('index.html')
        return template.render()


def main(host='127.0.0.1'):
    loop = asyncio.get_event_loop()
    loop.call_soon(tracker.run)
    app.run(host=host)
