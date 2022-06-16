import hl7
import pytest

# from hl7validator.predicates import MustBe, MayBe
# from hl7validator.selectors import SegmentSelector, FieldSelector
# from hl7validator.values import StringValue, AnyValue, IntValue, ConstValue, OneOfValues, CannotBe

@pytest.mark.skip('old api')
def test_predicate_must_be():

    test_msg = r'MSH|^~\\&|SrcSystem||TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r"'
    msg = hl7.parse(test_msg)

    must_be = MustBe(msg)
    # MSH.9 = OML^O21
    assert must_be.eval(FieldSelector('MSH.9.1.1'), ConstValue('OML'))
    assert must_be.eval(FieldSelector('MSH.9.1.2'), ConstValue('O21'))
    # MSH.12 = 2.3 or 2.4
    assert must_be.eval(FieldSelector('MSH.12.1.1'), OneOfValues('2.3', '2.4'))
    # MSH.2 no other than SrcSystem
    assert must_be.eval(FieldSelector('MSH.3.1.1'), ConstValue('SrcSystem'))
    with pytest.raises(AssertionError):
        assert must_be.eval(FieldSelector('MSH.3.1.1'), CannotBe('SrcSystem'))

@pytest.mark.skip('old api')
def test_predicate_may_be():
    test_msg = r'MSH|^~\\&|SrcSystem||TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r"'
    msg = hl7.parse(test_msg)

    may_be = MayBe(msg)
    # MSH.9 = OML^O21
    assert may_be.eval(FieldSelector('MSH.9.1.1'), ConstValue('OML'))

    with pytest.raises(AssertionError):
        assert may_be.eval(FieldSelector('MSH.9.1.1'), ConstValue('FOO'))
    assert may_be.eval(FieldSelector('MSH.8.1.1'), ConstValue('Any')) is None
