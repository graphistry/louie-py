# Contributing to LouieAI Python Library

Thank you for your interest in contributing! We welcome contributions via pull requests.

## Developer Certificate of Origin

By contributing to this project, you are agreeing to the Developer Certificate of Origin (DCO). All commits must be signed off with:

```
Signed-off-by: Your Name <your.email@example.com>
```

You can do this automatically by using the `-s` flag when committing:

```bash
git commit -s -m "Your commit message"
```

The full DCO text is available at https://developercertificate.org/

This lightweight approach (no CLAs or paperwork!) ensures contributions can be legally included while keeping the process simple.

## Development Setup

- **Prerequisites**: Python 3.8+ and pip. You'll also need an account on Graphistry's platform to test against LouieAI.
- **Fork & Clone** this repository.
- **Install in dev mode**: `uv pip install -e ".[dev]"` to get all dependencies and tools.
- We use **pre-commit** hooks (to be set up in a later phase) for linting and formatting, and CI will run tests, linters (ruff), and mypy.

## Branching and GitFlow

We follow a GitFlow-like process:
- Work on a feature or fix in a branch (e.g., `feature/<name>` or `bugfix/<name>`).
- Submit a Pull Request to the `main` branch. Ensure all CI checks pass.
- Include a clear description of the change and reference any issue it addresses.

## Coding Guidelines

- Run `ruff` and `mypy` to ensure code style and type safety.
- Use type hints for all functions.
- Write or update tests for any new functionality (we aim for good coverage).
- Keep functions and classes documented with docstrings.

## Using AI Planning (Optional)

This project uses an AI co-pilot approach for some development tasks. We have an AI planning template under `AI_PROGRESS/PLAN_TEMPLATE.md`. If you'd like to use an AI assistant to help code, you can follow a similar approach (see `AI_PROGRESS/` for past plans). This is entirely optional but can help maintain consistency and traceability when using AI tools.

## Reporting Issues

Please open issues for bug reports or feature requests. Include as much detail as possible.

## Security

If you find a security vulnerability, please follow the instructions in [SECURITY.md](SECURITY.md).

-- Happy coding! --