from copy import deepcopy
import pickle

import rpyc
from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    data = pickle.loads(get_sensei_data())

    return render_template('index.html', data=data)

# get files from chunk servers


def get_sensei():
    try:
        return rpyc.connect('localhost', 33333).root
    except ConnectionRefusedError:
        return None

def get_sensei_data():
    sensei = get_sensei()

    if not sensei:
        return "No connection"

    return sensei.metadata()


if __name__=="__main__":
    app.run(debug=True)