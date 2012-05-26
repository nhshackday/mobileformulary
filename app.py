
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


def drugs_like_me(term):
    """
    Return a list of Drugs that are like our search term.
    (For some value of like)
    """
    results = []
    for k in bnf:
        if k.lower().startswith(term.lower()):
            results.append(k)
    return results

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search", methods = ['GET', 'POST'])
def search():
    drug = request.form['q']
    results = drugs_like_me(drug)
    return render_template('search.html', results = results)

@app.route("/result/<drug>")
def result(drug):
    drug = bnf[drug]
    whitelist = ['doses', 'contra-indications', 'interactions', 'name']
    impairments = [k for k in drug if k.find('impairments')!= -1]
    whitelist += impairments

    return render_template('result.html', drug=drug, whitelist=whitelist, impairments=impairments)

@app.route('/jstesting')
def jstesting():
    return env.get_template('jstest.html').render()


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


