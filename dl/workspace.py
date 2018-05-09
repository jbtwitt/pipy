"""
Workspace structure

garage/
garage/apply
garage/apply/close
garage/apply/open
garage/learn
garage/learn/close
garage/learn/open
garage/savedModels
"""
import os

# root repository
Pirepo = "/pirepo/"

class Workspace:
    def __init__(self, name, labels):
        self.rootPath = Pirepo + name
        if not os.path.exists(self.rootPath):
            os.makedirs(self.rootPath)
        self.labels = labels
        self.json = os.path.join(self.rootPath, name + ".json")

    def getRootPath(self):
        return self.rootPath

    def getJson(self):
        return self.json

    def modelStore(self, modelName):
        folder = self.rootPath + '/savedModels/' + modelName
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder + '/' + modelName + '_model'

    def modelMeta(self, modelName):
        folder = self.rootPath + '/savedModels/' + modelName
        return folder + '/' + modelName + '_model.meta'

    def applyStore(self):
        folder = self.rootPath + '/apply/'
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def learnStore(self):
        folder = self.rootPath + '/learn/'
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def initLabelStores(self):
        applyFolder = self.applyStore()
        learnFolder = self.learnStore()
        for label in self.labels:
            folder = applyFolder + label
            if not os.path.exists(folder):
                os.makedirs(folder)
            folder = learnFolder + label
            if not os.path.exists(folder):
                os.makedirs(folder)

    def getLabels(self):
        return self.labels
            
if __name__ == "__main__":
    labels = ['car-brother', 'car-vivian', 'empty', 'others']
    ws = Workspace('nono-parking-lot', labels)
    print(ws.modelStore('mnst'))
