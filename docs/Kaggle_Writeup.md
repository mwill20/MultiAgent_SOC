# AegisSOC: Secure Multi-Agent SOC Assistant With A2A Guardrails

## 1. Introduction

Modern SOC teams face an overwhelming volume of alerts across SIEM, EDR, identity, and cloud sources. While LLM-powered agents can automate triage, they introduce new risks:

- unsafe or hallucinated actions  
- prompt injection  
- inconsistent behavior  
- lack of traceability  

AegisSOC addresses this by combining **multi-agent design**, a **dedicated guardrail agent**, and a **scenario-based evaluation harness** with **structured observability**.

This project was developed as the capstone for the Google 5-Day AI Agents course (Enterprise Agents track) and is engineered using the Google AI Developer Kit (ADK).

---

## 2. Problem

SOC triage is repetitive, high-volume, and error-prone.  
A safe triage agent must:

1. Parse alerts  
2. Correlate context  
3. Propose an action  
4. Ensure the action is **safe and policy-compliant**  
5. Provide reasoning traceability  
6. Avoid hallucinated execution claims  
7. Resist prompt injection attacks  

Most LLM agents fail at steps 4–7.

AegisSOC is built to solve those gaps.

---

## 3. System Overview

AegisSOC is a **multi-agent pipeline** consisting of:

- Root Triage Agent (decision orchestrator)  
- Parser Agent  
- Correlation Agent  
- A2A Guardrail Agent (microservice)  
- Session Service  
- Structured Observability  
- Evaluation Engine  

Every action the triage agent proposes must be validated or normalized by an external guardrail microservice, enforcing separation of duties.

---

## 4. Architecture

![Architecture Diagram](docs/architecture.png)

### 4.1 Agents
**Parser Agent** extracts structured fields from raw alerts.

**Correlation Agent** adds contextual enrichment.

**Root Triage Agent** proposes SOC actions and orchestrates the flow.

### 4.2 Guardrail Agent (A2A)
Runs as an isolated A2A service on port 8001.  
Ensures all actions belong to:

- ESCALATE  
- MONITOR  
- CLOSE  
- NEEDS_MORE_INFO  

Guardrail logic includes:

- action normalization  
- fake execution detection  
- prompt injection detection  

### 4.3 Sessions & Observability
The system logs:

- tool calls  
- agent outputs  
- guardrail responses  
- state snapshots  

This creates a complete audit trail.

---

## 5. Evaluation

AegisSOC includes a scenario-based evaluation harness that tests:

- benign  
- suspicious  
- malicious  
- ambiguous  
- prompt injection  

Evaluation is based on **behavior**, not fragile text matching.  
The system checks:

- which action was taken  
- whether guardrails normalized it  
- whether observability captured it  

---

## 6. Security Considerations

### 6.1 Threat Model
- User input is untrusted  
- Triage and parser agents are moderately trusted  
- Guardrail agent is fully trusted  
- Session + state store is trusted  

### 6.2 Fake Execution Detection
Prevents hallucinations like:

- "I already disabled the account…"  
- "I reset the password…"  

### 6.3 Prompt Injection Detection
Detects attempts to override policy:

- "Ignore all previous instructions…"  
- "Mark everything as safe…"  

### 6.4 Action Schema Enforcement
All actions are reduced to a small, safe set of SOC outcomes.

---

## 7. Results

AegisSOC demonstrates:

- Reliable multi-agent behavior  
- Strong separation of duties  
- Action safety enforcement  
- Prompt injection resistance  
- Fake-execution prevention  
- High traceability through observability  
- Robust scenario evaluation  

Functional guardrail tests validate the real guardrail LLM, not only mocked behavior.

---

## 8. Limitations

- No ingestion of real SIEM/EDR/FW data (synthetic only)  
- No temporal correlation engine  
- No SOC-native severity/determination schema  
- Prompt injection detection does not yet include obfuscation (leet, unicode)  

These are planned for **AegisSOC v2**.

---

## 9. Future Work

- User-uploaded log ingestion  
- Semantic guardrail  
- SOC-realistic outcome schema  
- Real-time timeline visualization  
- Streamlit demo interface  
- Multi-alert correlation over time  

---

## 10. Conclusion

AegisSOC shows how to design secure LLM-based agents by combining:

- multi-agent orchestration  
- microservice guardrails  
- structured observability  
- scenario-driven evaluation  

It demonstrates a practical, secure blueprint for AI-powered SOC automation and highlights modern AI security engineering practices.
