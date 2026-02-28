
class PicaAPIError(RuntimeError):
    def __init__(self, err: str, message: str):
        self.err = err
        self.message = message
    
    def __str__(self):
        return f'{self.err}: {self.message}'
