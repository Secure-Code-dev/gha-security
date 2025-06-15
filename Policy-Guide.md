# GitHub Actions Security Policies: Detailed Guide

This guide explains common GitHub Actions security policies with comprehensive details, insecure usage examples, and step-by-step remediation instructions. It also describes the vulnerabilities each bad practice can expose, to help you better understand the risk landscape.

---

## GHA-SEC001: Plaintext Secrets

### ❗ Problem
Secrets should not be printed to logs or echoed in a way that exposes them. Logs are often accessible to users and secrets could be compromised.

### 🔍 Vulnerability
**Exposure of credentials** — If a secret is printed to the console output, it can be harvested by insiders, attackers monitoring logs, or even by external contributors in public repositories. Secrets like API keys, tokens, or database passwords can then be used to gain unauthorized access.

### 🚫 Insecure Example
```yaml
- run: echo "${{ secrets.MY_SECRET }}"
```

### ✅ Secure Example
```yaml
- run: some_command --token "${{ secrets.MY_SECRET }}"
```

### 🛠️ Remediation
- Never log secrets directly.
- Use secrets only in commands where they are essential.
- Ensure the command or tool used does not print the secret accidentally.

---

## GHA-SEC002: Untrusted Input in Shell Commands

### ❗ Problem
GitHub events such as pull request titles, issue bodies, etc., can be manipulated by attackers. Using them in shell commands without sanitization can lead to injection vulnerabilities.

### 🔍 Vulnerability
**Shell Injection Attacks** — Attackers can inject malicious payloads (e.g., shell commands, scripts) via untrusted fields like PR titles. This can lead to arbitrary code execution within the GitHub runner environment.

### 🚫 Insecure Example
```yaml
- run: echo "${{ github.event.pull_request.title }}"
```

### ✅ Secure Example
```yaml
- run: |
    title="${{ github.event.pull_request.title }}"
    echo "Received title"
```

### 🛠️ Remediation
- Assign untrusted inputs to local variables.
- Avoid using direct command interpolation.
- Validate and sanitize inputs wherever possible.

---

## GHA-SEC003: Minimally Scoped Credentials

### ❗ Problem
By default, the `GITHUB_TOKEN` is granted all permissions. Overprivileged tokens increase the attack surface.

### 🔍 Vulnerability
**Privilege Escalation and Unauthorized Actions** — If a token with broad access is compromised, attackers can push code, create releases, modify workflows, or access sensitive repository information.

### 🚫 Insecure Example
```yaml
# No permissions block
```

### ✅ Secure Example
```yaml
permissions:
  contents: read
  issues: write
```

### 🛠️ Remediation
- Explicitly define the minimum required permissions in each workflow.
- Start with zero permissions and incrementally add only necessary ones.

---

## GHA-SEC004: Unknown Actions

### ❗ Problem
Third-party actions may be malicious or compromised. Using actions from unknown sources increases risk.

### 🔍 Vulnerability
**Supply Chain Attacks** — Attackers can introduce backdoors or malicious scripts into open-source actions, leading to credential theft, unauthorized code execution, or data exfiltration.

### 🚫 Insecure Example
```yaml
- uses: some-user/unknown-action@v1
```

### ✅ Secure Example
```yaml
- uses: actions/checkout@v4
```

### 🛠️ Remediation
- Use actions from trusted sources (`actions`, `github`, internally audited ones).
- Maintain an `allowlist` in the `policy.yaml` for safe third-party actions in your organization.

---

## GHA-SEC005: Non-specific Version Tags

### ❗ Problem
Using version tags like `@v1` or `@main` can lead to unexpected changes if the action is updated.

### 🔍 Vulnerability
**Unexpected Behavior or Compromise** — If an action author updates the version tag with malicious changes, your workflows could automatically pull the malicious update without any notice.

### 🚫 Insecure Example
```yaml
- uses: actions/setup-node@v1
or
- uses: actions/setup-node@latest
or
- uses: actionis/setup-node@main
```

### ✅ Secure Example
```yaml
- uses: actions/setup-node@v1.4.2
or
-uses: actions/setup-node@<commit-SHA>
```

### 🛠️ Remediation
- Pin actions to specific semantic versions or commit SHAs.

---

## GHA-SEC006: Self-hosted Runners

### ❗ Problem
Self-hosted runners can be compromised if exposed to untrusted code, especially in public repositories.

### 🔍 Vulnerability
**Runner Takeover and Persistence** — Attackers could run code that installs backdoors, modifies runners, or escalates to broader infrastructure compromise.

### 🚫 Insecure Example
```yaml
runs-on: [self-hosted]
```

### ✅ Secure Example
```yaml
runs-on: ubuntu-latest
```

### 🛠️ Remediation
- Use GitHub-hosted runners for public workflows.
- Restrict self-hosted runner access to trusted repositories only.

---

## GHA-SEC007: `pull_request_target` and External SHA

### ❗ Problem
The `pull_request_target` event runs with write permissions on the base repo but can checkout attacker-controlled code.

### 🔍 Vulnerability
**Repository Compromise** — An attacker could create a PR with malicious code, which, if checked out insecurely, could be executed with elevated permissions.

### 🚫 Insecure Example
```yaml
on: pull_request_target
jobs:
  test:
    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}
```

### ✅ Secure Example
```yaml
on: pull_request
```

### 🛠️ Remediation
- Use `pull_request` instead of `pull_request_target` for untrusted contributions.

---

## GHA-SEC008: Artifact Uploads with Sensitive Files

### ❗ Problem
Sensitive files like `.env`, `.pem`, or private keys should not be uploaded as artifacts.

### 🔍 Vulnerability
**Secret Leakage via Artifacts** — Uploaded artifacts may be accessible to unauthorized users or automated systems, exposing critical secrets.

