"""Unit tests for the Enterprise Tool Execution Framework."""

from __future__ import annotations

import pytest

from app.tools.exceptions import ToolSecurityError
from app.tools.manager import ToolManager
from app.tools.registry import ToolRegistry
from app.tools.security import (
    get_sandbox_root,
    validate_sandbox_path,
    validate_text_file,
)


class TestSandboxSecurityValidator:
    """Security verification tests for sandbox path enforcement."""

    def test_valid_relative_path(self) -> None:
        path = validate_sandbox_path("engineering/architecture_spec.md")
        assert path.exists()
        assert "sandbox/engineering/architecture_spec.md" in str(path)

    def test_directory_traversal_rejection_dotdot(self) -> None:
        with pytest.raises(
            ToolSecurityError, match="Security Violation: Directory traversal detected"
        ):
            validate_sandbox_path("../../etc/passwd")

    def test_directory_traversal_rejection_nested(self) -> None:
        with pytest.raises(
            ToolSecurityError, match="Security Violation: Directory traversal detected"
        ):
            validate_sandbox_path("engineering/../../app/main.py")

    def test_absolute_path_outside_sandbox_rejected(self) -> None:
        with pytest.raises(
            ToolSecurityError, match="Security Violation: Directory traversal detected"
        ):
            validate_sandbox_path("/etc/passwd")

    def test_null_byte_injection_rejected(self) -> None:
        with pytest.raises(ToolSecurityError, match="Path contains invalid null bytes"):
            validate_sandbox_path("engineering\x00/architecture_spec.md")

    def test_binary_file_validation_rejection(self) -> None:
        sandbox_root = get_sandbox_root()
        binary_file = sandbox_root / "test_binary.bin"
        try:
            binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")
            with pytest.raises(ToolSecurityError, match="Cannot read binary file"):
                validate_text_file(binary_file)
        finally:
            if binary_file.exists():
                binary_file.unlink()


class TestInitialToolSet:
    """Verification tests for pwd, ls, cat, and grep tools."""

    def setup_method(self) -> None:
        self.registry = ToolRegistry()
        self.manager = ToolManager(registry=self.registry)

    def test_pwd_tool_execution(self) -> None:
        result = self.manager.execute_tool("pwd")
        assert result.success is True
        assert result.tool == "pwd"
        assert "sandbox" in result.result["cwd"]
        assert result.error is None

    def test_ls_tool_execution_root(self) -> None:
        result = self.manager.execute_tool("ls", path=".")
        assert result.success is True
        assert result.tool == "ls"
        entries = [e["name"] for e in result.result["entries"]]
        assert "engineering" in entries
        assert "executive" in entries
        assert "finance" in entries

    def test_ls_tool_execution_subfolder(self) -> None:
        result = self.manager.execute_tool("ls", path="engineering")
        assert result.success is True
        entries = [e["name"] for e in result.result["entries"]]
        assert "architecture_spec.md" in entries

    def test_ls_tool_missing_directory(self) -> None:
        result = self.manager.execute_tool("ls", path="non_existent_folder")
        assert result.success is False
        assert "Directory not found" in result.error

    def test_cat_tool_execution_success(self) -> None:
        result = self.manager.execute_tool(
            "cat", path="engineering/architecture_spec.md"
        )
        assert result.success is True
        assert "Project Aegis" in result.result["content"]
        assert result.result["size_bytes"] > 0

    def test_cat_tool_missing_file(self) -> None:
        result = self.manager.execute_tool("cat", path="engineering/non_existent.md")
        assert result.success is False
        assert "File not found" in result.error

    def test_grep_tool_execution(self) -> None:
        result = self.manager.execute_tool(
            "grep", query="Project Aegis", path="engineering"
        )
        assert result.success is True
        assert result.result["total_matches"] >= 1
        matches = result.result["matches"]
        assert any("architecture_spec.md" in m["file"] for m in matches)

    def test_grep_tool_case_sensitivity(self) -> None:
        result_insensitive = self.manager.execute_tool(
            "grep", query="aegis", path="engineering", case_sensitive=False
        )
        assert result_insensitive.success is True
        assert result_insensitive.result["total_matches"] >= 1


class TestToolManagerAndAuditEvents:
    """Verification tests for ToolManager and Security Audit Events."""

    def setup_method(self) -> None:
        self.audits = []
        self.manager = ToolManager(audit_callback=lambda evt: self.audits.append(evt))

    def test_audit_event_recorded_on_success(self) -> None:
        res = self.manager.execute_tool("pwd")
        assert res.success is True
        assert len(self.manager.audit_logs) == 1
        event = self.manager.audit_logs[0]
        assert event.tool_name == "pwd"
        assert event.status == "SUCCESS"
        assert event.duration_ms >= 0

    def test_audit_event_recorded_on_security_violation(self) -> None:
        res = self.manager.execute_tool("cat", path="../../etc/passwd")
        assert res.success is False
        assert res.error is not None
        assert "Directory traversal detected" in res.error
        event = self.manager.audit_logs[0]
        assert event.status == "SECURITY_VIOLATION"
        assert "Directory traversal" in event.error_message

    def test_audit_event_recorded_on_not_found(self) -> None:
        res = self.manager.execute_tool("non_existent_tool")
        assert res.success is False
        event = self.manager.audit_logs[0]
        assert event.status == "NOT_FOUND"
