---
name: owasp
description: "OWASP Top 10 (2021) review checklist for security-reviewer: what to look for in code review and what a pass looks like for each of the 10 categories."
---

# OWASP Top 10 (2021) Code Review Checklist

Version: 1.0 (2026-11-21)

## A01 — Broken Access Control

**What to look for:**
- Endpoints that modify or read data without checking if the authenticated user is authorised to access that specific resource (e.g. `/api/users/123` returns data for any user, not just the caller).
- Horizontal privilege escalation: can user A access user B's data by changing an ID?
- Vertical privilege escalation: can a regular user call admin endpoints?
- CORS misconfiguration: `Access-Control-Allow-Origin: *` on authenticated endpoints.
- Missing authorisation on internal routes that assume "only logged-in users call this."
- Insecure direct object references: IDs in URLs/params used without ownership check.

**Pass looks like:**
- Every data-modifying endpoint verifies `request.user.id == resource.owner_id` (or equivalent role check).
- Role-based access control applied consistently — admin routes reject non-admin tokens with 403.
- CORS configured to specific allowed origins, not wildcard on authenticated routes.

---

## A02 — Cryptographic Failures

**What to look for:**
- Sensitive data (passwords, tokens, PII, financial data) transmitted over HTTP.
- Passwords stored as plaintext or with weak hashes (MD5, SHA-1 without salt).
- Symmetric encryption keys hardcoded in source code.
- Weak or deprecated algorithms: DES, RC4, MD5, SHA-1 for security purposes.
- JWT signed with `alg: none` or a weak HS256 secret.
- TLS certificate validation disabled (`verify=False` in Python requests, `--insecure` in curl).

**Pass looks like:**
- All HTTP traffic redirects to HTTPS; TLS 1.2+ enforced.
- Passwords hashed with bcrypt, argon2, or scrypt with appropriate cost factor.
- No secrets in source code — all in secrets manager.
- JWTs signed with RS256 (asymmetric) or HS256 with a strong secret (≥ 256 bits).

---

## A03 — Injection

**What to look for:**
- SQL queries constructed with string concatenation: `"SELECT * FROM users WHERE name = '" + name + "'"`.
- NoSQL injection: user input used directly in MongoDB queries.
- Command injection: `subprocess.run("ping " + host, shell=True)` — use `shell=False` with list args.
- Template injection: user input rendered in Jinja2/similar without escaping.
- LDAP injection: user input in LDAP filter strings.
- XSS (stored/reflected): user input inserted into HTML without escaping.

**Pass looks like:**
- All SQL uses parameterised queries or ORM: `db.execute("SELECT * FROM users WHERE name = ?", [name])`.
- `subprocess.run(["ping", host], shell=False)` — never `shell=True` with user input.
- HTML output escaped with the template engine's auto-escape feature enabled.
- No raw string concatenation used to build queries or shell commands from user input.

---

## A04 — Insecure Design

**What to look for:**
- No rate limiting on sensitive endpoints (login, password reset, OTP).
- Password reset flows that leak whether an email is registered ("user not found" vs "check your email").
- Missing brute-force protection on authentication.
- Sensitive operations (e.g. delete account, transfer funds) without a secondary confirmation step.
- Business logic flaws: can a user purchase more than their credit limit? Apply the same coupon twice?

**Pass looks like:**
- Login endpoints rate-limited (e.g. 5 failed attempts → lockout or CAPTCHA).
- Password reset returns the same message whether the email exists or not.
- High-value actions require re-authentication or explicit confirmation.
- Business rules enforced server-side, not just client-side.

---

## A05 — Security Misconfiguration

**What to look for:**
- Debug mode enabled in production (`DEBUG=True` in Django, `NODE_ENV=development`).
- Default credentials not changed (admin/admin, root/root).
- Verbose error messages that expose stack traces or internal paths to end users.
- Unused features or services enabled (directory listing, unused API endpoints).
- HTTP security headers missing: `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Strict-Transport-Security`.
- Cloud storage buckets or databases publicly accessible.

