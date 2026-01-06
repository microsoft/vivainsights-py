# Summary
This branch *<succinct summary of the purpose>*

# Changes
The changes made in this PR are:
1. Change 1
1. Change 2

# Checklist

## Always required

- [ ] All checks pass (run `python -m unittest discover -s tests -f` or `python run_tests_and_cleanup.py` locally)
- [ ] `NEWS.md` has been updated

## Adding new features

- [ ] New module has corresponding test file
- [ ] `vivainsights/__init__.py` is updated

## For releases

- [ ] Versions are updated in `pyproject.toml`, `setup.py`, `__init__.py`, and `docs/conf.py` (if applicable)
- [ ] `dist/` cleared before `python setup.py sdist bdist_wheel`
- [ ] Run `sphinx-apidoc -o docs vivainsights` to ensure all modules are included for the documentation site

# Change Type
Please check the type of change your PR introduces:
- [ ] Bugfix
- [ ] Feature (incl. changes to visualizations)
- [ ] Technical design
- [ ] Build related changes (e.g. tests)
- [ ] Refactoring (no functional changes, no api changes)
- [ ] Code style update (formatting, renaming) or Documentation content changes
- [ ] Other (please describe): 

# Notes
This fixes #<issue_number>

*<other things, such as how to incorporate new changes>*
*<brief summary of the purpose of this pull request>*
