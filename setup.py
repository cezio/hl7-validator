import pathlib
import pkg_resources
from setuptools import setup, find_namespace_packages

with pathlib.Path("requirements.in").open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name="hl7-validator",
    version="0.2",
    description="HL7 validation helper",
    long_description="",
    author="Cezary Statkiewicz",
    author_email="c.statkiewicz@gmail.com, cezio@thelirium.net",
    license="MIT",
    python_requires=">=3.7",
    package_dir={"": "src/"},
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=install_requires,
    package_data={
        "hl7validator.resources": ["*.lark"],
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
