import os
from .workspace import Workspace

class TrainStore:
    def __init__(self, workspace, trainType):
        self.workspace = workspace
        self.rootPath = self.workspace.getRootPath() + '/' + trainType
        if not os.path.exists(self.rootPath):
            os.makedirs(self.rootPath)

    def getRootPath(self):
        return self.rootPath

    def getLabels(self):
        return self.workspace.getLabels()

    def getLabelStore(self, idx):
        folder = self.rootPath + '/' + self.workspace.getLabels()[idx]
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

if __name__ == "__main__":
    labels = ['car-brother', 'car-vivian', 'empty', 'others']
    ws = Workspace('nono-parking-lot', labels)
    learnStore = TrainStore(ws, 'learn')
    print(learnStore.getLabelStore(0))
