import typing

from .exceptions import NotValid
from .context import Context, LogMessage

if typing.TYPE_CHECKING:
    from .predicates import BasePredicate
    from .selectors import BaseSelector


class ValidationRule:
    """
    Validation rule validates one specific check on the message
    """

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

    def set_context(self, context: "Context"):
        self.context = context
        return self

    def validate(self):
        self.predicate.set_context(self.context)
        if self.test_rule:
            self.test_rule.set_context(self.context)
            self.test_rule.validate()
        try:
            ret = self.predicate.validate(self.selector)
            self.context.add_msg(LogMessage(msg=f"Rule {self}: ok", rule=self))
            return ret
        except NotValid as err:
            self.context.add_msg(
                LogMessage(
                    msg=f"validation error for {err.selector} value {err.value}",
                    rule=self,
                    is_error=True,
                )
            )
        except Exception as err:
            self.context.add_msg(
                LogMessage(msg=f"internal error {err}", rule=self, is_error=True)
            )

    def __str__(self):
        extra = []
        if self.test_rule:
            extra.append(f" test rule: {str(self.test_rule)}")
        return f"<{self.__class__.__name__}: {self.selector} {self.predicate} {', '.join(extra)}>"
