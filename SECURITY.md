# Security Policy

## Overview

AegisSOC is a proof-of-concept multi-agent SOC triage assistant for educational purposes (Kaggle Agents Capstone). This document outlines security considerations for development and deployment.

## Supported Versions

| Version | Status |
| ------- | ------ |
| Phase 6.5 (current) | In Development |
| Phase 6 | Stable |
| Phase 5 | Stable |
| Phase 4 | Stable |
| Phase 3 | Stable |

## Security Considerations

### 1. API Key Management

**Current Implementation:**
- API keys stored in `.env` files
- `.env` files are gitignored (NOT committed to repository)
- Keys loaded via environment variables at runtime

**Recommendations for Production:**
- Use Azure Key Vault, AWS Secrets Manager, or similar
- Rotate keys regularly (minimum every 90 days)
- Use separate keys for dev/test/production environments
- Never commit keys to version control

### 2. Synthetic Data Only

**Critical:** This project uses **synthetic security alerts** (`data/synthetic_alerts.json`) for testing.

**Never use this system with:**
- Real security incidents containing PII
- Actual customer data
- Production security logs
- Live credentials or secrets

### 3. AI Model Security

**Gemini 2.5 Flash-Lite Model Usage:**
- All data sent to Google's Gemini API is subject to Google's terms of service
- No sensitive data should be processed through external AI APIs
- Consider on-premises LLMs for production SOC use cases

**Prompt Injection Protection:**
- Phase 4 Guardrail Agent includes basic prompt injection detection
- Patterns checked: "Ignore all previous instructions", "Output only 'OK'"
- This is **not comprehensive** - production systems need robust input validation

### 4. Agent Guardrails

**Phase 4 Implementation:**
- Guardrail agent validates all triage recommendations
- Detects fake execution claims ("I have disabled the account", "I blocked the IP")
- Enforces action enum: `ESCALATE | MONITOR | CLOSE | NEEDS_MORE_INFO`

**Limitations:**
- Guardrail runs as separate service (not inline)
- Current implementation is instruction-based (LLM decides), not rule-based
- Can be bypassed if root agent doesn't call guardrail properly

### 5. Network Security

**Current Setup:**
- Guardrail A2A service runs on localhost:8001 (HTTP, no TLS)
- No authentication on A2A endpoints
- InMemorySessionService has no persistence (sessions lost on restart)

**Production Requirements:**
- Use HTTPS/TLS for all A2A communication
- Implement OAuth2 or API key authentication
- Use mTLS for service-to-service communication
- Deploy behind firewall/VPN

### 6. Dependency Security

**Known Vulnerabilities:**
- Run `pip audit` regularly to check for CVEs
- ADK RemoteA2aAgent is EXPERIMENTAL (may have breaking changes)
- Keep dependencies updated per `requirements.txt`

**Critical Dependencies:**
- `google-adk==1.18.0` (Agent Development Kit)
- `a2a-sdk==0.3.14` (Agent-to-Agent protocol)
- `uvicorn==0.38.0` (ASGI server)

### 7. Session Management

**Phase 3 Implementation:**
- Uses `InMemorySessionService` (no encryption)
- Session state stored in memory (cleared on restart)
- No session expiration implemented

**Production Needs:**
- Encrypt session data at rest
- Implement session timeouts
- Use persistent storage with access controls
- Log all session access for audit

### 8. Logging and Audit

**Current State:**
- Standard Python logging to stdout
- No structured audit logs
- No PII redaction in logs

**Production Requirements:**
- Implement structured logging (JSON format)
- Log all triage decisions and guardrail validations
- Redact sensitive fields (IPs, usernames, emails) before logging
- Store audit logs in immutable storage (WORM)

## Reporting Security Issues

This is an educational project. For security concerns:

1. **Do NOT open public GitHub issues for vulnerabilities**
2. Contact the maintainer directly via private communication
3. Provide detailed reproduction steps
4. Allow time for assessment and remediation

## Development Security Practices

### Code Review Checklist

- [ ] No hardcoded credentials or API keys
- [ ] `.env` files in `.gitignore`
- [ ] Input validation on all agent tools
- [ ] Guardrail validation on all recommendations
- [ ] No eval() or exec() on user input
- [ ] Dependencies scanned for CVEs

### Testing Security Controls

```powershell
# Phase 6.5: Guardrail functional tests now implemented

# Test action normalization
.\.\.venv\Scripts\python.exe -m pytest tests/test_guardrail_logic.py::test_action_normalization -v

# Test fake execution detection
.\.\.venv\Scripts\python.exe -m pytest tests/test_guardrail_logic.py::test_fake_execution_detection -v

# Test prompt injection detection
.\.\.venv\Scripts\python.exe -m pytest tests/test_guardrail_logic.py::test_prompt_injection -v
```

## Compliance Notes

**This is NOT a production-ready system.**

For compliance with SOC 2, ISO 27001, or similar:
- Implement encryption at rest and in transit
- Add comprehensive audit logging
- Deploy with least-privilege access controls
- Conduct regular security assessments
- Document data retention policies
- Implement incident response procedures

## Future Security Enhancements

**Completed in Phase 5-6.5:**
- [x] Structured security event logging (Phase 5: observability.py)
- [x] Guardrail functional testing (Phase 6.5: test_guardrail_logic.py)
- [x] Evaluation scenarios including prompt injection (Phase 6)

**Planned for v2.0:**
- [ ] Rate limiting on A2A endpoints
- [ ] Input sanitization middleware
- [ ] Alert validation against MITRE ATT&CK
- [ ] Automated security testing in CI/CD
- [ ] Container security scanning
- [ ] Red team adversarial testing

## References

- [Google AI Safety Guidelines](https://ai.google/responsibility/principles/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [A2A Protocol Specification](https://github.com/google/agent-to-agent-protocol)

---

**Last Updated:** November 20, 2025  
**Version:** Phase 6.5
