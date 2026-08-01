# Attack Engine Architecture

This repository now separates the attack subsystem into a structured internal package while preserving the existing public API and frontend behavior.

## Attack Registry

The registry is the central lookup surface for attack definitions. It supports:

- registration of built-in or custom attack definitions
- lookup by attack ID
- lookup by category
- lookup by technique
- listing available definitions

The compatibility layer continues to expose the legacy attack objects used by the existing REST endpoints.

## Attack Library

The built-in attack payloads live in the centralized attack library. Each attack definition carries structured metadata, including:

- `attack_id`
- `name`
- `category`
- `technique`
- `severity`
- `description`
- `objectives`
- `prerequisites`
- `supported_modes`
- `variants`
- `tags`
- `version`

Variants preserve the existing prompt payloads and legacy IDs so the UI and API remain stable.

## Attack Session

Attack sessions track execution state for a single run. They record:

- `session_id`
- `attack_id`
- `status`
- timestamps
- messages
- current stage
- metadata

This provides the foundation for future multi-turn automated conversations without changing the current single-turn behavior.

### Expanded Session Model

The `AttackSession` is the central source-of-truth for an attack execution and has been expanded to include:

- `attack_variant`
- `execution_status`
- `conversation_history`
- `attacker_messages` / `victim_messages`
- `execution_events`
- `timeline`
- `metrics`
- `execution_result`
- `retry_count`

These fields are internal only and are serializable for future streaming and persistence.

## Attack Strategy

Attack strategies describe the logical stages of an attack, such as:

- reconnaissance
- trust_building
- payload_delivery
- evaluation

The abstraction exists now, but multi-step conversation orchestration is intentionally out of scope for this milestone.

### Conversation-Oriented Abstraction

Strategies are now defined around conversational progression and include canonical stages such as:

1. reconnaissance
2. trust_building
3. context_expansion
4. payload_delivery
5. adaptive_followup
6. retry_recovery
7. evaluation
8. detection

The current `SingleTurnStrategy` maps to a compact path through these stages; the abstraction allows future strategies to implement multi-turn behavior without API changes.

## Attack Executor

The enterprise executor handles:

- session creation and lifecycle updates
- prompt construction through the existing prompt builder
- response generation through the existing Ollama integration
- detection execution after a successful response

The legacy executor still returns the original attack result shape, but it now delegates to the enterprise executor internally.

### Exposed Execution Stages

The enterprise `AttackExecutor` now exposes extension points for each phase of execution while preserving `execute()`'s outward behavior:

- `initialize_session()` — create and initialize the `AttackSession`
- `prepare_strategy()` — choose/describe the strategy for the run
- `begin_execution()` — core single-turn interaction (future multi-turn orchestration will reuse this)
- `execute_stage()` — execute a named strategy stage (placeholder for future use)
- `finalize_attack()` — finalize internal state
- `generate_result()` — standardize the `AttackResult`

These hooks enable streaming per-stage events to the frontend in future milestones.

## Execution Modes

The architecture now includes a canonical `ExecutionMode` to describe how an attack should run:

- `MANUAL` — intended for human-driven interactions and manual orchestration.
- `AUTOMATED` — automated AI-driven execution (future milestone).
- `HYBRID` — mixed-mode where automation and manual control can interleave.

Each `AttackDefinition` declares `supported_execution_modes` and may include a `default_execution_mode`. The `AttackSession` stores `requested_mode`, `execution_mode`, and `active_mode` so runs can be validated and tracked. The `AttackExecutor` accepts an optional `execution_mode` and resolves a strategy according to the selected mode; for Milestone 1.1 all modes map to the existing single-turn strategy to preserve behavior. This prepares the codebase for future features such as manual step-through UIs, automated AI-vs-AI runs, and hybrid workflows without changing external APIs.

## Attack Result

Attack results are standardized internally so future modules can rely on a single structure. The result includes:

- `attack_id`
- `session_id`
- `success`
- `execution_time`
- `response`
- `detection_report`
- `telemetry`
- `metadata`

## Roadmap

Future milestones can layer on top of this foundation without changing the current REST contract:

1. multi-turn automated attack conversations
2. manual attack orchestration and pause/resume controls
3. attack chains and branching strategies
4. persistent session storage and replay
5. richer telemetry and per-stage evaluation

## Conversation Timeline & Execution Events

Two internal models were added to support future live visualization and streaming:

- **Timeline events**: timestamped, stage-aware events containing speaker, message, and metadata; stored on each `AttackSession` as `timeline`.
- **Execution events**: lightweight lifecycle events (e.g. `SessionStarted`, `StageStarted`, `StageCompleted`, `PayloadInjected`, `ConversationUpdated`, `RetryTriggered`, `DetectionStarted`, `DetectionCompleted`, `SessionFinished`) recorded in `execution_events`.

At this milestone events are recorded internally only; future milestones will stream these to the UI and enable stepwise playback and monitoring.
