"""
OpenBNF
"""
import difflib
import json
import os

from flask import Flask, request, redirect
from flask import render_template
import jinja2

app = Flask(__name__)
app.debug = True

bnf =  json.loads(
    open(os.path.join(
            os.path.dirname(__file__),
            'templates/bnf.json'
        ), 'r').read()
    )

def include_file(name):
    return jinja2.Markup(loader.get_source(env, name)[0])

loader = jinja2.PackageLoader(__name__, 'templates')
env = jinja2.Environment(loader=loader)
env.globals['include_file'] = include_file

"""
Search
"""

def drugs_like_me(term):
    """
    Return a list of Drugs that are like our search term.
    (For some value of like)
    """
    results = []
    if term.find('|') != -1:
        frist, rest= term.split('|')
        results = drugs_like_me(frist)
        results += drugs_like_me(rest)
        return results

    for k in bnf:
        if k.lower().startswith(term.lower()):
            results.append(k)
    return results

"""
Views
"""
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search", methods = ['GET', 'POST'])
def search():
    drug = request.form['q']
    results = drugs_like_me(drug)

    if len(results) == 1 and results[0].lower() == drug.lower():
        return redirect('/result/{0}'.format(results[0]))
    suggestions = []
    if not results:
        suggestions = difflib.get_close_matches(drug.upper(), bnf.keys())
    return render_template('search.html', results=results, query=drug, suggestions=suggestions)

@app.route("/result/<drug>")
def result(drug):
    drug = bnf[drug]
    whitelist = ['doses', 'contra-indications', 'interactions', 'name']
    impairments = [k for k in drug if k.find('impairment')!= -1]
    whitelist += impairments
    return render_template('result.html', drug=drug, whitelist=whitelist, impairments=impairments)

@app.route('/jstesting')
def jstesting():
    return env.get_template('jstest.html').render()

@app.route('/ajaxsearch', methods = ['GET'])
def ajaxsearch():
    term = request.args.get('term')
    return json.dumps(drugs_like_me(term)[:10])

@app.route('/api/')
def api_side_effects():
    term = request.args.get('drug')
    names = drugs_like_me(term)
    results = [bnf[n] for n in names]
    if 'callback' in request.args.get:
        return '{0}({1})'.format(request.args.get('callback'), json.dumps(results))
    else:
        return json.dumps(results)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


