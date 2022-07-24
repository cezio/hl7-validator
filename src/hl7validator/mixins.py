import typing
from enum import Enum

from .context import Context


class ContextMixin:
    context: Context

    def set_context(self, context: Context):
        self.context = context
        return self


class ValidateMixin:
    def validate(self, *args, **kwargs) -> typing.Any:
        raise NotImplemented()


class Cardinality(str, Enum):
    SEGMENT_NONE = "0"
    SEGMENT_ONE = "1"
    SEGMENT_AT_MOST_ONE = "0..1"
    SEGMENT_AT_LEAST_ONE = "1..n"
    SEGMENT_MANY = "0..n"
