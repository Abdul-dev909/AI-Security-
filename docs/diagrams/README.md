# Architecture & System Diagrams

This directory acts as the central asset repository for all visual diagrams depicting the architecture, data flows, and structures of the AI Security Assessment & Threat Intelligence Platform.

---

## Directory Scope

This folder stores and organizes diagrams across the following categories:

1. **Architecture Diagrams**: High-level structural overviews showing component layers, services, networks, and system boundaries.
2. **Sequence Diagrams**: Interaction lifecycles detailing how messages flow sequentially between the frontend, backend FastAPI handlers, database, and LLMs.
3. **Class Diagrams**: Code-level diagrams showing object classes, interfaces, attributes, and methods (e.g., memory models, agent conversation contexts).
4. **Database Diagrams**: Entity-Relationship Diagrams (ERDs) mapping SQL tables, primary/foreign keys, types, and schema relations.
5. **Deployment Diagrams**: Infrastructure layouts showing host nodes, ports, containerized services (e.g., Docker), and server connections.
6. **Flowcharts**: Logical block diagrams illustrating threat classification heuristics, guardrail routing decision trees, and attack orchestration loops.

---

## Contribution & Format Standards

To keep diagrams consistent, readable, and editable:
- **Mermaid Markdown**: Whenever possible, embed diagrams directly in documentation using fenced `mermaid` code blocks. This ensures diagrams are tracked in version control and easily editable.
- **Image Assets**: For complex drawings generated via third-party tools (e.g., Draw.io, Lucidchart, Excalidraw):
  - Save the source diagram file (e.g., `.drawio`, `.excalidraw`) alongside the exported image in this folder.
  - Export in standard vector format (`.svg`) or high-resolution raster format (`.png`).
  - Use transparent backgrounds or light themes for maximum compatibility.
- **Naming Conventions**: Use all-lowercase, underscore-separated file names describing the content type and flow. Example: `auth_flow_sequence_diagram.svg`.
