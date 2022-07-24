import typing

from .exceptions import NotValid
from .mixins import ContextMixin, ValidateMixin
from .selectors import BaseSelector
from .values import BaseValue


class BasePredicate(ContextMixin, ValidateMixin):
    expected: BaseValue

    def __init__(self, expected: BaseValue):
        self.expected = expected

    def validate(self, sel: BaseSelector) -> typing.Any:
        selected_value = sel.get_value(self.context.message)
        try:
            result = self.check_value(selected_value)
            return result
        except AssertionError:
            raise NotValid(self, sel, selected_value)

    def check_value(self, in_value):
        return self.expected.eval(in_value)

    def __str__(self):
        return f"<{self.__class__.__name__}(expected={self.expected})>"

    __repr__ = __str__


class MustBe(BasePredicate):
    pass


class MayBe(BasePredicate):
    def check_value(self, in_value):
        if in_value:
            return self.expected.eval(in_value)
        return in_value


class CannotBe(BasePredicate):
    def check_value(self, in_value):
        # We want to raise assertion error only if `in_value` matches the value in .expected.
        # this is a bit tricky, because when .expected will raise AssertionError, this should suppress the error
        # because the value is invalid on BaseValue level, so it's valid for us.
        try:
            if in_value and self.expected.eval(in_value):
                assert False, f"Value {in_value} cannot be {self.expected}"
            return in_value
        except AssertionError:
            return in_value
