import os
from flask import Flask
from flask import render_template
app = Flask(__name__)
app.debug = True

# Static includes
import jinja2

def include_file(name):
    return jinja2.Markup(loader.get_source(env, name)[0])

loader = jinja2.PackageLoader(__name__, 'templates')
env = jinja2.Environment(loader=loader)
env.globals['include_file'] = include_file

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/searching')
def searching():
    return env.get_template('search.html').render()


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
