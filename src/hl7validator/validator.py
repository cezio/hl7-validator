import typing

import hl7
import lark

from .parser import create_parser
from .predicates import BasePredicate
from .transformer import HL7Transformer
from .context import Context, LogMessage



class Validator:
    def __init__(self, rules: str, grammar: str=None):
        self.rules = rules
        self.grammar = grammar
        self._rules: lark.Tree = None
        self.transformer: HL7Transformer = None

    def get_parser(self, grammar: str = None) -> lark.Lark:
        p = create_parser(grammar)
        return p

    def get_rules(self, rules: str = None, grammar: str = None) -> typing.List[BasePredicate]:

        parser = self.get_parser(grammar)
        return parser.parse(rules)

    def validate(self, msg: typing.Union[str, bytes, hl7.Message]):
        self.transformer = transformer = HL7Transformer()
        if not isinstance(msg, hl7.Message):
            msg = hl7.parse(msg)
        self._rules = self.get_rules(rules=self.rules, grammar=self.grammar)
        transformer.transform(self._rules)
        rules = transformer.get_rules()
        ctx = Context(message=msg)
        for rule in rules:
            rule.set_context(ctx).validate()
        return ctx

