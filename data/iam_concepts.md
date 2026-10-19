# Identity and Access Management (IAM) Concepts

Identity and Access Management (IAM) is the discipline of ensuring the right people (and services) have the right access to the right resources — for the right reasons — and that access can be audited and revoked.

## Core ideas

- **Identity** — Who or what is requesting access (user, service account, device).
- **Authentication** — Proving that identity (password, passkey, certificate, MFA).
- **Authorization** — Deciding what that identity is allowed to do after authentication.
- **Accounting / audit** — Logging access decisions and actions for review.

A useful shorthand is **AAA**: Authentication, Authorization, Accounting.

## Access models

**Role-Based Access Control (RBAC)** assigns permissions to roles (e.g., "SOC Analyst"), then assigns users to roles. It scales well when job functions are stable.

**Attribute-Based Access Control (ABAC)** uses attributes (department, clearance, device health, time of day) in policies. It is more flexible and more complex to design.

**Least privilege** means granting only the minimum permissions needed for a task. **Just-in-time (JIT)** access elevates privileges temporarily and then removes them.

## Federation and SSO

Single Sign-On (SSO) lets users authenticate once and reach many apps. Federation protocols such as SAML and OpenID Connect (OIDC) exchange identity assertions between an identity provider (IdP) and service providers (SPs). Centralizing identity improves UX and lets security teams enforce MFA and disable accounts in one place.

## Common failure modes

- Shared admin accounts with no individual accountability
- Orphaned accounts after employees leave
- Over-privileged service accounts with long-lived keys
- Missing MFA on remote and privileged access
- Inconsistent offboarding from SaaS apps

## Why IAM matters in AI systems

RAG apps, model APIs, and agent tools all need identities. API keys, service accounts, and user sessions should follow the same least-privilege and audit principles as traditional systems. Treating "the chatbot" as anonymous is a security smell.
