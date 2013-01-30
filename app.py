"""
OpenBNF
"""
import difflib
import json
import os
import re

from flask import Flask, request, redirect, Response, make_response
from flask import render_template
import jinja2
from jinja2 import evalcontextfilter, Markup, escape

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
Filters - Turn Newlines into<br> please
Kudos http://flask.pocoo.org/snippets/28/
"""
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def json_template(tplname, **context):
    return Response(
        render_template(tplname,**context),
        mimetype='application/json'
        )

"""
Search
"""

def drugs_like_me(term):
    """
    Return a list of Drugs that are like our search term.
    (For some value of like)
    """
    results = []
    splitter = None
    for splittee in ['|', ' OR ']:
        if term.find(splittee) != -1:
            splitter = splittee
            break

    if splitter:
        frist, rest = term.split(splitter, 1)
        results = drugs_like_me(frist)
        results += drugs_like_me(rest)
        return results

    for k in bnf:
        # We only want dicts that have a name key, otherwise likely to
        # just be a list of indications (which we may later render another
        # way)
        if k.lower().startswith(term.lower()) and 'name' in bnf[k]:
            results.append(k)
    return results

"""
Views
"""
@app.route("/")
def index():
    drug_names = bnf.keys()
    drug_names.sort()
    return render_template('index.html', drugs=drug_names)

@app.route("/about")
def about():
    return render_template('about.html')

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
    whitelist = ['doses', 'contra-indications', 'interactions', 'name', 'breadcrumbs', 'fname']
    impairments = [k for k in drug if k.find('impairment')!= -1]
    whitelist += impairments
    return render_template('result.html', drug=drug, whitelist=whitelist, impairments=impairments)

@app.route('/jstesting')
def jstesting():
    return env.get_template('jstest.html').render()

@app.route('/ajaxsearch', methods = ['GET'])
def ajaxsearch():
    term = request.args.get('term')
    term = term.replace('+',  ' ')
    responses = drugs_like_me(term)[:10]
    return json.dumps(responses)

@app.route('/api/')
def api_side_effects():
    term = request.args.get('drug')
    names = drugs_like_me(term)
    results = [bnf[n] for n in names]
    if  request.args.get('callback', None):
        return '{0}({1})'.format(request.args.get('callback'), json.dumps(results))
    else:
        return Response(json.dumps(results), mimetype='text/json')

@app.route('/api/v2/openbnf')
def apidoc_endpoint():
    return json_template('api/base.json.js', host=request.host)

@app.route('/api/v2/openbnf/drug')
def apidoc_drug_endpoint():
    return json_template('api/drug.json.js', host=request.host)

@app.route('/api/v2/doc')
def apidoc():
    return env.get_template('apidoc.html').render()

@app.route('/api/v2/drug')
def api_v2_drug():
    term = request.args.get('name')
    names = drugs_like_me(term)
    results = [bnf[n] for n in names]
    if  request.args.get('callback', None):
        return '{0}({1})'.format(request.args.get('callback'), json.dumps(results))
    else:
        return Response(json.dumps(results), mimetype='text/json')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
