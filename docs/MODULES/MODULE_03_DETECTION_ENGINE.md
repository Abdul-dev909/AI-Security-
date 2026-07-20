# Module 03: Detection Engine

## Purpose
The Detection Engine provides real-time security analysis of interactions between the user and the AI agent. It acts as a passive observer, scanning the conversation context (user prompts and AI responses) to identify prompt injections, jailbreaks, data leakage, and instruction overrides.

## Overview
The detection engine is deeply integrated with the Attack Executor. Upon every successful attack execution, the engine evaluates the resulting `DetectionContext` using a registry of specialized detectors. The aggregated results are packaged into a `DetectionReport` and included in the final `AttackResult`. This allows downstream systems and the API to expose security insights without interrupting the core conversation flow.

## Responsibilities
- **Context Collection**: Gather the user prompt, AI response, and conversation history into a unified `DetectionContext`.
- **Detection Execution**: Route the context through all registered detectors via the `DetectionCoordinator`.
- **Fault Tolerance**: Ensure that individual detector failures are logged and do not crash the overarching detection pipeline.
- **Reporting**: Aggregate individual detector findings into a comprehensive `DetectionReport` containing overall severity, total detections, and lightweight metadata (e.g., execution time).

## Architecture
The module follows a clean, extensible pattern:
- **`DetectionContext`**: The data payload passed to each detector.
- **`BaseDetector`**: Abstract interface for all detection rules.
- **`DetectorRegistry`**: Central repository for loading and listing active detectors.
- **`DetectionCoordinator`**: Orchestrates the execution loop over all registered detectors, catching exceptions and aggregating `DetectionResult` objects.
- **Integration Layer**: The engine is hooked directly into `AttackExecutor.execute()`, ensuring that any successful AI interaction is automatically scanned.

## Components
- **CanaryDetector**: Identifies leakage of sensitive tokens (e.g., API keys, passwords) in the AI's output.
- **JailbreakDetector**: Spots common jailbreak patterns and dangerous system commands in the AI's response without expected refusal phrases.
- **PromptLeakageDetector**: Looks for exposure of hidden system instructions or developer notes.
- **InstructionOverrideDetector**: Analyzes both user prompt (for manipulation attempts like "ignore previous instructions") and AI response (for compliance indicators).

## Data Flow
1. The **User** sends an adversarial prompt (simulated by the Attack Engine).
2. The **AttackExecutor** queries the AI agent and receives a response.
3. The `AttackExecutor` builds a **DetectionContext**.
4. The **DetectionCoordinator** loops through the **DetectorRegistry**.
5. Each **Detector** analyzes the context and returns a **DetectionResult**.
6. The Coordinator compiles a **DetectionReport** and returns it to the Executor.
7. The Executor embeds the report into the **AttackResult**, which is returned to the caller (API or test suite).

## Interfaces
- **Internal API**: `DetectionCoordinator.run_detection(context: DetectionContext) -> DetectionReport`
- **External Integration**: API endpoints that return an `AttackResult` or `ChatResponse` will include the `DetectionReport` payload.

## Extensibility
To add a new detector:
1. Subclass `BaseDetector`.
2. Implement the `name`, `description`, and `detect()` properties/methods.
3. Register the new detector in the app initialization (e.g., `app/main.py`).

## Future Improvements
- **Asynchronous Detection**: Run detectors in parallel using `asyncio` to reduce overall latency.
- **Dynamic Rule Updates**: Allow adding or modifying regex/heuristic rules without restarting the server.
- **Active Filtering**: Transition from passive observation to active interception (blocking malicious requests before they reach the LLM).