**Pass looks like:**
- `DEBUG=False` (or equivalent) for production builds.
- Error responses return generic messages; full errors logged server-side only.
- Security headers present on all responses.
- No default credentials; all secrets rotated from defaults.

---

## A06 — Vulnerable and Outdated Components

**What to look for:**
- Dependencies with known CVEs in `requirements.txt` / `package.json` / `pom.xml`.
- Unpinned dependencies (`requests>=2.0` vs `requests==2.31.0`).
- Base Docker image using an old OS version with unpatched packages.
- End-of-life runtime versions (e.g. Python 3.8, Node 16).

**Pass looks like:**
- `pip audit` (Python) or `npm audit` (Node) returns no Critical/High CVEs.
- Trivy or docker scout scan of the container image returns no Critical CVEs.
- Dependencies pinned to specific versions; automated dependency update bot in place (Dependabot/Renovate).

---

## A07 — Identification and Authentication Failures

**What to look for:**
- Weak password policy: allows "password123" or single-character passwords.
- Session tokens not invalidated on logout.
- Session tokens with excessively long expiry (> 24h for web apps without refresh token rotation).
- JWT secret is weak or hardcoded (`secret`, `changeme`).
- No MFA available for privileged accounts.
- Credential stuffing protection absent (no rate limiting, no account lockout).

**Pass looks like:**
- Minimum password length ≥ 12 chars; common password list checked.
- Logout invalidates the session/token server-side (for JWTs: use short expiry + refresh token rotation).
- JWT secret is ≥ 256 bits and stored in secrets manager.
- MFA available (required for admin).
- Failed login attempts rate-limited.

---

## A08 — Software and Data Integrity Failures

**What to look for:**
- Dependencies installed without integrity checks (no lockfile; `pip install` without `--require-hashes`).
- CI/CD pipeline allows arbitrary code injection via PR comments or environment variables.
- Auto-update mechanisms that fetch and execute code without signature verification.
- Insecure deserialisation: `pickle.loads(user_data)`, `yaml.load(data)` (without `Loader=yaml.SafeLoader`).

**Pass looks like:**
- `package-lock.json` or `poetry.lock` committed and used in CI (`npm ci` not `npm install`).
- CI/CD uses pinned action versions (`actions/checkout@v4` not `actions/checkout@latest`).
- `yaml.safe_load()` used everywhere (never bare `yaml.load()`).
- No deserialisation of untrusted data with pickle or equivalent.

---

## A09 — Security Logging and Monitoring Failures

**What to look for:**
- No logging of authentication events (login, logout, failed attempts).
- Sensitive data (passwords, tokens, PII) included in log output.
- Logs written only to local files with no centralised aggregation.
- No alerting on anomalous patterns (many failed logins, privilege escalation attempts).
- Log injection: user input included in log messages without sanitisation (can corrupt logs).

**Pass looks like:**
- Auth events (success and failure), access control failures, and admin actions all logged.
- No PII or credentials in log output.
- Logs shipped to centralised system (CloudWatch, Azure Monitor, Cloud Logging).
- Alert configured for repeated failed authentication.

---

## A10 — Server-Side Request Forgery (SSRF)

**What to look for:**
- Code that makes HTTP requests to a URL supplied by the user: `requests.get(user_provided_url)`.
- Webhook receivers that fetch a URL from the payload without validation.
- Image upload features that accept a URL and fetch the image server-side.
- Any feature that resolves user-supplied hostnames.

**Pass looks like:**
- User-supplied URLs validated against an allowlist of permitted domains/schemes.
- Outbound HTTP calls blocked to `169.254.169.254` (AWS metadata), `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, and `localhost`.
- Redirect following disabled or strictly controlled.
- If webhooks are required: use a dedicated outbound proxy with allowlist enforcement.

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
