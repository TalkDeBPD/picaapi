class PicaAPIError(RuntimeError):
    '''
    用于返回PicaAPI错误信息与错误码
    '''
    def __init__(self, err: str, message: str):
        self.err = err
        self.message = message
    
    def __str__(self):
        return f'{self.err}: {self.message}'
