#!/usr/bin/env python3
"""
validate-report.py — Deterministic R&M Report Validator (v1.9)

Validates a generated Reliability & Maintainability report against the
SonarQube standards JSON file. Performs three checks:
  1. Rule ID existence (V-01)
  2. Severity accuracy (V-02)
  3. Quality Gate recalculation (V-04)

Usage:
  python3 .kiro/scripts/validate-report.py <report.md> [--rules sonarqube_rules.json]

Output:
  - Prints validation results to stdout
  - Writes corrected report to <report>_validated.md if issues found
  - Exit code: 0 = all valid, 1 = corrections made, 2 = error
"""

import json
import re
import sys
import os
from pathlib import Path


def load_rules(rules_path):
    """Load SonarQube rules JSON into a lookup dict: rule_key -> {title, severity}"""
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules_list = json.load(f)

    lookup = {}
    for rule in rules_list:
        key = rule.get('rule_key', '')
        lookup[key] = {
            'title': rule.get('title', ''),
            'severity': rule.get('severity', ''),
        }
    return lookup


def map_severity(standards_severity):
    """Map standards file severity to report severity label."""
    mapping = {
        'Blocker': 'CRITICAL',
        'Critical': 'CRITICAL',
        'High': 'HIGH',
        'Medium': 'MEDIUM',
        'Low': 'LOW',
    }
    return mapping.get(standards_severity, standards_severity.upper())


def extract_findings(report_text):
    """Extract findings from report markdown. Returns list of dicts."""
    findings = []

    pattern = re.compile(
        r'###\s+(BUG-\d+)\s*[—:\-]+\s*(.+?)(?=\n)',
        re.MULTILINE
    )

    for match in pattern.finditer(report_text):
        finding_id = match.group(1)
        title = match.group(2).strip()
        start_pos = match.start()

        section_text = report_text[start_pos:start_pos + 3000]

        rule_match = re.search(
            r'\*\*Rule\*\*:\s*`?([a-z]+:S\d+)`?\s*[—\-]+\s*(.+?)(?:\n|$)',
            section_text
        )

        severity_match = re.search(
            r'\*\*Risk Level\*\*:\s*(CRITICAL|Critical|HIGH|High|MEDIUM|Medium|LOW|Low)',
            section_text
        )

        priority_match = re.search(
            r'\*\*Fix Priority\*\*:\s*(P[0-3])',
            section_text
        )

        raw_severity = severity_match.group(1) if severity_match else None
        normalized_severity = raw_severity.upper() if raw_severity else None

        findings.append({
            'id': finding_id,
            'title': title,
            'rule_id': rule_match.group(1) if rule_match else None,
            'rule_desc': rule_match.group(2).strip() if rule_match else None,
            'severity': normalized_severity,
            'priority': priority_match.group(1) if priority_match else None,
            'position': start_pos,
        })

    return findings


def validate_findings(findings, rules_lookup):
    """Validate all findings against the rules lookup. Returns issues list."""
    issues = []

    for f in findings:
        rule_id = f['rule_id']
        if not rule_id:
            issues.append({
                'finding': f['id'],
                'check': 'V-00',
                'issue': 'No rule ID found in finding',
                'action': 'Move to Appendix',
            })
            continue

        # V-01: Rule existence
        if rule_id not in rules_lookup:
            issues.append({
                'finding': f['id'],
                'check': 'V-01',
                'issue': f'Rule {rule_id} does not exist in standards',
                'action': 'Move to Appendix',
                'rule_id': rule_id,
            })
            continue

        # V-02: Severity check
        expected_severity = map_severity(rules_lookup[rule_id]['severity'])
        if f['severity'] and f['severity'] != expected_severity:
            issues.append({
                'finding': f['id'],
                'check': 'V-02',
                'issue': f'{rule_id} severity is {f["severity"]}, should be {expected_severity}',
                'action': f'Correct to {expected_severity}',
                'rule_id': rule_id,
                'expected': expected_severity,
                'actual': f['severity'],
            })

        # V-03: Title check (fuzzy — flag if completely different)
        if f['rule_desc'] and rule_id in rules_lookup:
            expected_title = rules_lookup[rule_id]['title'].lower()
            actual_desc = f['rule_desc'].lower()
            # Check if key words from the title appear in the description
            title_words = set(w for w in expected_title.split() if len(w) > 3)
            desc_words = set(w for w in actual_desc.split() if len(w) > 3)
            if title_words and len(title_words & desc_words) / len(title_words) < 0.3:
                issues.append({
                    'finding': f['id'],
                    'check': 'V-03',
                    'issue': f'{rule_id} description mismatch. Expected: "{rules_lookup[rule_id]["title"]}"',
                    'action': 'Move to Appendix (wrong rule for finding)',
                    'rule_id': rule_id,
                })

    return issues


