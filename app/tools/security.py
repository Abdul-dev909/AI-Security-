"""Security validator enforcing strict sandbox root boundaries for tool file
operations.
"""

from __future__ import annotations

from pathlib import Path

from app.tools.exceptions import ToolSecurityError

# Absolute root path to the enterprise sandbox directory
SANDBOX_ROOT: Path = (
    Path(__file__).resolve().parent.parent.parent / "sandbox"
).resolve()


def get_sandbox_root() -> Path:
    """Return the absolute path to the sandbox root directory."""
    if not SANDBOX_ROOT.exists():
        SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
    return SANDBOX_ROOT


def validate_sandbox_path(user_path: str | Path) -> Path:
    """Validate and resolve a path string or Path object strictly within sandbox/.

    Rejects:
    - Null / empty inputs
    - Path traversal attempts using '../' or '/..'
    - Absolute host paths pointing outside sandbox/
    - Symbolic links pointing outside sandbox/

    Returns:
        Path: The absolute resolved Path object inside sandbox/
    """
    if not user_path or (isinstance(user_path, str) and not user_path.strip()):
        user_path = "."

    raw_path_str = str(user_path).strip()
    root = get_sandbox_root()

    # Reject null byte injection
    if "\x00" in raw_path_str:
        raise ToolSecurityError("Security Violation: Path contains invalid null bytes.")

    # Convert to Path object
    target_path = Path(raw_path_str)

    if target_path.is_absolute():
        # If absolute, it must start with SANDBOX_ROOT
        try:
            resolved_path = target_path.resolve(strict=False)
        except Exception as exc:
            raise ToolSecurityError(
                f"Security Violation: Invalid path resolution: {exc}"
            ) from exc
    else:
        # Relative paths are appended to SANDBOX_ROOT
        resolved_path = (root / target_path).resolve(strict=False)

    # Check commonpath boundary enforcement
    try:
        common = Path(get_sandbox_root()).resolve()
        # Verify that resolved_path is relative to root
        resolved_path.relative_to(common)
    except ValueError as err:
        raise ToolSecurityError(
            f"Security Violation: Directory traversal detected for path "
            f"'{raw_path_str}'. Access outside sandbox/ is strictly prohibited."
        ) from err

    # Check symlink safety if target exists
    if resolved_path.is_symlink():
        real_target = resolved_path.readlink().resolve()
        try:
            real_target.relative_to(common)
        except ValueError as err:
            raise ToolSecurityError(
                f"Security Violation: Symbolic link '{raw_path_str}' "
                "points outside sandbox root."
            ) from err

    return resolved_path


def get_relative_sandbox_path(absolute_path: Path) -> str:
    """Return a clean string representation of absolute_path relative to
    sandbox root.
    """
    root = get_sandbox_root()
    try:
        rel = absolute_path.resolve().relative_to(root)
        return str(rel) if str(rel) != "." else ""
    except ValueError:
        return str(absolute_path)


def validate_text_file(resolved_path: Path) -> None:
    """Validate that a resolved path is an existing readable text file (non-binary)."""
    if not resolved_path.exists():
        raise ToolSecurityError(
            f"File not found: '{get_relative_sandbox_path(resolved_path)}'."
        )

    if not resolved_path.is_file():
        raise ToolSecurityError(
            f"Path is not a regular file: '{get_relative_sandbox_path(resolved_path)}'."
        )

    # Read first block to ensure it's valid UTF-8 text and not binary
    try:
        with open(resolved_path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                raise ToolSecurityError(
                    f"Security Violation: Cannot read binary file "
                    f"'{get_relative_sandbox_path(resolved_path)}'."
                )
            chunk.decode("utf-8")
    except UnicodeDecodeError as err:
        raise ToolSecurityError(
            f"Security Violation: File '{get_relative_sandbox_path(resolved_path)}' "
            "is not valid UTF-8 text."
        ) from err
