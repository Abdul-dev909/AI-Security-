"""AgentPlanner stub for complex capability planning."""

from __future__ import annotations

from app.agent.context import AgentContext
from app.agent.models import CapabilityResolution


class AgentPlanner:
    """Planner layer for evaluating complex multi-step capability plans in future milestones."""

    def plan(
        self, context: AgentContext, resolution: CapabilityResolution
    ) -> CapabilityResolution:
        """Pass through resolution or refine tool arguments."""
        return resolution
