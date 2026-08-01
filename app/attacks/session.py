"""Attack session lifecycle helpers."""

from __future__ import annotations

from .models import AttackSession


class AttackSessionManager:
    """In-memory session lifecycle manager for attack executions."""

    def create_session(
        self,
        attack_id: str,
        *,
        metadata: dict | None = None,
        attack_variant: str | None = None,
        requested_mode: str | None = None,
        execution_mode: str | None = None,
    ) -> AttackSession:
        session = AttackSession(attack_id=attack_id, metadata=metadata or {})
        if attack_variant:
            session.attack_variant = attack_variant
        # Accept optional modes as strings or ExecutionMode values
        if requested_mode:
            try:
                from .metadata import ExecutionMode

                session.requested_mode = ExecutionMode.normalize(requested_mode)
            except Exception:
                session.requested_mode = None
        if execution_mode:
            try:
                from .metadata import ExecutionMode

                session.execution_mode = ExecutionMode.normalize(execution_mode)
                session.active_mode = session.execution_mode
            except Exception:
                session.execution_mode = None
        session.record_event("session_created", {"attack_id": attack_id})
        return session

    def start_session(
        self,
        session: AttackSession,
        *,
        stage: str | None = None,
    ) -> AttackSession:
        session.start(stage=stage)
        return session

    def complete_session(self, session: AttackSession) -> AttackSession:
        session.complete()
        return session

    def fail_session(self, session: AttackSession) -> AttackSession:
        session.fail()
        return session
