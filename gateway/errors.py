from http import HTTPStatus

class ApiError(Exception):
    code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, description="Lo sentimos! ha ocurrido un error, intentelo nuevamente"):
        self.description = description

class Unauthorized(ApiError):
    code = HTTPStatus.UNAUTHORIZED

class Forbidden(ApiError):
    code = HTTPStatus.FORBIDDEN