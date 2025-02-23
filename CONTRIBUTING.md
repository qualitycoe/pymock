# Contributing to Pymock

Thank you for your interest in contributing to Pymock! We welcome contributions from everyone. Here’s how you can help:

## Getting Started
1. **Fork the Repository**: Clone it locally with `git clone https://github.com/yourusername/pymock.git`.
2. **Set Up Environment**:
   - Install Hatch: `pip install hatch`.
   - Create the environment: `hatch env create`.
3. **Install Pre-Commit**: Run `pre-commit install` to set up hooks.

## Making Changes
- **Branch**: Create a new branch (`git checkout -b feature/your-feature`).
- **Code Style**: Follow PEP 8, enforced by Black, Ruff, and Flake8 via pre-commit.
- **Type Hints**: Use MyPy for type checking; run `hatch run types:check`.
- **Tests**: Add tests in `tests/` and run `hatch run test`.

## Submitting Changes
1. **Commit**: Use clear messages (e.g., `git commit -m "Add feature X"`).
2. **Push**: `git push origin feature/your-feature`.
3. **Pull Request**: Open a PR on GitHub, describing your changes and linking to any issues.

## Bug Reports and Feature Requests
- Use the [GitHub Issues](https://github.com/qualitycoe/pymock/issues) page.
- Provide detailed descriptions, steps to reproduce, and expected behavior.

## Questions?
Email us at qualitycoe@outlook.com or open a discussion on GitHub.

Happy contributing!
