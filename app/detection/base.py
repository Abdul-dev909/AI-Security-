"""
Base classes for the detection framework.
"""

from abc import ABC, abstractmethod

from app.detection.models import DetectionContext, DetectionResult


class BaseDetector(ABC):
    """
    Abstract base class that all detectors must inherit from.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the detector."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the detector does."""

    @abstractmethod
    def detect(self, context: DetectionContext) -> DetectionResult:
        """
        Execute the detection logic.

        Args:
            context: A DetectionContext containing the data to be analyzed.

        Returns:
            DetectionResult: The result of the detection.
        """
