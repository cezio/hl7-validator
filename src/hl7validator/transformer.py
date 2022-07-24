import logging
import pkgutil
import typing
from urllib.parse import urlparse

import lark

from .exceptions import RuleImportError
from .parser import FILE_LOCATION, PACKAGE_LOCATION, create_parser
from .predicates import CannotBe, MayBe, MustBe
from .rules import FieldValidationRule, SegmentValidationRule
from .selectors import Cardinality, FieldSelector, SegmentSelector
from .values import (
    AnyValue,
    ConstValue,
    IntValue,
    OneOfValues,
    RegexpValue,
    StringValue,
    )

log = logging.getLogger(__name__)


def get_type_for_check_type(value: str):

    if value == "int":
        value_converter = IntValue()
    elif value == "string":
        value_converter = StringValue()
    elif value == "any":
        value_converter = AnyValue()
    else:
        raise ValueError(f"Invalid type: {value}")
    return value_converter


@lark.v_args(inline=True)
class HL7Transformer(lark.Transformer):
    """
    Tree transformer for validation rules
    """

    def __init__(self):
        self._rules = []
        self._structure = []
        self._imports = []

    # field validation handlers
    def selector_field(self, value: lark.Token):
        return FieldSelector(value.value)

    def selector_segment(self, value: lark.Token):
        return SegmentSelector(value.value)

    def must_be_value(self, value: typing.Union[lark.Token, lark.Tree]):

        if isinstance(value, lark.Tree) and value.data == "regexp":
            return MustBe(RegexpValue("".join([v.value for v in value.children])))
        elif value.value.startswith('r"') and value.value.endswith('"'):
            val = value.value[2:][:-1]
            return MustBe(RegexpValue(val))
        return MustBe(ConstValue(value.value))

    def must_be_one_of(self, values: lark.Tree):
        return MustBe(OneOfValues(*[v for v in values.children]))

    def must_be_type(self, value: lark.Token):
        value_converter = get_type_for_check_type(value.value)
        return MustBe(value_converter)

    def may_be_value(self, value: lark.Token):
        return MayBe(ConstValue(value.value))

    def may_be_one_of(self, values: lark.Tree):
        return MayBe(OneOfValues(*[v for v in values.children]))

    def may_be_type(self, value: lark.Token):
        value_converter = get_type_for_check_type(value.value)
        return MayBe(value_converter)

    def cannot_be_value(self, value: lark.Token):
        return CannotBe(ConstValue(value.value))

    def cannot_be_one_of(self, values: lark.Tree):
        return CannotBe(OneOfValues(*[v for v in values.children]))

    def cannot_be_type(self, value: lark.Token):
        value_converter = get_type_for_check_type(value.value)
        return CannotBe(value_converter)

    def must_be_not_empty(self):
        return MustBe(AnyValue())

    def must_be_empty(self):
        return CannotBe(AnyValue())

    def test_is_value(self, value: lark.Token):
        return MustBe(ConstValue(value.value))

    def test_is_empty(self):
        return CannotBe(AnyValue())

    def test_is_not_empty(self):
        return MustBe(AnyValue())

    def test_list_of_values(self, values: lark.Tree):
        return MayBe(OneOfValues(*[v.value.strip('"') for v in values.children]))

    def test_is_type(self, value: lark.Token):
        value_converter = get_type_for_check_type(value.value)
        return MustBe(value_converter)

    def _create_rule(self, selector, predicate, test_rule=None):
        rule = FieldValidationRule(
            selector=selector, predicate=predicate, test_rule=test_rule
        )
        return rule

    def create_rule(self, base_rule: lark.Tree, *args):
        # check rule in children
        if isinstance(base_rule.children[0], lark.Tree):
            _test_rule = self._create_rule(*(base_rule.children[1].children))
            selector, predicate = base_rule.children[0].children
        else:
            _test_rule = None
            selector, predicate = base_rule.children
        rule = self._create_rule(selector, predicate, _test_rule)
        self._rules.append(rule)
        return rule

    def create_check_rule(self, selector, predicate, *args, **kwargs):

        rule = self._create_rule(selector, predicate)
        return rule

    def optional_segment(self, segment: SegmentSelector):
        segment.cardinality = Cardinality.SEGMENT_AT_MOST_ONE
        return segment

    def structure_segment(
        self,
        level: str,
        segment: SegmentSelector,
        card_token: lark.Token = None,
        *args,
        **kwargs,
    ):
        last: typing.Optional[SegmentSelector] = None
        try:
            last = self._structure[-1]
        except IndexError:
            pass
        segment.level = len(level)
        if card_token:
            card = Cardinality(card_token.children[0].value)
            segment.cardinality = card

        if last:
            p = last
            while p and p.level >= segment.level:
                p = p.parent
            if p:
                segment.set_parent(p)
        self._structure.append(segment)
        return segment

    def import_rule(self, rule_token: lark.Token, *args, **kwargs):
        source = _read_source(rule_token.value.strip('"'))
        log.info(f"importing {source}")
        t = make_transformer(source)
        self._rules.extend(t.get_rules())
        self._structure.extend(t._structure)
        log.info(
            f"imported {len(t.get_rules())} rules, {len(t.get_structure())} from {source}"
        )

    # structure handlers
    def get_rules(self) -> typing.List[FieldValidationRule]:
        return self._rules

    def get_structure(self) -> typing.List[SegmentValidationRule]:
        # roots only
        return [SegmentValidationRule(p) for p in self._structure if p.parent is None]

    def get_imports(self) -> typing.List[str]:
        return self._imports


def _read_source(source_loc: str) -> str:
    url = urlparse(source_loc)
    if url.scheme == FILE_LOCATION:
        with open(url.path, "rt") as f:
            data = f.read()
    elif url.scheme == PACKAGE_LOCATION:
        pkg_name = url.hostname
        pkg_res = url.path
        data = pkgutil.get_data(pkg_name, pkg_res).decode("utf-8")
    else:
        raise RuleImportError(source_loc)
    return data


def make_transformer(rules: str, grammar: str = None) -> "HL7Transformer":
    transformer = HL7Transformer()
    parser = create_parser(grammar)
    tree = parser.parse(rules)
    transformer.transform(tree)
    return transformer
