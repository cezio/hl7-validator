import re
import typing

import hl7

from .mixins import Cardinality


class BaseSelector:
    sel: str
    sel_regex: typing.ClassVar[re.Pattern]

    def __init__(self, sel):
        self.sel = sel
        assert self.__class__.validate_selector(sel)


    @classmethod
    def validate_selector(cls, val) -> bool:
        return cls.sel_regex.match(val)

    def get_value(self, msg: hl7.Component):
        sel = msg[self.sel]
        return sel

    def __str__(self):
        return f"<{self.__class__.__name__} sel={self.sel}>"

    def __repr__(self):
        return f"{self.__class__.__name__}(sel={self.sel})"


class SegmentSelector(BaseSelector):
    # ABC only
    sel_regex = re.compile(r"([A-Z]{2}[A-Z0-9]{1})")
    cardinality: Cardinality
    parent: "typing.Optional[SegmentSelector]"
    level: int
    children: list

    def __init__(
        self,
        sel,
        cardinality: Cardinality = None,
        parent: "SegmentSelector" = None,
        level: int = None,
    ):
        super().__init__(sel)
        self.level = level
        self.cardinality = cardinality or Cardinality.SEGMENT_ONE
        self.children = []
        self.set_parent(parent)

    def set_parent(self, parent: "SegmentSelector"):

        self.parent = parent
        if parent:
            parent.children.append(self)

    def __str__(self):
        return (
            f"<{self.__class__.__name__} sel={self.sel} cardinality={self.cardinality}>"
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(sel={self.sel} cardinality={self.cardinality})"
        )


class FieldSelector(BaseSelector):
    # ABC.1, ABC.1.1, ABC.1.2.3
    sel_regex = re.compile(r"^[A-Z]{2}[A-Z0-9]{1}\.[0-9]+(\.[0-9]+)*?")


__all__ = ["FieldSelector", "SegmentSelector"]
