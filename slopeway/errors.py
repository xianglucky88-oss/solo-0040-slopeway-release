class Problem(Exception):
    def __init__(self, status, code, message, **details):
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details

    def payload(self):
        return {'code': self.code, 'message': str(self), **self.details}


def bad(message, **details):
    return Problem(422, 'invalid_input', message, **details)


def missing(message):
    return Problem(404, 'not_found', message)


def conflict(message, **details):
    return Problem(409, 'conflict', message, **details)
