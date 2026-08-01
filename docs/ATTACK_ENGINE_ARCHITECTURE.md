# Attack Engine Architecture (Enterprise)

This architecture defines a formal, stateful execution pipeline serving as the backbone for automated, manual, and hybrid AI attacks.

## Core Execution Pipeline

The execution of an attack follows a strict 10-step pipeline:

1. **Definition**: The `AttackDefinition` or `AttackPlugin` is selected.
2. **Planner**: The `AttackPlanner` generates an `AttackPlan` with specific `AttackObjective`s, determining the expected stages and estimated turns.
3. **Strategy**: The `AttackStrategy` maintains the `StrategyContext` (isolated from the global session) to determine the next immediate action (e.g., transition stage, prompt generation).
4. **Prompt Builder**: The `AttackPromptBuilder` generates the actual payload using the strategy context and conversation history.
5. **Executor**: The `AttackExecutor` operates as a pure stateless worker. It sends the prompt to the target AI and retrieves the response.
6. **Analyzer**: The `AttackResponseAnalyzer` analyzes the victim's response to detect leakage, refusals, and success conditions without requiring full AI reasoning initially.
7. **Strategy Evaluation**: The strategy evaluates the analyzed response against its current objectives.
8. **Decision Engine**: The `DecisionEngine` determines whether to retry, escalate, transition stages, or terminate based on the strategy's evaluation.
9. **Orchestrator**: The `AttackOrchestrator` is the central brain coordinating all the above components. It enforces the `OrchestratorState` machine and ensures no illegal state transitions occur.
10. **Timeline & Result**: The `EventBus` broadcasts `AttackTimelineEvent`s (which are stored in the session for future replay and visualization), and a final `AttackResult` is generated.

## Plugins & Extensibility

All future attacks should be implemented as plugins conforming to the `AttackPlugin` interface. A plugin bundles its own:
- `AttackPlanner`
- `AttackStrategy`
- `AttackPromptBuilder`
- `AttackResponseAnalyzer`

The `AttackRegistry` supports dynamic plugin registration.

## Conversation as a First-Class Object

The `AttackConversationManager` maintains the entire conversation using structured `AttackMessage` objects. Messages include metadata such as `sender`, `stage`, `turn_number`, `token_count`, `latency`, and `sequence_number`. The architecture supports multiple senders (`ATTACKER_AI`, `ATTACKER_USER`, `VICTIM_AI`, `SYSTEM`) allowing manual and automated attacks to share the exact same orchestration pipeline seamlessly.

## Stream-Friendly Hooks

The engine uses an `EventBus` to publish lifecycle events (`AttackStarted`, `StageChanged`, `PromptGenerated`, `ResponseReceived`, etc.). This decouple enables future UI modules (e.g., SSE or WebSockets) to subscribe to real-time events without modifying core orchestration logic.

## Session Persistence

The `AttackSessionStore` interface abstracts session persistence (e.g., in-memory, SQLite) for pause/resume and analytics capabilities.
