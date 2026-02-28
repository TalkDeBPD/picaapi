class Picture:
    def __init__(self, info: dict):
        self.fileServer = info['fileServer']
        self.originalName = info['originalName']
        self.path = info['path']
    
    @property
    def url(self):
        return self.fileServer + '/' + self.path
