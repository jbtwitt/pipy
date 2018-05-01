import json
import os
from datetime import datetime

JsonFile = "{}/{}.meta.json"
class HqMetaFile:

    def __init__(self, hqConf):
        repo = hqConf["repo"]
        self.metaFile = JsonFile.format(repo, datetime.now().strftime("%Y%m%d"))
        # print(self.metaFile)

    def write(self, hqMeta):
        with open(self.metaFile, 'w') as outfile:
            json.dump(hqMeta, outfile)

    def read(self):
        hqMetas = json.load(open(self.metaFile))
        for hqMeta in hqMetas:
            print(hqMeta)
        return hqMetas
