# Engineering Setup Guide

This guide details the procedures for setting up the local development environment, installing core and developer dependencies, managing pre-commit hook automations, running unit test suites, and setting up VS Code configuration.

---

## Project Setup & Virtual Environment

To isolate dependencies and ensure reproducible builds, we use a Python virtual environment.

### 1. Clone & Navigate
```bash
git clone <repository_url>
cd AI-Security-
```

### 2. Create the Virtual Environment
We recommend using Python 3.10 or higher:
```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment
- **Linux/macOS**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (Command Prompt)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

---

## Installing Dependencies

Install both the runtime application dependencies and dev-tools (Ruff, Black, isort, MyPy, pre-commit) configured in `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Installing & Configuring pre-commit

We use `pre-commit` to run code checks before commits are recorded.

### 1. Install Git Hooks
Once `pre-commit` is installed via `requirements.txt`, register it in the local Git configuration:
```bash
pre-commit install
```

### 2. Optional: Run Checks Against All Files
Verify the configuration by running all hooks on every file in the project manually:
```bash
pre-commit run --all-files
```

---

## Code Quality & Dev Commands

The following tools are configured via [pyproject.toml](file:///home/dawoodkali/Projects/AI-Security-/pyproject.toml) and [pytest.ini](file:///home/dawoodkali/Projects/AI-Security-/pytest.ini).

### 1. Code Formatting (Black & isort)
To format code and check imports sorting:
```bash
# Format Python code
black app/ tests/

# Sort imports
isort app/ tests/
```

### 2. Linting (Ruff)
To run Ruff checkups for style suggestions and common issues:
```bash
# Run lint check
ruff check app/ tests/

# Run lint check with auto-fixing enabled
ruff check app/ tests/ --fix
```

### 3. Type Checking (MyPy)
To run static analysis checking for type safety issues:
```bash
mypy app/
```

### 4. Running Tests (pytest)
To execute the pytest automated test suite with verbose output:
```bash
pytest
```

---

## VS Code Integration

We have included pre-configured workspace setting options inside the repository to streamline your coding flow.

### Recommended Extensions
When opening the project in VS Code, install the workspace recommended extensions:
- **Python** (`ms-python.python`): Core language support.
- **Pylance** (`ms-python.vscode-pylance`): Fast, feature-rich language server.
- **Ruff** (`charliermarsh.ruff`): Fast import sorting and linting.
- **Black Formatter** (`ms-python.black-formatter`): Code styling formatting.
- **GitHub Copilot** (`github.copilot`): AI pair programmer.
- **GitLens** (`eamodio.gitlens`): Comprehensive git visualization.
- **Markdown All in One** (`yzhang.markdown-all-in-one`): Markdown authoring utility.
- **Docker** (`ms-azuretools.vscode-docker`): Container management helper.
- **YAML** (`redhat.vscode-yaml`): Configuration file checking.

### Pre-Configured Settings
The workspace settings file [.vscode/settings.json](file:///home/dawoodkali/Projects/AI-Security-/.vscode/settings.json) automates:
- **Format on Save**: Enabled via `ms-python.black-formatter`.
- **Ruff Hooks on Save**: Automatically removes unused imports and sorts libraries.
- **File Utilities**: Automatically trims trailing whitespace and adds final newlines on save.
- **Pytest Discovery**: Automatically discovers tests in the `tests/` directory.

---

## Common Development Command Cheatsheet

| Command | Action |
| :--- | :--- |
| `source .venv/bin/activate` | Activate Python virtual environment |
| `pip install -r requirements.txt` | Install/update dependencies |
| `pre-commit run --all-files` | Manually run pre-commit hooks |
| `pytest` | Execute backend tests |
| `ruff check . --fix` | Check and fix lint issues |
| `black .` | Format code standard layout |
| `mypy app/` | Type-check project source files |
