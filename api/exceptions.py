from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework import status


class GEEValidationError(APIException):
    """Raise custom validation errors for GEE.

    Parameters
    ----------
    detail: str
        Detail of the error
    field: str
        The field that the error is related to
    status_code: int
        HTTP status code for the error

    """

    def __init__(
        self,
        field,
        detail='The process cannot be executed.',
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    ):
        self.status_code = status_code
        self.detail = {field: force_text(detail)}
