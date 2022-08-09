import typing
from copy import copy

import hl7

from .context import LogMessage
from .exceptions import NotValid
from .mixins import Cardinality, ContextMixin, ValidateMixin

if typing.TYPE_CHECKING:
    from .predicates import BasePredicate
    from .selectors import BaseSelector, SegmentSelector


class FieldValidationRule(ContextMixin, ValidateMixin):
    """
    Validation rule validates one specific check on the message
    """

    selector: "BaseSelector"
    predicate: "BasePredicate"
    test_rule: "BaseRule"

    def __init__(
        self,
        selector: "BaseSelector",
        predicate: "BasePredicate",
        test_rule: "BaseRule" = None,
    ):
        self.selector = selector
        self.predicate = predicate
        self.test_rule = test_rule
        self.context = None

    def validate(self):
        self.predicate.set_context(self.context)
        if self.test_rule:
            self.test_rule.set_context(self.context)
            self.test_rule.validate()
        try:
            ret = self.predicate.validate(self.selector)
            self.context.add_msg(
                LogMessage(msg=f"Rule {self}: ok", rule=self, selector=self.selector)
            )
            return ret
        except NotValid as err:
            self.context.add_msg(
                LogMessage(
                    msg=f"validation error for {err.selector} value {err.value}",
                    rule=self,
                    selector=err.selector,
                    is_error=True,
                )
            )
        # except Exception as err:
        #     self.context.add_msg(
        #         LogMessage(msg=f"internal error {err}", rule=self, is_error=True)
        #     )

    def __str__(self):
        extra = []
        if self.test_rule:
            extra.append(f" test rule: {str(self.test_rule)}")
        return f"<{self.__class__.__name__}: {self.selector} {self.predicate} {', '.join(extra)}>"


def _get_segments(message: hl7.Message, sel: str) -> typing.List[hl7.Segment]:
    segments = [
        (
            idx,
            seg,
        )
        for idx, seg in enumerate(message)
        if seg[0][0] == sel
    ]
    return segments


def _validate_segment(selector: "SegmentSelector", message: hl7.Message):
    cd = selector.cardinality
    sel = selector.sel
    segments = _get_segments(message, sel)

    sel_len = len(segments)
    if cd == Cardinality.SEGMENT_NONE and sel_len > 0:
        raise NotValid(
            selector=selector, rule=None, value=selector.sel, msg=f"not expected {sel}"
        )
    elif cd == Cardinality.SEGMENT_ONE and sel_len < 1:
        raise NotValid(
            selector=selector, rule=None, value=selector.sel, msg=f"not enough {sel}"
        )
    elif cd == Cardinality.SEGMENT_ONE and sel_len > 1:
        raise NotValid(
            selector=selector, rule=None, value=selector.sel, msg=f"too much {sel}"
        )
    elif cd == Cardinality.SEGMENT_AT_MOST_ONE and sel_len > 1:
        raise NotValid(
            selector=selector, rule=None, value=selector.sel, msg=f"too much {sel}"
        )
    elif cd == Cardinality.SEGMENT_AT_LEAST_ONE and sel_len < 1:
        raise NotValid(
            selector=selector, rule=None, value=selector.sel, msg=f"not enough {sel}"
        )

def _cut_message_to_selector(
    current_selector: "SegmentSelector",
    current_message: hl7.Message,
    next_selector: "SegmentSelector",
):
    out = []
    current_msg = []
    segidx = 0
    # set only when we hit first selector occurence
    has_match = False

    for segidx, seg in enumerate(current_message):
        seg_name = seg[0][0]
        if seg_name == current_selector.sel:
            has_match = True
        if not has_match:
            continue
        if current_msg and seg_name == current_selector.sel:
            out.append(current_msg)
            current_msg = [seg]
        # rest of the message
        elif (current_msg or out) and (
            next_selector and seg_name == next_selector.sel
        ):
            out.append(current_msg)
            current_msg = []
            break
        else:
            current_msg.append(seg)

    if current_msg:
        out.append(current_msg)
    rest = current_message[segidx:]
    return out, rest


class SegmentValidationRule(ContextMixin, ValidateMixin):
    selector: "SegmentSelector"

    def __str__(self):
        return f"<{self.__class__.__name__}: (selector={self.selector})>"

    __repr__ = __str__

    def __init__(self, selector: "SegmentSelector"):
        self.selector = selector

    def _validate(self):
        msg = self.context.message
        # for self, we should check if current selector exists in one instance
        self_sel = copy(self.selector)
        _validate_segment(self_sel, msg)

        # validate children cardinality
        for c in self.selector.children:
            try:
                _validate_segment(c, msg)
            except NotValid as err:
                err.rule = self
                raise err

        current_message = msg[1:]
        for cidx, c in enumerate(self.selector.children):
            try:
                nextc = self.selector.children[cidx + 1]
            except IndexError:
                nextc = None
            msg_chunks, current_message = _cut_message_to_selector(
                c, current_message, nextc
            )
            for msg_chunk in msg_chunks:
                subctx = copy(self.context)
                subctx.message = msg_chunk
                subv = SegmentValidationRule(c)
                subv.set_context(subctx).validate()

    def validate(self, *args, **kwargs) -> typing.Any:
        try:
            self._validate()
            self.context.add_msg(
                    LogMessage(
                            msg=f"validation {self} -> ok",
                            rule=self,
                            selector=self.selector,
                            is_error=False,
                            )
                    )
        except NotValid as err:
            self.context.add_msg(
                LogMessage(
                    msg=f"validation error for {err.selector} value {err.value}: {err.msg}",
                    rule=self,
                    selector=err.selector,
                    is_error=True,
                )
            )
        # except Exception as err:
        #     self.context.add_msg(
        #             LogMessage(msg=f"internal error {err}", rule=self, is_error=True)
        #             )
