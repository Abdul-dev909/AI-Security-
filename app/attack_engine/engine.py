"""Attack Engine coordination module."""

from __future__ import annotations

import logging

from app.attack_engine.executor import AttackExecutor
from app.attack_engine.models import AttackResult
from app.attack_engine.registry import AttackRegistry

logger = logging.getLogger(__name__)


class AttackEngine:
    """Coordinating engine for iterating over and executing registered attacks."""

    def __init__(self, executor: AttackExecutor) -> None:
        """Initialize the engine with an attack executor.

        Args:
            executor: The AttackExecutor instance to run each attack.
        """
        self.executor = executor

    def run(self, registry: AttackRegistry) -> list[AttackResult]:
        """Execute all enabled attacks in the registry and return their results.

        Args:
            registry: The AttackRegistry containing attack definitions.

        Returns:
            A list of AttackResult instances for each executed attack.
        """
        logger.info("Starting attack engine execution run.")
        results: list[AttackResult] = []

        for attack in registry.list():
            if not attack.enabled:
                logger.info(
                    "Skipping disabled attack: %s (ID: %s)", attack.name, attack.id
                )
                continue

            result = self.executor.execute(attack)
            results.append(result)

        logger.info(
            "Attack engine execution run completed. Executed %d attacks.", len(results)
        )
        return results
