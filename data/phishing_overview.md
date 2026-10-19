# Phishing Overview

Phishing is a social-engineering attack where an adversary tricks a person into revealing credentials, installing malware, or transferring money by impersonating a trusted party. Email is the classic channel, but phishing also appears in SMS (smishing), voice calls (vishing), and chat apps.

## Common patterns

- **Urgency and fear** — "Your account will be locked in 24 hours."
- **Authority** — Messages that look like they come from IT, a bank, or a manager.
- **Lookalike domains** — `rnicrosoft.com` instead of `microsoft.com`, or extra subdomains.
- **Unexpected attachments or links** — Especially `.html`, `.zip`, or shortened URLs.
- **Credential harvesting pages** — Fake login forms that forward passwords to the attacker.

Spear phishing targets a specific person or role with researched details. Business Email Compromise (BEC) often skips malware and instead spoofs or hijacks executive email to request wire transfers.

## Defenses (layered)

1. **User awareness** — Training that teaches people to pause, verify, and report.
2. **Email security** — SPF, DKIM, DMARC; attachment sandboxing; URL rewriting.
3. **MFA** — Multi-factor authentication reduces the value of stolen passwords (not a silver bullet against session theft or MFA fatigue).
4. **Reporting paths** — Easy "Report Phish" buttons and a clear SOC triage process.
5. **Least privilege** — Limit what a compromised account can reach.

## Detection signals

Unusual sender domains, mismatched display names, first-time senders requesting money, and links that resolve to recently registered domains are common indicators. Automated classifiers (including TF-IDF or transformer models on message text) can triage bulk mail, but humans still matter for novel campaigns.

## Key takeaway

Phishing succeeds because it attacks trust and attention, not only software bugs. Technical controls and human process both belong in the Protect and Detect functions of a security program.
