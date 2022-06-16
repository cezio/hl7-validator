import pathlib
import pkg_resources
from setuptools import setup, find_namespace_packages

with pathlib.Path('requirements.in').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]


setup(
    name='hl7-validator',
    version='0.1',
    description='HL7 validation helper',
    long_description='',
    author='Cezary Statkiewicz',
    author_email='c.statkiewicz@gmail.com, cezio@thelirium.net',
    license='MIT',
    package_dir={'': 'src/'},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
        install_requires=install_requires,
    package_data={"hl7validator.resources": ["*.lark"],
                  "hl7validator": ["*.txt", "*.md", "*.rst"]
            },
    # include_package_data=True
    packages=find_namespace_packages(where='src/',
                                     exclude=['tests', 'tests.*']),
    zip_safe=False,
)
