# Summary
This branch *<succinct summary of the purpose>*

# Changes
The changes made in this PR are:
1. Change 1
1. Change 2

# Checks
- [ ] All checks pass (run `python -m unittest discover -s tests -f` or `python run_tests_and_cleanup.py` locally)
- [ ] Versions are updated in `pyproject.toml`, `setup.py`, and `docs/conf.py` (if applicable)
- [ ] `NEWS.md` has been updated
- [ ] If a new module has been added, a corresponding test has been created
- [ ] If a new module has been created, `vivainsights/__init__.py` is updated accordingly
- [ ] Everything under `dist` has been cleared prior to running `python setup.py sdist bdist_wheel`
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
