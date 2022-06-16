import typing
import hl7
import lark
from .selectors import SegmentSelector, FieldSelector
from .values import StringValue, ConstValue, IntValue, OneOfValues, AnyValue
from .predicates import MustBe, MayBe, CannotBe
from .rules import ValidationRule

def get_type_for_check_type(value: str):

    if value == 'int':
        value_converter = IntValue()
    elif value == 'string':
        value_converter = StringValue()
    elif value == 'any':
        value_converter = AnyValue()
    else:
        raise ValueError(f"Invalid type: {value}")
    return value_converter


@lark.v_args(inline=True)
class HL7Transformer(lark.Transformer):
    """

predicate: "must be"  CHECK_VALUES              -> must_be_value // must be 'a', 'b', 1
           | "must be"  CHECK_TYPES             -> must_be_type // must be int, string
           | "may be" CHECK_TYPES               -> may_be_type
           | "may be" CHECK_VALUES              -> may_be_value
           | "may be one of" list_of_values     -> may_be_one_of
           | "must be one of" list_of_values     -> must_be_one_of
           | "cannot be one of" list_of_values     -> cannot_be_one_of
           | "cannot be"  CHECK_VALUES          -> cannot_be_value
           | "cannot be"  CHECK_TYPES           -> cannot_be_type
           | "must be not empty"                -> must_be_not_empty
           | "must be empty"                    -> must_be_empty

test: "is of value"  CHECK_VALUES               -> test_is_value
     | "is empty"                               -> test_is_empty
     | "is one of" list_of_values               -> test_list_of_values
     | "is not empty"                           -> test_is_not_empty
     | "is of type" CHECK_TYPES                 -> test_is_type

    """

    def __init__(self):
        self.rules = []

    def selector_field(self, value: lark.Token):
        return FieldSelector(value.value)

    def selector_segment(self, value: lark.Token):
        return SegmentSelector(value.value)

    def must_be_value(self, value: lark.Token):
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

    def _create_rule(self, tree, *args):
        values = tree.children
        test_rule = None
        if len(values) == 2:
            selector, predicate = values
        else:
            selector, predicate, test_rule = values

        rule = ValidationRule(selector=selector, predicate=predicate, test_rule=test_rule)
        return rule

    def create_rule(self, tree, *args):
        rule = self._create_rule(tree, *args)
        self.rules.append(rule)
        return rule

    def create_test_rule(self, tree, *args):
        rule = self._create_rule(tree, *args)
        return rule

    def get_rules(self) -> typing.List[ValidationRule]:
        return self.rules
