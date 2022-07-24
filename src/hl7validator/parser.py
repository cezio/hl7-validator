import pkgutil

import lark

DEFAULT_GRAMMAR = "resources/hl7validation.lark"
FILE_LOCATION = r"file"
PACKAGE_LOCATION = r"pkg"


def create_parser(grammar: str = None) -> lark.Lark:
    """
    Creates Lark parser with validation rules grammar
    :param grammar:
    :return:
    """
    data = pkgutil.get_data(__name__, grammar or DEFAULT_GRAMMAR).decode("utf-8")
    return lark.Lark(data)  # , parser='lalr')


def parse_rules(parser: lark.Lark, rules: str) -> lark.Tree:
    """
    Parses given rules

    :param parser:
    :param rules:
    :return:
    """
    return parser.parse(rules)
