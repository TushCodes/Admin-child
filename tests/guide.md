# Tests guide

This folder contains automated and manual checks that help developers confirm the app still works after changes.

## File purposes

- `__init__.py` marks this folder as the tests module.
- `conftest.py` provides shared test setup.
- `e2e/` contains browser-style tests for full user flows.
- `manual/` contains scripts developers can run by hand while reproducing issues.
- `middleware/` contains tests for request and response middleware.
- `support/` contains helpers used by tests.
- `guide.md` is this plain-language guide to the tests folder.
