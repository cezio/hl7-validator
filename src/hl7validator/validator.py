import typing

import hl7
import lark

from .context import Context
from .parser import create_parser
from .predicates import BasePredicate
from .transformer import HL7Transformer
from .mixins import ValidateMixin, ContextMixin


class Validator(ContextMixin, ValidateMixin):
    """
    Validator class wraps whole grammar parser->rules parsing->payload validation process

    Validator creation requires rules to parse. Ruleset describes a specific HL7 message profile. Later on, a message
     will be checked if it complies with those rules.

    """

    def __init__(self, rules: str, grammar: str = None):
        """
        Initializes the instance.
        :param rules: Rules is a string with message rules
        :param grammar: optional grammar data (default will be used)
        """
        self.rules = rules
        self.grammar = grammar
        self._rules: lark.Tree = None
        self.transformer: HL7Transformer = None
        self.context = None

    def get_parser(self, grammar: str = None) -> lark.Lark:
        """
        Creates a parser for this instance
        :param grammar:
        :return:
        """
        p = create_parser(grammar)
        return p

    def _get_parser_tree(
        self, rules: str = None, grammar: str = None
    ) -> typing.List[BasePredicate]:
        """
        Creates parser tree for rules
        :param rules:
        :param grammar:
        :return:
        """

        parser = self.get_parser(grammar)
        return parser.parse(rules)

    def validate(self, msg: typing.Union[str, bytes, hl7.Message] = None) -> Context:
        """
        Validates a specific message if it matches a given profile

        Returns Context object with validation result

        :param msg:
        :return:
        """
        if not isinstance(msg, hl7.Message):
            msg = hl7.parse(msg)
        ctx = self.context or Context(message=msg)

        if not ctx.message:
            raise ValueError('empty message')
        self.set_context(ctx)

        self.transformer = transformer = HL7Transformer()
        if not isinstance(msg, hl7.Message):
            msg = hl7.parse(msg)
        tree = self._get_parser_tree(rules=self.rules, grammar=self.grammar)
        transformer.transform(tree)
        imports = transformer.get_imports()
        rules = transformer.get_rules()
        struct = transformer.get_structure()
        # first: check structure
        for seg in struct:
            seg.set_context(ctx).validate()
        # then check specific fields
        for rule in rules:
            rule.set_context(ctx).validate()
        return ctx
