import os

from click.testing import CliRunner
from lark import lark

from hl7validator.cli import main
from hl7validator.mixins import Cardinality
from hl7validator.parser import create_parser
from hl7validator.predicates import MustBe
from hl7validator.transformer import HL7Transformer
from hl7validator.validator import Validator
from hl7validator.values import AnyValue

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
    assert len(_rules) == len([r for r in rules.split("\n") if r.strip()])


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
    test_msg = (
        r'MSH|^~\\&|Invalid||TargetSystem|LabName|2007052713||OML^O21|12345|P|2.4\r"'
    )
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


def test_parser_cli_error():
    this_dir = os.path.dirname(__file__)
    tmsg = os.path.join(this_dir, "resources", "test.message.hl7")
    trules = os.path.join(this_dir, "resources", "test.incorrect.rules")
    runner = CliRunner()
    out = runner.invoke(main, [trules, tmsg])
    assert out.exit_code == 1


def test_parser_cli_ok():
    this_dir = os.path.dirname(__file__)
    tmsg = os.path.join(this_dir, "resources", "test.message.hl7")
    trules = os.path.join(this_dir, "resources", "test.correct.rules")
    runner = CliRunner()
    out = runner.invoke(main, [trules, tmsg])
    assert out.exit_code == 0


def test_structure_validation_complex():
    test_msg = (
        b"MSH|^~\\&|SrcSystem||TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r"
        b"PID|1|0000|||\r"
        b"PV1||||\r"
        b"OBR|||\r"
        b"ABC||||\r"
        b"NTE|||\r"
        b"NTE|||\r"
    )

    rules = """
// import "pkg://hl7validator/resources/base_hl7.rules"

 MSH
   PID  0..1
     // [XXX] notation is an equivalent of XXX 0..1
     [PV1]
     NTE 1..n
   OBR  1..n
     NTE 0..1
  
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
    assert len(ctx.get_errors())
    assert not ctx.is_valid
    errors = ctx.get_errors()
    assert errors[0].selector.sel == "NTE"
    assert errors[0].selector.cardinality == Cardinality.SEGMENT_AT_LEAST_ONE
    assert errors[1].selector.sel == "NTE"
    assert errors[1].selector.cardinality == Cardinality.SEGMENT_AT_MOST_ONE


def test_structure_validation_import():
    test_msg = (
        b"MSH|^~\\&|SrcSystem|SrcSystemLabName|TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r"
        b"PID|1|0000|||\r"
        b"PV1|aaa|||\r"
        b"OBR|||\r"
        b"ABC||||\r"
        b"NTE|||\r"
        b"NTE|||\r"
    )

    rules = """
import "pkg://hl7validator/resources/base_hl7.rules"
MSH
  PID
    PV1
    NTE 0..n

"PV1.1" must be not empty

"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)
    assert len(validator.transformer.get_rules()) == 4  # 4 rules from import
    assert len(validator.transformer.get_structure()) == 2  # 1 rule for structure (MSH)
    assert len(ctx.log) == 10  # 3 rules from import + 1 rule from local + 2 main structure rules (with 6 children inside)

    assert not len(ctx.get_errors())
    assert ctx.is_valid


def test_structure_validation_import_bad_structure():
    test_msg = b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"

    rules = """
import "pkg://hl7validator/resources/base_hl7.rules"
// no other rules
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert len(ctx.log) == 4  # 3 rules from import + 1 import strucutre rule

    assert len(validator.transformer.get_rules()) == 3  # 4 rules from import
    assert len(validator.transformer.get_structure()) == 1  # 1 rule for structure (MSH)
    assert not ctx.is_valid
    assert len(ctx.get_errors()) == 2

    errors = ctx.get_errors()
    assert errors[0].selector.sel == "MSH.3"
    assert errors[1].selector.sel == "MSH.5"
    assert isinstance(errors[0].rule.predicate, MustBe)
    assert isinstance(errors[1].rule.predicate, MustBe)
    assert isinstance(errors[0].rule.predicate.expected, AnyValue)
    assert isinstance(errors[1].rule.predicate.expected, AnyValue)


def test_structure_validation_duplicate_segment():
    test_msg = (b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"
                b"SE1||||\r"
                b"SE2||||\r"
                b"SE2||||\r"
                b"SE3||||\r"
                )

    rules = """
SE1
SE2
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert not ctx.is_valid
    errors = ctx.get_errors()
    assert len(errors) == 1
    assert errors[0].selector.sel == 'SE2'


def test_structure_validation_order():
    test_msg = (b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"
                b"SE1||||\r"
                b"SE2||||\r"
                b"SE3||||\r"
                )

    rules = """
SE2
SE1
SE3
MSH
SE2
  SE3
  
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert len(validator.transformer.get_rules()) == 0
    assert len(validator.transformer.get_structure()) == 5
    assert ctx.is_valid


def test_structure_validation_order_duplicated():
    test_msg = (b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"
                b"SE1||||\r"
                b"SE2||||\r"
                b"SE3||||\r"
                b"SE2||||\r"
                )

    rules = """
// the message is not valid, because there's a SE2 segment without following SE3 
SE2
  SE3
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert not ctx.is_valid
def test_structure_validation_order_duplicated_chain():
    test_msg = (b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"
                b"SE1||||\r"
                b"SE2||||\r"
                b"SE3||||\r"
                b"SE4||||\r" )

    rules = """ 
SE2
  SE3
    SE4
SE3
  SE4
SE5 0
SE2 0..1
  SE3 0..1
    SE5 0..1
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert ctx.is_valid


def test_structure_validation_zero_segment():
    test_msg = (b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"
                b"SE1||||\r"
                b"SE2||||\r"
                b"SE3||||\r"
                b"SE2||||\r" )

    rules = """ 
SE2 1..n
  SE3
     SE4 0
     SE2
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert ctx.is_valid

def test_structure_validation_one_or_more_segment():
    test_msg = (b"MSH|^~\\&|||||200705271331||OML^O21|12345|P|2.4\r"
                b"SE1||||\r"
                b"SE2||||\r"
                b"SE3||||\r"
                b"SE2||||\r" )

    rules = """ 
SE2 1..n
  SE3
     SE4 1..n
"""
    validator = Validator(rules=rules)
    ctx = validator.validate(test_msg)

    assert not ctx.is_valid
