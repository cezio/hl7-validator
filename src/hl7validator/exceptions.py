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
