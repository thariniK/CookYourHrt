from http import HTTPStatus

class BaseException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.code = args[1]
        else:
            self.message = None
            self.code = 404

    def __str__(self):
        if self.message and self.code:
            return 'Exception - {0} - [{1}]'.format(self.code, self.message)
        elif self.message:
            return 'Exception, {0}'.format(self.message)
        else:
            return 'Exception has been raised'

class URLNotPresent(BaseException):
    """Please provide an URL"""
    def __init__(self, *args):
        super().__init__("Please provide an URL", HTTPStatus.BAD_REQUEST)

class InvalidURL(BaseException):
    """Please provide a correct URL"""
    def __init__(self, *args):
        super().__init__("Please provide a correct URL", HTTPStatus.BAD_REQUEST)

class URLGivesNotFound(BaseException):
    """The URL provided seems to be incorrect, please try again"""
    def __init__(self, *args):
        super().__init__("The URL provided seems to be incorrect, please try again", HTTPStatus.BAD_REQUEST)

class ContentNotFound(BaseException):
    """The URL provided seems to be incorrect, please try again"""
    def __init__(self, *args):
        super().__init__("The URL provided seems to be incorrect, please try again", HTTPStatus.BAD_REQUEST)

class NoSchemaResultSet(BaseException):
    """The recipe you're looking for is not found"""
    def __init__(self, *args):
        super().__init__("The recipe you're looking for is not found", HTTPStatus.NOT_FOUND)

class NoRefinedResult(BaseException):
    """Failed to get recipe, please try again later"""
    def __init__(self, *args):
        super().__init__("Failed to get recipe, please try again later", HTTPStatus.NOT_FOUND)