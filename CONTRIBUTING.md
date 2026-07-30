# Contributing to vivainsights

Thank you for your interest in contributing to vivainsights! We welcome contributions from everyone, and we appreciate your help in making our project better.

## Getting Started

To get started, please follow these steps:

1. Fork the repository and clone it to your local machine.
2. Install the package in editable mode by running `python -m pip install -e .`.
3. Create a new branch for your changes.
4. Make your changes and commit them to your branch.
5. Push your branch to your forked repository.
6. Open a pull request to the main repository.

## Code Style

We follow the PEP 8 style guide for Python code. Please make sure your code adheres to this style guide before submitting a pull request.

## Testing

Tests use Python's `unittest` framework. Please include tests for behavioral
changes and run:

```console
python -m unittest discover -s tests -p "test_*.py"
```

Documentation changes should also build without warnings:

```console
sphinx-build -W --keep-going -b html docs docs/_build/html
```

## Code of Conduct

Please note that we have a code of conduct in place to ensure that our community is welcoming and inclusive. By participating in this project, you agree to abide by its terms.

## Contact Us

If you have any questions or concerns, please don't hesitate to contact us at [email address].