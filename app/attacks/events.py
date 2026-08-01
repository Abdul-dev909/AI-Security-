"""Event bus for internal orchestration events."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from collections.abc import Callable
from typing import Any

from .models import AttackTimelineEvent


@runtime_checkable
class EventSubscriber(Protocol):
    """Subscriber for attack events."""

    def on_event(self, event: AttackTimelineEvent) -> None:
        """Handle an emitted event."""
        ...


class EventBus:
    """Internal event bus for orchestrator events."""

    def __init__(self) -> None:
        self._subscribers: list[EventSubscriber | Callable[[AttackTimelineEvent], None]] = []

    def subscribe(self, subscriber: EventSubscriber | Callable[[AttackTimelineEvent], None]) -> None:
        """Subscribe to events."""
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber | Callable[[AttackTimelineEvent], None]) -> None:
        """Unsubscribe from events."""
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def publish(self, event: AttackTimelineEvent) -> None:
        """Publish an event to all subscribers."""
        for subscriber in self._subscribers:
            try:
                if hasattr(subscriber, "on_event"):
                    subscriber.on_event(event) # type: ignore
                else:
                    subscriber(event) # type: ignore
            except Exception:
                # Event handlers should not crash the execution flow
                pass
