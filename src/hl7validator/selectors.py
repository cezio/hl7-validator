import re
import typing

import hl7


class BaseSelector:
    sel: str
    sel_regex: typing.ClassVar[re.Pattern]

    def __init__(self, sel):
        assert self.__class__.validate_selector(sel)
        self.sel = sel

    @classmethod
    def validate_selector(cls, val) -> bool:
        return cls.sel_regex.match(val)

    def get_value(self, context: hl7.Component):
        sel = context[self.sel]
        return sel

    def __str__(self):
        return f'<{self.__class__.__name__} sel={self.sel}>'

    def __repr__(self):
        return f'{self.__class__.__name__}(sel={self.sel})'


class SegmentSelector(BaseSelector):
    # ABC only
    sel_regex = re.compile(r'^[A-Z]{3}')


class FieldSelector(BaseSelector):
    # ABC.1, ABC.1.1, ABC.1.2.3
    sel_regex = re.compile(r'^[A-Z]{3}\.[0-9]+(\.[0-9]+)*?')


__all__ = ['FieldSelector', 'SegmentSelector']
