class ConfigError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class FifoRequestNotFound(Exception):
    msg = "Required request not found in FIFO"
    def __str__(self):
        return FifoRequestNotFound.msg
