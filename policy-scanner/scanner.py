import os
import re
import yaml
from collections import defaultdict

# Get the directory of the current script (policy-scanner directory)
SCANNER_DIR = os.path.realpath(os.path.dirname(__file__))
POLICY_FILE = os.path.join(SCANNER_DIR, 'policy.yaml')
WORKFLOWS_DIR = os.path.join(os.environ['GITHUB_WORKSPACE'], '.github', 'workflows')
ACTIONS_DIR = os.path.join(os.environ['GITHUB_WORKSPACE'], '.github', 'actions')

def save_findings_to_md(findings, scanned_files):
    grouped = defaultdict(list)
    for finding in findings:
        grouped[finding['file']].append(finding)

    md_file_path = os.path.join(SCANNER_DIR, 'scan_results.md')
    with open(md_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# 🛡🔎 GHA Security Policy Scan Results\n")
        for file_path in scanned_files:
            if file_path in grouped:
                md_file.write(f"\n### 📃File: `{file_path}`\n")
                for finding in grouped[file_path]:
                    prefix = "❌ ERROR" if finding["level"] == "error" else "⚠️ WARNING"
                    md_file.write(f"\n#### {prefix}: [{finding['policy']}] {finding['description']}\n")
                    md_file.write(f"  - **Code**: {finding.get('code', 'N/A')}\n")
                    md_file.write(f"  - **Learn more**: {finding.get('url', 'N/A')}\n")
                    md_file.write(f"  - **Line**: {finding['line']}\n")
                    md_file.write(f"  - **Match**: {finding['match']}\n")
                md_file.write("\n" + "-" * 40)
            else:
                md_file.write(f"\n### ✅ No policy violations found in: `{file_path}`\n")
                md_file.write("\n" + "-" * 40)

    # Save the md file path to the environment file
    with open(os.getenv('GITHUB_ENV'), 'a') as env_file:
        env_file.write(f"MD_FILE_PATH={md_file_path}\n")

    return md_file_path


def load_policies():
    with open(POLICY_FILE, 'r') as f:
        return yaml.safe_load(f)['policies']

def scan_file(filepath, content, policies):
    findings = []
    lines = content.splitlines()
    rel_filepath = os.path.relpath(filepath, os.environ['GITHUB_WORKSPACE'])

    for name, policy in policies.items():
        description = policy.get("description", "")
        pattern = policy.get("pattern")
        missing_block = policy.get("missing_block")
        allowlist = policy.get("allowlist", [])
        exclude_files = policy.get("exclude") or []

        if rel_filepath in exclude_files:
            continue  # Skip scanning this file for this policy

        if pattern:
            regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            for lineno, line in enumerate(lines, start=1):
                match = regex.search(line)
                if match:
                    if name == "unknown-actions":
                        full_action = match.group(1)
                        org = full_action.split("/")[0]
                        if org in allowlist:
                            continue
                    if name == "gcp-legacy-auth":
                        peek_ahead = lines[lineno:lineno + 10]  # Look at next few lines
                        if not any("credentials_json" in l for l in peek_ahead):
                            continue
                    findings.append({
                        "policy": name,
                        "level": policy["level"],
                        "description": description,
                        "code": policy.get("code", ""),
                        "url": policy.get("url", ""),
                        "match": match.group(0).strip(),
                        "file": filepath,
                        "line": lineno
                    })

        if missing_block and missing_block not in content:
            findings.append({
                "policy": name,
                "level": policy["level"],
                "description": f"'{missing_block}' block is missing",
                "code": policy.get("code", ""),
                "url": policy.get("url", ""),
                "match": "-",
                "file": filepath,
                "line": "-"
            })
    return findings

def scan_directory(directory, policies):
    all_findings = []
    scanned_files = []
    for root, _, files in os.walk(directory):
        # Exclude scanning within the 'policy-scanner' directory itself
        if SCANNER_DIR in root:
            continue
        for f in files:
            if f.endswith((".yaml", ".yml")):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    findings = scan_file(path, content, policies)
                    all_findings.extend(findings)
                    scanned_files.append(path)
    return all_findings, scanned_files

def print_findings_grouped(findings, scanned_files):
    grouped = defaultdict(list)
    for finding in findings:
        grouped[finding['file']].append(finding)

    for file_path in scanned_files:
        if file_path in grouped:
            print(f"\n🔍 File: {file_path}")
            for finding in grouped[file_path]:
                prefix = "❌ ERROR" if finding["level"] == "error" else "⚠️ WARNING"
                print(f"\n{prefix}: [{finding['policy']}] {finding['description']}")
                print(f"   → Code: {finding.get('code', 'N/A')}")
                print(f"   → Learn more: {finding.get('url', 'N/A')}")
                print(f"   → Line: {finding['line']}")
                print(f"   → Match: {finding['match']}")
            print("\n" + "-" * 40)
        else:
            print(f"\n✅ No policy violations found in: {file_path}")
            print("\n" + "-" * 40)

def main():
    policies = load_policies()
    if not policies:
        print("No policies found. Exiting...")
        return

    findings, scanned_files = scan_directory(WORKFLOWS_DIR, policies)
    more_findings, more_files = scan_directory(ACTIONS_DIR, policies)

    findings.extend(more_findings)
    scanned_files.extend(more_files)

    # Save the findings to a .md file
    md_file_path = save_findings_to_md(findings,scanned_files)

    # Print findings
    print_findings_grouped(findings, scanned_files)
  
    return md_file_path

if __name__ == "__main__":
    main()
