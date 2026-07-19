"""
Registry for managing detectors.
"""

from app.detection.base import BaseDetector


class DetectorRegistry:
    """
    Registry for managing available detectors.
    """

    def __init__(self) -> None:
        self._detectors: dict[str, BaseDetector] = {}

    def register(self, detector: BaseDetector) -> None:
        """
        Register a new detector instance.

        Args:
            detector: The detector instance to register.

        Raises:
            ValueError: If a detector with the same name is already registered.
        """
        if detector.name in self._detectors:
            raise ValueError(
                f"Detector with name '{detector.name}' is already registered."
            )
        self._detectors[detector.name] = detector

    def unregister(self, name: str) -> None:
        """
        Unregister a detector by name.

        Args:
            name: The name of the detector to unregister.

        Raises:
            KeyError: If the detector is not found.
        """
        if name not in self._detectors:
            raise KeyError(f"Detector with name '{name}' not found.")
        del self._detectors[name]

    def get_detector(self, name: str) -> BaseDetector:
        """
        Retrieve a detector by its name.

        Args:
            name: The name of the detector.

        Returns:
            BaseDetector: The requested detector.

        Raises:
            KeyError: If the detector is not found.
        """
        if name not in self._detectors:
            raise KeyError(f"Detector with name '{name}' not found.")
        return self._detectors[name]

    def list_detectors(self) -> list[BaseDetector]:
        """
        List all registered detectors.

        Returns:
            List[BaseDetector]: A list of all registered detector instances.
        """
        return list(self._detectors.values())
