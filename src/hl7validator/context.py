import typing
import hl7
import attrs


@attrs.define(auto_attribs=True)
class LogMessage:
    msg: str
    rule: typing.Any
    is_error: bool = False


@attrs.define(auto_attribs=True)
class Context:
    message: hl7.Message
    log: typing.List[LogMessage] = attrs.field(factory=list)
    is_valid: bool = True

    def add_msg(self, log_msg: LogMessage) -> 'Context':
        self.log.append(log_msg)
        if log_msg.is_error:
            self.is_valid = False
            print(log_msg)
        return self

    def add_error(self, log_msg: str):
        msg = LogMessage(log_msg, True)
        return self.add_msg(msg)
