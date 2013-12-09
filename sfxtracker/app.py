import os
from vase import Vase
from jinja2 import Environment, FileSystemLoader

app = Vase(__name__)

TEMPLATES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')


@app.route(path="/")
def index(request):
    if request.method == 'POST':
        # TODO: start task
        pass
    else:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template('index.html')
        return template.render()


if __name__ == '__main__':
    app.run(host='127.0.0.1')
