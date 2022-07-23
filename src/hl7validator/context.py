import typing

import attrs
import hl7


@attrs.define(auto_attribs=True)
class LogMessage:
    msg: str
    rule: typing.Any
    is_error: bool = False


@attrs.define(auto_attribs=True)
class Context:
    """
    Container for keeping data related to the validation process.

    This will be returned from validation. You should check .is_valid for validation result.
    """

    # payload to validate
    message: hl7.Message
    # list of validation messages (not all may be errors)
    log: typing.List[LogMessage] = attrs.field(factory=list)

    def add_msg(self, log_msg: LogMessage) -> "Context":
        self.log.append(log_msg)
        return self

    def add_error(self, log_msg: str):
        msg = LogMessage(log_msg, True)
        return self.add_msg(msg)

    @property
    def is_valid(self) -> bool:
        return not bool(self.get_errors())

    def get_errors(self):
        return [l for l in self.log if l.is_error]