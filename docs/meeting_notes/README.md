# Meeting Notes & Architectural Decisions

This directory contains records of engineering team meetings, design reviews, and Architecture Decision Records (ADRs) for the platform.

---

## Documenting Architecture Decisions (ADRs)

For all major architectural changes, developers must file an Architecture Decision Record (ADR). This tracks technical rationale, options considered, and downstream impacts.

### ADR File Format
- File Name: `adr_###_short_descriptive_title.md` (e.g., `adr_001_fastapi_sqlite_selection.md`)
- Location: Save inside this `docs/meeting_notes/` directory.

### ADR Template:
```markdown
# ADR [Number]: [Descriptive Title]

## Context & Problem Statement
*Describe the technical context, the challenges encountered, and what requirements need to be satisfied.*

## Decision Drivers
*What goals, constraints, or standards are driving this choice (e.g., performance, security, complexity)?*

## Options Considered
1. **Option A**: [Short summary of Option A]
   - **Pros**: List benefits
   - **Cons**: List drawback/risks
2. **Option B**: [Short summary of Option B]
   - **Pros**: List benefits
   - **Cons**: List drawback/risks

## Selected Option & Rationale
*Detail which option was selected, why it outperformed alternative proposals, and how it aligns with drivers.*

## Consequences & Downstream Impacts
*What must we look out for now? Describe changes in workflow, migration, risks, and training requirements.*
```

---

## Documenting General Meetings & Design Reviews

Standard syncs, design reviews, and sprint planning sessions should be logged to prevent alignment issues and track action items.

### Meeting Notes File Format
- File Name: `YYYY_MM_DD_meeting_topic.md` (e.g., `2026_07_19_module_3_planning.md`)

### Meeting Notes Template:
```markdown
# Meeting Notes: [Topic Name]

## Date & Attendees
- **Date**: [YYYY-MM-DD]
- **Facilitator**: [Name]
- **Attendees**: [Name 1, Name 2, ...]

## Agenda
- [x] Item 1
- [ ] Item 2

## Discussion & Key Decisions
- **Topic A**: Notes on points raised, feedback, and architectural outcomes.
- **Topic B**: Notes on points raised, feedback, and architectural outcomes.

## Action Items
| Task | Assignee | Due Date | Status |
| :--- | :--- | :--- | :--- |
| [ ] Set up basic detection routes | @developer | YYYY-MM-DD | Planned |
| [ ] Review threat model | @security | YYYY-MM-DD | In Progress |
```
