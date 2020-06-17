# Contributing


## Contributing to app_import_utility

- Fork **app_import_utility** repository to [QualiSystemsLab](https://github.com/qualisystemslab) or to your own account.
- Clone it to your local machine using

```bash
$ git clone https://github.com/YOUR_ACCOUNT/app_import_utility.git
```

- Create a branch for local development
```bash
$ git checkout -b name-of-your-feature
```

- Make the required changes:
    - It's important to use to keep high standard of code, so please develop using TDD:
    ### TDD
      - Write a failing test first
      - Write a minimum amount of code to satisfy the failing test
      - Refactor the code

    - Running tests from command line:
    ```bash
    $ python setup.py test
    ```

- Commit and push them to github
```bash
$ git add .
$ git commit -m "Your detailed description of your changes"
$ git push origin name-of-your-feature
```
- Submit a pull request


## Pull Request Guidelines

Before you submit a pull request, make sure it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated.
3. The pull request should support for Python 2.7.