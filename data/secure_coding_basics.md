# Secure Coding Basics for AI Apps

AI demos often skip security. Portfolio projects should still show you know the basics — especially if your background is cybersecurity.

## Input trust boundaries

Treat all user input as untrusted: chat prompts, uploaded files, URLs, and tool arguments. Validate types and length. Do not pass raw user text into shell commands or SQL.

For RAG systems specifically:

- Sanitize or constrain filenames and paths used at ingest time
- Do not auto-fetch arbitrary URLs from user questions without allowlists
- Separate system instructions from retrieved document text so documents cannot easily override policy (prompt injection awareness)

## Secrets and keys

Never commit API keys, tokens, or `.env` files. Use environment variables and `.gitignore`. Rotate keys if they leak. Prefer local/offline models for demos when a free API is not required.

## Dependency hygiene

Pin versions in `requirements.txt`. Be cautious with packages that execute code at install time. Keep the attack surface small: fewer dependencies means fewer supply-chain surprises.

## Logging and PII

Log enough to debug (query latency, retrieval scores) but avoid logging raw secrets or sensitive personal data. If your corpus might contain PII, document that risk and keep demos on synthetic/educational text.

## Auth around demos

A public Gradio share link is convenient and dangerous. For portfolio demos, prefer local `127.0.0.1` or add basic auth if you must expose a URL. Rate-limit if an endpoint can burn paid API credits.

## Takeaway

Secure coding for AI is mostly classical engineering: least privilege, validate inputs, protect secrets, and assume retrieved text may be adversarial. That mindset is a differentiator when combined with solid ML work.
