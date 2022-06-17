import os
from click.testing import CliRunner
from lark import lark

from hl7validator.parser import create_parser
from hl7validator.validator import HL7Transformer,Validator
from hl7validator.cli import main


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


def test_parser_validation_ok():
    test_msg = r'MSH|^~\\&|SrcSystem||TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r"'
    rules = """
// this is a comment
// this value must not be empty
 "MSH.3.1" must be not empty
 // this value must be a proper string
 "MSH.3.1" must be string
 // cannot be that value
 "MSH.3.1" cannot be "AnySystem"
 // must be a specific string value
 "MSH.3.1" must be "SrcSystem"
 // list of allowed values
 "MSH.3.1" must be one of "SrcSystem", "OtherSystem"
 // this is a regexp
 "MSH.7.1" must match r"[0-9]{12}" if "MSH.7.1" is not empty
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)
    assert ctx.is_valid

def test_parser_validation_invalid():
    test_msg = r'MSH|^~\\&|Invalid||TargetSystem|LabName|2007052713||OML^O21|12345|P|2.4\r"'
    rules = """
// this is a comment
// this value must not be empty
 "MSH.3.1" must be not empty
 // this value must be a proper string
 "MSH.3.1" must be string
 // cannot be that value
 "MSH.3.1" cannot be "AnySystem"
 // must be a specific string value
 "MSH.3.1" must be "SrcSystem"
 // list of allowed values
 "MSH.3.1" must be one of "SrcSystem", "OtherSystem"
 // this is a regexp
 "MSH.7.1" must match r"[0-9]{12}" if "MSH.7.1" is not empty
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)
    assert len(ctx.log)
    # 3 rules broken: MSH.3.1 invalid value, MSH.3.1 value not in allowed set, MSH.7.1 invalid regexp
    assert len([l for l in ctx.log if l.is_error]) == 3
    assert ctx.is_valid is False


def test_parser_cli():
    this_dir = os.path.dirname(__file__)
    tmsg = os.path.join(this_dir, 'resources', 'test.message.hl7')
    trules = os.path.join(this_dir, 'resources', 'test.incorrect.rules')
    runner = CliRunner()
    out = runner.invoke(main, [trules, tmsg], standalone_mode=False)
    assert out.return_value == 1

def test_parser_cli():
    this_dir = os.path.dirname(__file__)
    tmsg = os.path.join(this_dir, 'resources', 'test.message.hl7')
    trules = os.path.join(this_dir, 'resources', 'test.correct.rules')
    runner = CliRunner()
    out = runner.invoke(main, [trules, tmsg], standalone_mode=False)
    assert out.return_value == 0
