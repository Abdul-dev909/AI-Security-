# System Architecture

## Purpose
This document outlines the overarching architecture of the AI Security Assessment & Threat Intelligence Platform. It serves as a guide for developers and architects to understand the system topologies, boundaries, and how different modules interact to provide a secure, modular testing framework for LLMs.

## Overview
The platform consists of three core modules seamlessly integrated:
1. **Module 1: Vulnerable AI Agent** – A conversational interface connected to a backend LLM, designed to process user prompts and maintain conversational state.
2. **Module 2: Attack Engine** – An automated framework that executes a registry of adversarial prompts against the AI Agent to identify vulnerabilities.
3. **Module 3: Detection Engine** – A security layer that passively intercepts AI interactions to detect prompt injections, jailbreaks, and sensitive data leaks in real-time.

## Responsibilities
- **Extensibility**: Provide a clean interface to add new attacks (Module 2) and new detectors (Module 3) without modifying core orchestration logic.
- **Isolation**: Ensure the execution of one attack does not poison the conversational state of subsequent attacks.
- **Resilience**: Detectors must fail gracefully without interrupting the attack execution loop or the main application workflow.
- **Modularity**: Separate concerns strictly—Attack Engine iterates attacks, Attack Executor orchestrates a single run, and Detection Coordinator analyzes the result.

## Architecture
The system follows a modular, monolithic architecture deployed via FastAPI:
- **API Gateway (FastAPI)**: Routes HTTP requests (`/chat`, `/health`) and provides interactive swagger documentation.
- **State Management**: `ConversationManager` and `MemoryManager` handle conversation history and persistent memory storage (SQLite).
- **Orchestration**: The `AttackEngine` aggregates results from the `AttackExecutor`, which manages the lifecycle of a single interaction, integrating the `DetectionCoordinator` seamlessly.

## Components
- **FastAPI Backend**: The core web server.
- **Ollama Client**: Handles communication with the local LLM server.
- **SQLite Database**: Persists long-term agent memories.
- **Attack Registry & Executor**: Loads attacks and runs them in isolated contexts.
- **Detector Registry & Coordinator**: Loads detection rules and analyzes the `DetectionContext` post-generation.

## Data Flow
1. **Attack Iteration**: The `AttackEngine` pulls an `Attack` from the `AttackRegistry`.
2. **Execution**: The `AttackExecutor` clears the conversational history, builds the prompt using the `PromptBuilder`, and submits it to the `OllamaClient`.
3. **Response Handling**: The LLM response is returned. If execution fails, it is caught and logged.
4. **Detection**: If execution succeeds, the `AttackExecutor` builds a `DetectionContext` and passes it to the `DetectionCoordinator`.
5. **Aggregation**: The Coordinator runs all registered detectors and compiles a `DetectionReport`.
6. **Result Generation**: The `AttackExecutor` embeds the `DetectionReport` into an `AttackResult` and returns it to the `AttackEngine`.

## Interfaces
- **REST API**: JSON-based communication. `ChatResponse` objects naturally contain the `DetectionReport`.
- **Internal APIs**: Strongly typed Pydantic models (e.g., `Attack`, `AttackResult`, `DetectionContext`, `DetectionReport`) dictate data exchange between internal components.

## Dependencies
- **FastAPI / Pydantic**: For routing, data validation, and documentation.
- **Ollama**: Local inference engine.
- **SQLite3**: Lightweight, file-based database for memory persistence.
- **Pytest**: For robust unit and integration testing.

## Future Improvements
- **Decoupled Architecture**: Extract the Attack Engine into a separate microservice.
- **Web Dashboard**: Implement a React-based frontend to visualize Attack and Detection results in real-time.
- **Active Mitigation**: Allow the Detection Engine to intercept and sanitize outputs before they reach the frontend.
