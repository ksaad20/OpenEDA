# Contributing to OpenEDA

Thank you for your interest in contributing to OpenEDA! This document provides guidelines for contributing to the project.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Contributor License Agreement](#contributor-license-agreement)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Code Style](#code-style)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)
8. [Community Guidelines](#community-guidelines)
9. [Contact](#contact)

---

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/ksaad20/OpenEDA.git
   cd OpenEDA

   git remote add upstream https://github.com/ksaad20/OpenEDA.git

Contributor License Agreement

All contributors must agree to our Contributor License Agreement (CLA).

By submitting a pull request, issue, or any contribution to the OpenEDA repository, you acknowledge that you have read and agree to the terms of our CLA.


If you have not yet signed the CLA, you will be prompted to do so when you open your first pull request. The CLA ensures that:

You have the right to submit your contribution

You grant OpenEDA the necessary licenses to use and distribute your contribution

The project can be relicensed for commercial purposes while preserving your rights under Apache 2.0

For corporate contributions, please contact the maintainers to execute a separate Corporate CLA.


How to Contribute:

Reporting Bugs

Before reporting a bug, please check existing issues to avoid duplicates. When reporting, include:

A clear description of the bug

Steps to reproduce

Expected vs. actual behavior

Your environment (OS, Python version, relevant dependencies)

Error messages or logs

Suggesting Features


Feature requests are welcome! Please open an issue with:

A clear description of the feature

The motivation/use case

Any proposed implementation approach


Contributing Code
1. Create a new branch for your feature or fix:

bash
git checkout -b feature/your-feature-name

3. Make your changes
4. Write or update tests
5. Update documentation as needed
6. Commit with clear messages
7. Development Setup
8. Prerequisites:
   
Python 3.9+
pip or conda

Installation

bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

Code Style
We follow PEP 8 for Python code. Please ensure your code:
Passes flake8 linting
Is formatted with black
Has type hints where appropriate
Includes docstrings for public functions and classes

# Run linting
flake8 openeda/

# Run formatting
black openeda/ tests/

Testing
All contributions should include tests. We use pytest.

# Run all tests
pytest

# Run with coverage
pytest --cov=openeda --cov-report=html

Aim for high test coverage on new code
Include unit tests for individual functions
Include integration tests for workflows

Pull Request Process
Ensure your CLA is signed — PRs will be blocked until this is complete
Update your branch with the latest upstream changes:
bash
git fetch upstream
git rebase upstream/main
Push your branch to your fork
Open a pull request against ksaad20/OpenEDA:main
Fill out the PR template with:
Description of changes
Related issue numbers
Testing performed
Breaking changes (if any)
Wait for review — maintainers will review within a few days
Address review feedback
Once approved, your PR will be merged
Community Guidelines
Be respectful and constructive in all interactions
Focus on technical merit in discussions
Help newcomers learn and contribute
Respect differing viewpoints and experiences
Contact
Issues: GitHub Issues
Discussions: GitHub Discussions
Email: kazisaadasif29@gmail.com

Thank you for helping make OpenEDA better!

---

To add this to your repo:

1. Go to `github.com/ksaad20/OpenEDA`
2. Click **Add file** → **Create new file**
3. Name it `CONTRIBUTING.md`
4. Paste the text above
5. Commit with message: `Add CONTRIBUTING.md with CLA reference and contribution guidelines`
