"""Attack Registry for managing attack definitions."""

from __future__ import annotations

from app.attack_engine.models import Attack


class AttackRegistry:
    """Registry for registering, unregistering, and listing attack definitions.

    Contains no execution logic. Uses a dictionary internally to manage attacks by their IDs.
    """

    def __init__(self) -> None:
        """Initialize an empty attack registry."""
        self._attacks: dict[str, Attack] = {}

    def register(self, attack: Attack) -> None:
        """Register a new attack definition.

        Args:
            attack: The Attack model instance to register.

        Raises:
            ValueError: If an attack with the same ID is already registered.
        """
        if attack.id in self._attacks:
            raise ValueError(f"Attack with ID '{attack.id}' is already registered.")
        self._attacks[attack.id] = attack

    def unregister(self, attack_id: str) -> None:
        """Remove an attack definition from the registry.

        Args:
            attack_id: The ID of the attack to unregister.

        Raises:
            ValueError: If the attack ID is not found in the registry.
        """
        if attack_id not in self._attacks:
            raise ValueError(f"Attack with ID '{attack_id}' not found in registry.")
        del self._attacks[attack_id]

    def get(self, attack_id: str) -> Attack | None:
        """Retrieve an attack definition by its ID.

        Args:
            attack_id: The ID of the attack to retrieve.

        Returns:
            The Attack model instance if found, otherwise None.
        """
        return self._attacks.get(attack_id)

    def list(self) -> list[Attack]:
        """List all currently registered attack definitions.

        Returns:
            A list of all registered Attack model instances.
        """
        return list(self._attacks.values())

    def clear(self) -> None:
        """Clear all registered attack definitions from the registry."""
        self._attacks.clear()
