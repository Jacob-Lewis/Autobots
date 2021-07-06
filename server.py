from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def hello():
    return '<h2>hello</h2>'

def run():
  #app.run(host='127.0.0.1',port=5000)
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
