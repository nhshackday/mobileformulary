
import json
import os
from flask import Flask, request
from flask import render_template
app = Flask(__name__)
app.debug = True

bnf =  json.loads(
    open(os.path.join(
            os.path.dirname(__file__),
            'templates/bnf.json'
        ), 'r').read()
    )

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

@app.route("/search", methods = ['GET', 'POST'])
def search():
    drug = request.form['q']
    results = []
    for k in bnf:
        if k.lower().startswith(drug.lower()):
            results.append(k)
    return render_template('search.html', results = results)

@app.route("/result")
def result():
    return render_template('result.html')

@app.route('/jstesting')
def jstesting():
    return env.get_template('jstest.html').render()

@app.route('/ajaxsearch', methods = ['GET'])
def ajaxsearch():
    pass

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


