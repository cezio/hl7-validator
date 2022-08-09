import pathlib
import pkg_resources
from setuptools import setup, find_namespace_packages

install_requires = ['attrs', 'hl7', 'lark', 'click']

setup(
    name="hl7-validator",
    version="0.3.3",
    description="HL7 validation helper",
    long_description="HL7 Validation helper library allows to validate HL7 messages using human-readable rules files.\n"
                     " See `Readme <https://github.com/cezio/hl7-validator/tree/master#readme>`_ for details.",
    author="Cezary Statkiewicz",
    author_email="c.statkiewicz@gmail.com, cezio@thelirium.net",
    license="MIT",
    python_requires=">=3.7",
    package_dir={"": "src/"},
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=install_requires,
    package_data={
        "hl7validator.resources": ["*.lark", "*.rules"],
        "hl7validator": ["*.txt", "*.md", "*.rst"],
    },
    packages=find_namespace_packages(where="src/", exclude=["tests", "tests.*"]),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "validate_hl7 = hl7validator.cli:main",
        ],
    },
)
