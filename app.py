import os
from flask import Flask
from flask import render_template
app = Flask(__name__)
app.debug = True

@app.route("/")
def index():
    return render_template('index.html')
    
@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/result")
def result():
    return render_template('result.html')
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
