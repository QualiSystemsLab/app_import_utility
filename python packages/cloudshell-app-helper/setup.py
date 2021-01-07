from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('version.txt') as version_file:
    version_from_file = version_file.read().strip()

with open('requirements.txt') as f_required:
    required = f_required.read().splitlines()

with open('test_requirements.txt') as f_tests:
    required_for_tests = f_tests.read().splitlines()

setup(
    name="cloudshell-app-helper",
    author="Quali",
    author_email="support@qualisystems.com",
    description="CloudShell package to assist with creating Apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    test_suite='unittest',
    test_requires=required_for_tests,
    package_data={'': ['*.txt']},
    install_requires=required,
    version=version_from_file,
    include_package_data=True,
    keywords="sandbox cloud cloudshell helper",
    classifiers=[
        "Development Status :: 1 - Beta",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ]
)