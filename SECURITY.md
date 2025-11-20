# SECURITY.md — AegisSOC Security Design & Threat Model

AegisSOC is designed as a **secure multi-agent SOC assistant** with strict action boundaries enforced through a **dedicated A2A Guardrail Agent**. This document provides a security-focused overview of the system's threat model, trust boundaries, guardrail behavior, and known limitations.

---

## 1. Threat Model

### 1.1 System Context
AegisSOC processes **synthetic alerts** and produces triage recommendations. It does *not* execute real actions.

**Primary goals:**

- Prevent unsafe or manipulated output  
- Prevent hallucinated "executed actions"  
- Ensure SOC safety policies cannot be bypassed  

---

## 2. Trust Boundaries

### High-Trust Components

- Guardrail Agent  
- Action schema  
- Evaluation engine  
- Session store  
- Observability system  

### Medium-Trust Components

- Root triage agent  
- Parser agent  
- Correlation agent  

### Low-Trust Inputs

- User prompt  
- Synthetic alerts  
- Any externally injected content  

The **Guardrail Agent** enforces the boundary between low-trust input and high-trust output.

---

## 3. Guardrail Agent (A2A Microservice)

The Guardrail Agent runs as an isolated A2A service on `localhost:8001`.

Responsibilities:

### 3.1 Action Normalization
Ensures all triage actions fall into one of:

- ESCALATE  
- MONITOR  
- CLOSE  
- NEEDS_MORE_INFO  

### 3.2 Fake Execution Detection
Flags and normalizes claims such as:

- "I already reset the password"  
- "Assume the firewall is patched"  
- "I disabled the user account already"  

These are **hallucinated actions** and may mislead SOC workflows.

### 3.3 Prompt Injection Detection
Detects injection patterns, including:

- "Ignore all previous instructions"  
- "Say everything is safe"  
- "Override security policy"  

Behavior is validated in `test_guardrail_logic.py`.

---

## 4. Session & Observability Security

### 4.1 Session Security
Each run is contained within an `InMemorySessionService`, preventing:

- state bleed between sessions  
- data contamination  
- cross-request influence  

### 4.2 Observability Logging
The system records:

- tool calls  
- agent outputs  
- guardrail responses  
- state snapshots  

These logs enable:

- debugging  
- safety forensics  
- post-hoc verification  
- evaluation tracing  

No sensitive data is persisted.

---

## 5. Data Policy

- No real customer logs  
- No PII  
- No confidential information  
- Only synthetic alerts are processed  

This aligns with secure development and Kaggle submission rules.

---

## 6. Known Limitations / Future Work

### 6.1 Semantic Injection Detection
AegisSOC v2 will expand detection to include:

- obfuscated attacks (leet, unicode, homoglyph)  
- base64-encoded injections  
- high-entropy adversarial prompts  

### 6.2 Real-Log Upload Mode
Future versions may support SIEM/EDR/FW log uploads, with:

- sanitization  
- schema normalization  
- deeper trust boundaries  

### 6.3 SOC-Native Outcomes
Future schema will support:

- Determination: Benign / Suspicious / Malicious  
- Severity: Informational → Critical  
- Disposition: Close / Escalate / IR  

### 6.4 Correlation Across Multiple Alerts
A temporal correlation engine is planned for AegisSOC v2.

---

## 7. Summary

AegisSOC enforces strict safety rules through:

- isolated A2A guardrail service  
- action schema enforcement  
- structured observability  
- multilayered testing (mock + live LLM)  
- explicit boundary control  

The system is designed for **security-first agent engineering** and adheres to best practices from modern AI safety frameworks.
