# Project Roadmap

This document outlines the milestones, execution phases, and module statuses for the AI Security Assessment & Threat Intelligence Platform.

---

## High-Level Status Overview

| Phase | Milestone Focus | Target Modules | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Foundation & Attack Simulation | Module 1, Module 2, Basic Frontend | **Completed** |
| **Phase 2** | Real-Time Detection & Audit Logging | Module 3, Module 4 | **In Progress** |
| **Phase 3** | Post-Incident Analytics & Intelligence | Module 5, Module 6 | **Planned** |
| **Phase 4** | Advanced Models & Security Hub | Module 7, Module 8, Module 9, Module 10 | **Planned** |

---

## Detailed Milestone Execution

### Phase 1: Foundation & Attack Simulation
Focuses on creating the target environment, the offensive framework to evaluate target security, and the visual workspace for engineers.

- [x] **Module 1: Vulnerable AI Agent**  
  *Status: `Completed`*  
  Simulated autonomous LLM agent exposing prompt injections, jailbreaks, and sensitive data handling vulnerabilities. Includes local Ollama LLM client integration and conversation persistence.
- [x] **Module 2: Automated Attack Engine**  
  *Status: `Completed`*  
  Automated attack execution library and endpoint layer, capable of systematically driving payloads against target agents.
- [x] **Basic Frontend (Vite + React)**  
  *Status: `Completed`*  
  Initial React dashboard containing collapsing menus, conversation terminals, attack simulators, system metric logs, and status dashboards.

---

### Phase 2: Real-Time Detection & Audit Logging
*Current active focus. Preparing to begin Module 3 (Detection Engine).*

- [/] **Module 3: Detection Engine**  
  *Status: `In Progress`*  
  Integrate scanning pipelines, heuristic/pattern rules, and vector-based guardrails monitoring agent outputs/inputs in real time.
- [ ] **Module 4: Evidence Collection**  
  *Status: `Planned`*  
  Implement low-overhead, tamper-resistant data capture, logging chat messages, metadata states, model responses, and trace parameters.

---

### Phase 3: Post-Incident Analytics & Intelligence
Focuses on investigating compromises and indexing threat actions into searchable databases.

- [ ] **Module 5: Digital Forensics**  
  *Status: `Planned`*  
  Post-incident toolset to compile time-series logs, trace execution paths of jailbreak attempts, and reconstruct security compromise timelines.
- [ ] **Module 6: Attack Intelligence Database**  
  *Status: `Planned`*  
  Central repository for caching, formatting, and indexing historical threat intelligence, known CVEs, and unique local model failures.

---

### Phase 4: Advanced Models & Security Hub
Focuses on intelligence correlation, automated risk metrics, proactive scanning, and central control dashboards.

- [ ] **Module 7: Similarity Analysis**  
  *Status: `Planned`*  
  Vector embeddings/semantic search pipeline matching new attack vectors with existing logs in the Attack Intelligence Database.
- [ ] **Module 8: Risk Prediction**  
  *Status: `Planned`*  
  Machine learning modules predicting compromise probability based on telemetry data, active system settings, and model history.
- [ ] **Module 9: Threat Hunting**  
  *Status: `Planned`*  
  Query dashboard allowing engineers to proactively search logs for latent security anomalies or dormant adversarial strategies.
- [ ] **Module 10: Security Dashboard**  
  *Status: `Planned`*  
  Premium monitoring dashboard integrating charts, maps, settings, telemetry, and automated security controls.
