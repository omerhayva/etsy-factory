from __future__ import annotations


class AutomationError(RuntimeError):
    """Base exception for user-facing automation errors."""


class ConfigurationError(AutomationError):
    """Raised when a required integration setting is missing."""


class ApiError(AutomationError):
    """An external API returned an error response."""


class DuplicateScheduleError(AutomationError):
    """A non-cancelled job already exists for the same listing, board and time."""
