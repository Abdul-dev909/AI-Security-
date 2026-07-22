"""Exceptions raised by the Tool Execution Framework."""

from __future__ import annotations


class ToolError(Exception):
    """Base exception for all tool execution framework errors."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found in the registry."""


class ToolSecurityError(ToolError):
    """Raised when a tool request violates sandbox boundaries or security policies."""


class ToolExecutionError(ToolError):
    """Raised when a tool encounters an operational failure during execution."""


class InvalidArgumentError(ToolError):
    """Raised when provided arguments do not conform to the tool's expected schema."""
