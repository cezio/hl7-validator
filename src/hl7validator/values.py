import re
import typing


class BaseValue:
    def eval(self, *args, **kwargs):
        raise NotImplemented()

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    __repr__ = __str__


class BaseConverter(BaseValue):
    converter: typing.ClassVar[typing.Callable]

    def __init__(self, *args):
        pass

    def eval(self, in_value: str) -> typing.Any:
        try:
            return self.converter(in_value)
        except (ValueError, TypeError):
            assert False, f"Invalid input {in_value} for {self.converter}"

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    __repr__ = __str__


class StringValue(BaseConverter):
    converter = str


class IntValue(BaseConverter):
    converter = int


class AnyValue(BaseConverter):
    converter = bool

    def eval(self, in_value: str) -> typing.Any:
        try:
            assert self.converter(in_value)
            return True
        except (ValueError, TypeError, AssertionError):
            assert False, f"Invalid input {in_value} for {self.converter}"


class RegexpValue(BaseValue):
    def __init__(self, re_value: str):
        self._re = re_value
        self.re = re.compile(self._re)

    def eval(self, in_value: str) -> typing.Any:
        assert self.re.match(in_value)
        return in_value

    def __str__(self):
        return f"<{self.__class__.__name__}({self._re})>"

    __repr__ = __str__


class ConstValue(BaseValue):
    def __init__(self, const: str):
        self.const = const.strip('"')

    def eval(self, in_value: str) -> typing.Any:
        assert in_value == self.const
        return in_value

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.const}>"

    __repr__ = __str__


class OneOfValues(BaseValue):
    def __init__(self, *values):
        self.values = [v.strip('"') for v in values]

    def eval(self, in_value: str) -> typing.Any:
        assert in_value in self.values
        return in_value

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.values}>"

    __repr__ = __str__


__all__ = [
    "AnyValue",
    "IntValue",
    "StringValue",
    "ConstValue",
    "OneOfValues",
    "RegexpValue",
]
