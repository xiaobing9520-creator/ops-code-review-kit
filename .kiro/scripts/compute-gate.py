#!/usr/bin/env python3
"""
compute-gate.py — Deterministic Quality Gate Calculator (v1.9)

Reads a validation JSON (from validate-report.py) or directly parses a report,
and computes the definitive Quality Gate result.

Quality Gate Rule:
  FAIL if: Critical > 0 OR (High AND P0)
  PASS otherwise.

Usage:
  python3 .kiro/scripts/compute-gate.py <report.md> [--validation <validation.json>]
  python3 .kiro/scripts/compute-gate.py --summary <report1.md> <report2.md> ...

Output:
  Prints PASS or FAIL with breakdown. Exit code: 0=PASS, 1=FAIL, 2=error.
"""

import json
import re
import sys
import os


def parse_findings_from_report(report_path):
    """Parse findings directly from report markdown."""
    with open(report_path, 'r', encoding='utf-8') as f:
        text = f.read()

    findings = []
    pattern = re.compile(
        r'###\s+(BUG-\d+|SEC-\d+)\s*[—:\-]+\s*(.+?)(?=\n)',
        re.MULTILINE
    )

    for match in pattern.finditer(text):
        finding_id = match.group(1)
        start_pos = match.start()
        section = text[start_pos:start_pos + 2000]

        sev_match = re.search(r'\*\*Risk Level\*\*:\s*(CRITICAL|Critical|HIGH|High|MEDIUM|Medium|LOW|Low)', section)
        pri_match = re.search(r'\*\*Fix Priority\*\*:\s*(P[0-3])', section)

        raw_sev = sev_match.group(1) if sev_match else 'UNKNOWN'

        findings.append({
            'id': finding_id,
            'severity': raw_sev.upper(),
            'priority': pri_match.group(1) if pri_match else 'P3',
        })

    return findings


def compute_gate(findings, invalid_ids=None):
    """Apply quality gate formula."""
    if invalid_ids is None:
        invalid_ids = set()

    critical = 0
    high_p0 = 0
    high_other = 0
    medium = 0

    for f in findings:
        if f['id'] in invalid_ids:
            continue

        sev = f['severity']
        pri = f['priority']

        if sev == 'CRITICAL':
            critical += 1
        elif sev == 'HIGH':
            if pri == 'P0':
                high_p0 += 1
            else:
                high_other += 1
        elif sev == 'MEDIUM':
            medium += 1

    gate_pass = (critical == 0) and (high_p0 == 0)

    return {
        'status': 'PASS' if gate_pass else 'FAIL',
        'critical': critical,
        'high_p0': high_p0,
        'high_other': high_other,
        'medium': medium,
        'total_valid': critical + high_p0 + high_other + medium,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compute-gate.py <report.md> [--validation <file.json>]")
        print("       python3 compute-gate.py --summary <report1.md> <report2.md> ...")
        sys.exit(2)

    # Summary mode: compute overall gate from multiple reports
    if sys.argv[1] == '--summary':
        reports = sys.argv[2:]
        if not reports:
            print("ERROR: No report files specified for --summary")
            sys.exit(2)

        all_pass = True
        print("=" * 60)
        print("  OVERALL QUALITY GATE (Summary)")
        print("=" * 60)

        for rpath in reports:
            if not os.path.exists(rpath):
                print(f"  WARNING: {rpath} not found, skipping")
                continue

            # Try to use validation JSON if available
            val_path = rpath.replace('.md', '_validation.json')
            invalid_ids = set()
            if os.path.exists(val_path):
                with open(val_path, 'r') as f:
                    val_data = json.load(f)
                invalid_ids = set(val_data.get('invalid_finding_ids', []))

            findings = parse_findings_from_report(rpath)
            gate = compute_gate(findings, invalid_ids)

            basename = os.path.basename(rpath)
            status_mark = '✓' if gate['status'] == 'PASS' else '✗'
            print(f"  {status_mark} {basename}: {gate['status']} "
                  f"(Crit={gate['critical']}, High P0={gate['high_p0']}, "
                  f"High other={gate['high_other']}, Med={gate['medium']})")

            if gate['status'] == 'FAIL':
                all_pass = False

        print()
        overall = 'PASS' if all_pass else 'FAIL'
        print(f"  OVERALL: {overall}")
        print("=" * 60)
        sys.exit(0 if all_pass else 1)

    # Single report mode
    report_path = sys.argv[1]
    if not os.path.exists(report_path):
        print(f"ERROR: Report not found: {report_path}")
        sys.exit(2)

    # Check for validation JSON
    invalid_ids = set()
    val_path = None
    if '--validation' in sys.argv:
        idx = sys.argv.index('--validation')
        if idx + 1 < len(sys.argv):
            val_path = sys.argv[idx + 1]
    else:
        val_path = report_path.replace('.md', '_validation.json')

    if val_path and os.path.exists(val_path):
        with open(val_path, 'r') as f:
            val_data = json.load(f)
        invalid_ids = set(val_data.get('invalid_finding_ids', []))
        print(f"Using validation data: {len(invalid_ids)} invalid findings excluded")

    findings = parse_findings_from_report(report_path)
    gate = compute_gate(findings, invalid_ids)

    print("=" * 60)
    print("  QUALITY GATE RESULT")
    print("=" * 60)
    print(f"  Report: {os.path.basename(report_path)}")
    print(f"  Total findings: {len(findings)}")
    print(f"  Excluded (invalid): {len(invalid_ids)}")
    print(f"  Valid findings: {gate['total_valid']}")
    print()
    print(f"  Critical:      {gate['critical']}  {'← BLOCKS' if gate['critical'] > 0 else ''}")
    print(f"  High + P0:     {gate['high_p0']}  {'← BLOCKS' if gate['high_p0'] > 0 else ''}")
    print(f"  High (P1-P3):  {gate['high_other']}  (does not block)")
    print(f"  Medium:        {gate['medium']}  (does not block)")
    print()
    print(f"  *** QUALITY GATE: {gate['status']} ***")
    print("=" * 60)

    sys.exit(0 if gate['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