### 🚫 Insecure Example
```yaml
- uses: actions/upload-artifact@v3
  with:
    path: .env
```

### ✅ Secure Example
```yaml
- uses: actions/upload-artifact@v3
  with:
    path: logs/output.txt
```

### 🛠️ Remediation
- Audit uploaded artifacts regularly.
- Exclude sensitive files from uploads.

---

## GHA-SEC009: Missing Checksum for Downloads

### ❗ Problem
Downloaded scripts or binaries should be validated to ensure integrity.

### 🔍 Vulnerability
**Remote Code Execution** — If an attacker modifies a downloaded script, and the checksum is not verified, arbitrary malicious code could be executed in your CI environment.

### 🚫 Insecure Example
```yaml
- run: curl -sSL http://example.com/script.sh | bash
```

### ✅ Secure Example
```yaml
- run: |
    curl -sSL -o script.sh http://example.com/script.sh
    echo "abcd1234  script.sh" | sha256sum -c -
    bash script.sh
```

### 🛠️ Remediation
- Validate all downloads before execution using SHA256 or GPG signatures.

---

## GHA-SEC010: Secrets in Global `env:`

### ❗ Problem
Secrets should be scoped to steps. Using them globally increases exposure.

### 🔍 Vulnerability
**Increased Secret Exposure** — Secrets available globally can be accidentally leaked if printed or used in any other untrusted step.

### 🚫 Insecure Example
```yaml
env:
  SECRET_TOKEN: ${{ secrets.MY_SECRET }}
```

### ✅ Secure Example
```yaml
- run: ./script.sh
  env:
    SECRET_TOKEN: ${{ secrets.MY_SECRET }}
```

### 🛠️ Remediation
- Always scope secrets at the minimal necessary level (preferably individual steps).

---

## GHA-SEC011: Auto-Approve Pull Requests

### ❗ Problem
Automating approval can allow malicious changes to be merged without human oversight.

### 🔍 Vulnerability
**Unauthorized Code Merge** — Malicious PRs could be auto-approved and merged, leading to supply chain attacks, credential leaks, or infrastructure damage.

### 🚫 Insecure Example
```yaml
- run: gh pr review --approve
```

### ✅ Secure Example
```yaml
# Use manual review from maintainers
```

### 🛠️ Remediation
- Always require human review, even if PRs come from trusted contributors.

---

## GHA-SEC012: `continue-on-error: true`

### ❗ Problem
Using `continue-on-error: true` hides failures, leading to false positives.

### 🔍 Vulnerability
**Silent Failures and Insecure Builds** — Failures in critical security checks, test cases, or build steps might be ignored, resulting in insecure or broken deployments.

### 🚫 Insecure Example
```yaml
- run: make test
  continue-on-error: true
```

### ✅ Secure Example
```yaml
- run: make test
  continue-on-error: false
```

### 🛠️ Remediation
- Use `continue-on-error` cautiously, only when failure is acceptable.
- Prefer explicit conditional logic (`if: failure()`).

---

## GHA-SEC013: Deprecated `set-output` Command

### ❗ Problem
The `::set-output` command is deprecated and less secure.

### 🔍 Vulnerability
**Output Injection** — Deprecated commands like `::set-output` can be vulnerable to unexpected input parsing issues and injection attacks.

### 🚫 Insecure Example
```yaml
- run: echo "::set-output name=version::1.0"
```

### ✅ Secure Example
```yaml
- run: echo "version=1.0" >> "$GITHUB_OUTPUT"
```

### 🛠️ Remediation
- Migrate to the modern `$GITHUB_OUTPUT` method for all workflows.

---
## GHA-SEC014: Use of Legacy GCP Authentication 

### ❗ Problem
Using credentials_json for authentication with Google Cloud is a legacy method that involves managing long-lived secrets, which is less secure.

### 🔍 Vulnerability
**Secret Leakage Risk** — Embedding static service account keys like credentials_json increases the risk of accidental leakage, misuse, or unauthorized access if the key is exposed in the CI/CD pipeline or version control.

### 🚫 Insecure Example
```yaml
- name: Authenticate with GCP
  id: 'auth'
  uses: 'google-github-actions/auth@v2'
  with:
    credentials_json: '<YOUR-SERVICE-ACCOUNT-FILE-AS-INPUT>'
```

### ✅ Secure Example
```yaml
- name: Authenticate to GCP
  uses: google-github-actions/auth@v2
  with:
    token_format: 'access_token'
    workload_identity_provider: '<YOUR-WORKFLOW-IDENTITY-PROVIDER>'
    service_account: '<SERVICE-ACCOUNT>'
```

### 🛠️ Remediation
- Stop using credentials_json for authentication.
- Set up a [Workload Identity Federation provider](https://cloud.google.com/iam/docs/workload-identity-federation) in your GCP project.
- This enables short-lived, automatically rotated tokens without needing long-lived secrets.

---

📌 **Additional Note:** 
Each policy rule in `policy.yaml` supports an `exclude` parameter. If you want to intentionally allow a specific workflow or action to violate a policy (for example, due to justified exceptions), you can list the workflow or action path under the `exclude` field.

**Example:**
```yaml
policies:
  minimally-scoped-credentials:
      code: GHA-SEC003
      level: warning
      description: "Workflow is missing 'permissions' block"
      missing_block: permissions
      exclude:
        - .github/workflows/new-changes.yaml
```
In the above example, the `legacy-deploy.yml` workflow will be excluded from the "Non-specific Version Tags" (GHA-SEC005) policy check during scanning.

---

> 📌 **Important**: Regularly audit workflows for these patterns. Keep up-to-date with GitHub Actions [Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions).
