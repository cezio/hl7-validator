from lark import lark

from hl7validator.parser import create_parser
from hl7validator.validator import HL7Transformer,Validator


def test_parser_creation():
    
    rules = """
 "MSH.3.1.1" must be string
 "MSH.9.1.1" must be "OML"
 "MSH.9.1.2" must be "O21"
 "MSH.3.1.1" must be not empty
 "MSH.3.1.1" must be not empty
 "MSH.3.1.1" may be "Lab system"
 "MSH.3.1.1" may be string
 "MSH.3.1.1" must be one of "Lab1", "Lab2", "Lab3"
 "MSH.3.1.1" cannot be one of "Test", "Value"
 "MSH.3.2" cannot be int
 "MSH.3.3" must be int
 "MSH.3.3" must be int if "MSH.4" is empty
 "MSH.3.3" must be "Test" if "MSH.4" is not empty
"""

    p = create_parser()
    assert isinstance(p, lark.Lark)
    t = p.parse(rules)
    tr = HL7Transformer()
    tr.transform(t)
    _rules = tr.get_rules()
    assert _rules
    # discard any empty line
    assert len(_rules) == len([r for r in rules.split('\n') if r.strip()])


def test_parser_validation():
    test_msg = r'MSH|^~\\&|SrcSystem||TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r"'
    rules = """
 "MSH.3.1" must be not empty
 "MSH.3.1" must be string
 "MSH.3.1" cannot be "AnySystem"
 "MSH.3.1" must be "SrcSystem"
 "MSH.3.1" must be one of "SrcSystem", "OtherSystem"
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)
    assert ctx.is_valid