def compute_quality_gate(findings, invalid_finding_ids):
    """Compute quality gate from valid findings only."""
    critical_count = 0
    high_p0_count = 0
    high_other_count = 0
    medium_count = 0

    for f in findings:
        if f['id'] in invalid_finding_ids:
            continue

        sev = f['severity']
        pri = f['priority']

        if sev == 'CRITICAL':
            critical_count += 1
        elif sev == 'HIGH':
            if pri == 'P0':
                high_p0_count += 1
            else:
                high_other_count += 1
        elif sev == 'MEDIUM':
            medium_count += 1

    gate_pass = (critical_count == 0) and (high_p0_count == 0)

    return {
        'status': 'PASS' if gate_pass else 'FAIL',
        'critical': critical_count,
        'high_p0': high_p0_count,
        'high_other': high_other_count,
        'medium': medium_count,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-report.py <report.md> [--rules sonarqube_rules.json]")
        sys.exit(2)

    report_path = sys.argv[1]

    # Find rules file
    rules_path = None
    if '--rules' in sys.argv:
        idx = sys.argv.index('--rules')
        if idx + 1 < len(sys.argv):
            rules_path = sys.argv[idx + 1]

    if not rules_path:
        # Auto-detect: look for sonarqube_rules.json in common locations
        candidates = [
            'sonarqube_rules.json',
            '.kiro/rules/sonarqube_rules.json',
            '../sonarqube_rules.json',
        ]
        script_dir = Path(__file__).parent.parent.parent
        candidates.append(str(script_dir / 'sonarqube_rules.json'))

        for c in candidates:
            if os.path.exists(c):
                rules_path = c
                break

    if not rules_path or not os.path.exists(rules_path):
        print("ERROR: Cannot find sonarqube_rules.json. Use --rules flag.")
        sys.exit(2)

    if not os.path.exists(report_path):
        print(f"ERROR: Report file not found: {report_path}")
        sys.exit(2)

    # Load data
    rules_lookup = load_rules(rules_path)
    with open(report_path, 'r', encoding='utf-8') as f:
        report_text = f.read()

    # Extract and validate
    findings = extract_findings(report_text)

    if not findings:
        print("WARNING: No findings extracted from report.")
        print("(Report may use a different format or has no BUG-XX findings)")
        sys.exit(0)

    issues = validate_findings(findings, rules_lookup)

    # Compute sets
    invalid_ids = set()
    for issue in issues:
        if issue['action'].startswith('Move to Appendix'):
            invalid_ids.add(issue['finding'])

    # Compute corrected gate
    gate = compute_quality_gate(findings, invalid_ids)

    # Output results
    print("=" * 60)
    print("  VALIDATION RESULTS")
    print("=" * 60)
    print(f"Report: {report_path}")
    print(f"Rules loaded: {len(rules_lookup)}")
    print(f"Findings extracted: {len(findings)}")
    print(f"Issues found: {len(issues)}")
    print()

    if issues:
        print("| Check | Finding | Issue | Action |")
        print("|-------|---------|-------|--------|")
        for issue in issues:
            print(f"| {issue['check']} | {issue['finding']} | {issue['issue'][:60]} | {issue['action']} |")
        print()

    print(f"Valid findings (after removing invalid): {len(findings) - len(invalid_ids)}")
    print(f"Invalid findings (to Appendix): {len(invalid_ids)}")
    print()
    print("QUALITY GATE (Recalculated):")
    print(f"  Status: {gate['status']}")
    print(f"  Critical: {gate['critical']}")
    print(f"  High P0: {gate['high_p0']}")
    print(f"  High (P1-P3): {gate['high_other']}")
    print(f"  Medium: {gate['medium']}")
    print()

    # Check if report's stated gate matches
    report_gate_match = re.search(r'\*\*Status:\s*(PASS|FAIL)\*\*', report_text)
    if report_gate_match:
        reported_gate = report_gate_match.group(1)
        if reported_gate != gate['status']:
            print(f"⚠ GATE MISMATCH: Report says {reported_gate}, should be {gate['status']}")
        else:
            print(f"✓ Gate matches: {gate['status']}")

    print("=" * 60)

    # Write machine-readable output for LLM consumption
    output_path = report_path.replace('.md', '_validation.json')
    validation_output = {
        'report': report_path,
        'total_findings': len(findings),
        'issues': issues,
        'invalid_finding_ids': list(invalid_ids),
        'quality_gate': gate,
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(validation_output, f, indent=2, ensure_ascii=False)
    print(f"\nValidation JSON written to: {output_path}")

    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
