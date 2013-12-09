import os
from vase import Vase
from jinja2 import Environment, FileSystemLoader
from .checker import Checker

app = Vase(__name__)

TEMPLATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')


@app.route(path="/")
def index(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        url = request.POST.get('url')
        checker = Checker(url, email)
        checker.start()
        return "OK"
    else:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template('index.html')
        return template.render()
