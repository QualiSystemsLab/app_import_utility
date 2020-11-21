import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(os.path.join('version.txt')) as version_file:
    version_from_file = version_file.read().strip()

with open('requirements.txt') as f_required:
    required = f_required.read().splitlines()

with open('test_requirements.txt') as f_tests:
    required_for_tests = f_tests.read().splitlines()

setuptools.setup(
    name="cloudshell-app-helper",
    version=version_from_file,
    author="Quali",
    author_email="support@qualisystems.com",
    description="CloudShell package to assist with creating Apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={'': ['*.txt']},
    include_package_data=True,
    tests_require=required_for_tests,
    install_requires=required,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
)