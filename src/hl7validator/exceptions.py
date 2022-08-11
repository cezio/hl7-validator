import hl7

class BaseValidatorError(Exception):
    pass


class NotValid(BaseException):
    def __init__(self, rule, selector, value, msg=None):
        self.rule = rule
        self.selector = selector
        self.value = value
        self.msg = msg

    def __str__(self):
        return f"<NotValid(rule={self.rule}, selector={self.selector}, value={self.value} {self.msg or ''})>"


class RuleImportError(BaseValidatorError):
    pass

class MessageMalformedError(BaseValidatorError):
    def __init__(self, selector: str, message: hl7.Message, original_error: Exception):
        self.selector = selector
        self.message = message
        self.original_error = original_error

    def __str__(self):
        return f"<MessageMalformed={self.selector}, error={self.original_error}>"