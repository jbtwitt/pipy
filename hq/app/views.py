import json
import math
from flask import render_template

from app import app

hqConf = json.load(open('hqrobot.json'))
print(hqConf)

@app.route('/')
def index():
    return render_template('index.html',
                           title='HQ',
                           hqUrl=hqConf['hqUrl'],
                           tickers=hqConf['tickers'])

@app.route('/hqMeta')
def hqMeta():
    hqMetas = json.load(open('../../robotRepo/hqMeta20180504.json'))
    return render_template('hqMeta.html',
                           title='HQ',
                           hqUrl=hqConf['hqUrl'],
                           hqMetas=hqMetas,
                           convert2Percent=toPercent)

def toPercent(value):
    return round(100 * value, 2)