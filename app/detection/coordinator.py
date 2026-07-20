"""
Coordinator for executing multiple detectors.
"""

import logging

from app.detection.models import DetectionContext, DetectionReport, DetectionSeverity
from app.detection.registry import DetectorRegistry
from app.utils import execution_timer

logger = logging.getLogger(__name__)


class DetectionCoordinator:
    """
    Orchestrates the execution of multiple detectors against a given context.
    """

    def __init__(self, registry: DetectorRegistry) -> None:
        self.registry = registry

    def run_detection(self, context: DetectionContext) -> DetectionReport:
        """
        Execute all registered detectors against the provided context.

        Args:
            context: The DetectionContext to be analyzed.

        Returns:
            DetectionReport: The aggregated report of all detections.
        """
        report = DetectionReport()
        detectors = self.registry.list_detectors()

        severity_order = {
            DetectionSeverity.LOW: 1,
            DetectionSeverity.MEDIUM: 2,
            DetectionSeverity.HIGH: 3,
            DetectionSeverity.CRITICAL: 4,
        }

        logger.info("Detection started with %d detectors.", len(detectors))

        with execution_timer() as elapsed:
            for detector in detectors:
                try:
                    logger.debug("Running detector: %s", detector.name)
                    result = detector.detect(context)
                    report.results.append(result)
                    report.total_detectors_executed += 1

                    if result.detected:
                        report.total_detections += 1

                        if result.severity:
                            if report.highest_severity is None:
                                report.highest_severity = result.severity
                            else:
                                current_level = severity_order.get(
                                    report.highest_severity, 0
                                )
                                new_level = severity_order.get(result.severity, 0)
                                if new_level > current_level:
                                    report.highest_severity = result.severity

                except Exception as e:
                    logger.error(
                        "Detector '%s' failed: %s", detector.name, e, exc_info=True
                    )

        report.detection_time = elapsed()

        logger.info(
            "Detection completed in %.3fs. Executed: %d, "
            "Detections: %d, Highest Severity: %s",
            report.detection_time,
            report.total_detectors_executed,
            report.total_detections,
            report.highest_severity.name if report.highest_severity else "None",
        )

        return report
