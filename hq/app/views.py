import json
import math
from flask import render_template, request
import glob
import urllib

from app import app

hqConf = json.load(open('hqrobot.json'))
print(hqConf)

@app.route('/')
def index():
    hqMetaFiles = glob.glob(hqConf['repo'] + '/hqMeta*.json')
    listFiles = hqMetaFiles[len(hqMetaFiles)-3:]
    hqMetaFiles = []
    for hqMetaFile in listFiles:
        hqMetaFiles.append(urllib.parse.urlencode({'hqMetaFile': hqMetaFile}))

    return render_template('index.html',
                           title='HQ',
                           hqUrl=hqConf['hqUrl'],
                           hqMetaFiles=hqMetaFiles,
                           tickers=hqConf['tickers'])

@app.route('/hqMeta')
def hqMeta():
    hqMetaFile = request.args.get('hqMetaFile')
    hqMetas = json.load(open(hqMetaFile))
    return render_template('hqMeta.html',
                           title='HQ',
                           hqUrl=hqConf['hqUrl'],
                           hqMetas=hqMetas,
                           downAlert=-0.1,
                           round=round)
