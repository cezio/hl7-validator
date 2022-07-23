# HL7 Validator

`hl7validator` provides a declarative way of validating HL7 messages. This package provides a simple DSL to describe
validation rules. A HL7 message will be checked against those rules.

[![hl7validator - GH CI pipeline (py 3.8/3.9/3.10)](https://github.com/cezio/hl7-validator/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/cezio/hl7-validator/actions/workflows/python-package.yml)

## Installation

This is a work in progress. At the moment, the only way to install this tool is to use cloned source (into virtual env):

```shell
$ git clone https://github.com/cezio/hl7-validator.git
$ cd hl7-validator
$ python -m venv venv
$ source venv/bin/activate
$ pip install .
```

## Usage

### In code:

You can validate a HL7 message in few lines, assuming you have proper rules ready:

```python

from hl7validator.validator import Validator

rules = """
// we expect OML^O21 in MSH.9, but we need to look into subfields with python-hl7
MSH.9.1.1 must be "OML"
MSH.9.1.2 must be "O21"
HSH.12.1 must be one of "2.3", "2.4", "2.5"
"""

msg = test_msg = r'MSH|^~\\&|SrcSystem||TargetSystem|LabName|200705271331||OML^O21|12345|P|2.4\r'
validator = Validator(rules)
result = validator.validate(msg)
assert result.is_valid

```

### As cli script

Validation is also available as a CLI script: `validate_hl7`. Incorrect message will result in non-zero return code from
the script:

```shell

$ validate_hl7 tests/resources/test.incorrect.rules tests/resources/test.message.hl7 
Message is invalid:
 * validation error for <FieldSelector sel=MSH.3.1> value FromSystem | <FieldValidationRule: <FieldSelector sel=MSH.3.1> <MustBe(expected=<ConstValue: SrcSystem>)> >
 * validation error for <FieldSelector sel=MSH.3.1> value FromSystem | <FieldValidationRule: <FieldSelector sel=MSH.3.1> <MustBe(expected=<OneOfValues: ['SrcSystem', 'OtherSystem']>)> >
$ echo $?
1
```

Correct message will return zero as return code, and will print the `Message is valid.` message, which can be suppressed
with `-q` switch.

```shell
$ validate_hl7 tests/resources/test.correct.rules tests/resources/test.message.hl7 
Message is valid.
 $ echo $?
0
```

# Validation rules

A HL7 message can be validated with a set of rules written in human-friendly form with a dedicated DSL. Each rule is one
line.
A rule is a check on a specific field if the value of this field matches certain conditions. Field is specified with
accessor notation: `AAA.1.1` (or `AAA.1.1.1` if you need to access a subfield).
See [accessor documentation in python-hl7 for details](https://python-hl7.readthedocs.io/en/latest/accessors.html).
Once field selection is specified, value conditions can be specified. You can specify if a value should:

* be not empty
* be of a specific type (int, string)
* be of a specific value (constant value) or within a specific set of values (a list of allowed values)
* match a specific regexp
* match specific criteria, if it's not empty (`may be`)
* be dependent on another field (current field will be checked if other field's check will be positive; syntax for
  dependent checks is similar to base checks

You can also put comments prepended with `//` chars.

Sample set of rules:

```
// this is a comment
// this value must not be empty
 "MSH.3.1" must be not empty
 // this value must be a proper string
 "MSH.3.1" must be string
 // this value should be a string if speficied (implies it should not be empty)
 "MSH.3.2" may be string
 // cannot be that value
 "MSH.3.1" cannot be "AnySystem"
 // must be a specific string value
 "MSH.3.1" must be "FromSystem"
 // list of allowed values
 "MSH.3.1" must be one of "FromSystem", "OtherSystem"
 // this is a regexp
 "MSH.7.1" must match r"[0-9]{12}"
 // dependency on another field
 "NTE.2.1" must be "P" if "PID.2.1" is not empty
 // various checks:
 "NTE.2.1" must be "P" if "PID.2.1" is of value "ABC"
 "NTE.2.1" must be "P" if "PID.2.1" matches r"ABC"
 "NTE.2.1" must be "P" if "PID.2.1" is one of "ABC", "BCD", "CDE"
 "NTE.2.2" must be "P" if "PID.2.1" is of type string
```

See [the grammar file](https://github.com/cezio/hl7-validator/blob/master/src/hl7validator/resources/hl7validation.lark)
for details.