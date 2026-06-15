#!/usr/bin/env python3
"""
scan-planner.py — Deterministic Context Window Batch Planner (v1.10)

Reads file-manifest.json and produces scan-plan.json that assigns files to
context window batches based on token budget and dependency relationships.

Algorithm:
  1. Build dependency graph from imports/imported_by
  2. Find connected components (files that MUST be in same batch)
  3. Sort components deterministically (by first file path alphabetically)
  4. Greedily assign components to batches respecting token budget

Usage:
  python3 .kiro/scripts/scan-planner.py --manifest code-review-artifacts/reverse-engineering/file-manifest.json
  python3 .kiro/scripts/scan-planner.py --manifest file-manifest.json --budget 600000

Output:
  - Writes scan-plan.json to code-review-artifacts/scan-plan.json
  - Prints human-readable summary to stdout
"""

import json
import sys
import os
from collections import defaultdict
from pathlib import Path


DEFAULT_BUDGET = 800000  # 800K tokens per batch (leaves ~200K for rules/prompt/output)


def load_manifest(manifest_path):
    """Load file-manifest.json and return list of file entries."""
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_dependency_graph(files):
    """Build adjacency list from imports/imported_by relationships."""
    path_set = {f['path'] for f in files}
    adj = defaultdict(set)

    for f in files:
        path = f['path']
        for imp in f.get('imports', []):
            if imp in path_set:
                adj[path].add(imp)
                adj[imp].add(path)
        for imp_by in f.get('imported_by', []):
            if imp_by in path_set:
                adj[path].add(imp_by)
                adj[imp_by].add(path)

    return adj


def find_connected_components(files, adj):
    """Find connected components using BFS. Returns list of sorted file groups."""
    path_set = {f['path'] for f in files}
    visited = set()
    components = []

    for f in sorted(files, key=lambda x: x['path']):
        path = f['path']
        if path in visited:
            continue

        # BFS from this node
        component = []
        queue = [path]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            if node in path_set:
                component.append(node)
            for neighbor in sorted(adj.get(node, [])):
                if neighbor not in visited:
                    queue.append(neighbor)

        if component:
            component.sort()
            components.append(component)

    # Sort components by their first file path for determinism
    components.sort(key=lambda c: c[0])
    return components


def compute_component_tokens(component, file_lookup):
    """Sum tokens for all files in a component."""
    total = 0
    for path in component:
        if path in file_lookup:
            total += file_lookup[path].get('tokens', 0)
    return total


def aggregate_signals(file_paths, file_lookup):
    """Aggregate security_signals and quality_signals for a set of files."""
    signal_counts = defaultdict(int)
    for path in file_paths:
        entry = file_lookup.get(path, {})
        for sig in entry.get('security_signals', []):
            signal_counts[sig] += 1
        for sig in entry.get('quality_signals', []):
            signal_counts[sig] += 1
    return dict(sorted(signal_counts.items()))


def split_oversized_component(component, file_lookup, budget):
    """Split an oversized connected component into sub-batches.

    Strategy: greedy fill by file (alphabetically sorted within component).
    Files in the same component share dependencies, but it's better to split
    into multiple batches than to have one 2M+ token batch that exceeds the
    model's effective working memory.

    The dependency relationship is preserved in the manifest — Agent A can
    reference file-manifest.json for cross-batch context when needed.
    """
    sub_batches = []
    current = []
    current_tokens = 0

    for path in component:  # already sorted alphabetically
        file_tokens = file_lookup.get(path, {}).get('tokens', 0)

        # If single file exceeds budget (unlikely), give it own batch
        if file_tokens > budget:
            if current:
                sub_batches.append(current[:])
                current = []
                current_tokens = 0
            sub_batches.append([path])
            continue

        if current_tokens + file_tokens > budget and current:
            sub_batches.append(current[:])
            current = []
            current_tokens = 0

        current.append(path)
        current_tokens += file_tokens

    if current:
        sub_batches.append(current[:])

    return sub_batches


def assign_batches(components, file_lookup, budget):
    """Greedily assign components to batches respecting token budget."""
    batches = []
    current_batch_files = []
    current_batch_tokens = 0

    for component in components:
        comp_tokens = compute_component_tokens(component, file_lookup)

        # If single component exceeds budget, split it into sub-batches
        if comp_tokens > budget:
            # Flush current batch if non-empty
            if current_batch_files:
                batches.append(current_batch_files[:])
                current_batch_files = []
                current_batch_tokens = 0
            # Split oversized component
            sub_batches = split_oversized_component(component, file_lookup, budget)
            batches.extend(sub_batches)
            print(f"  INFO: Component starting with {component[0]} "
                  f"({comp_tokens:,} tokens, {len(component)} files) exceeds budget "
                  f"({budget:,}). Split into {len(sub_batches)} sub-batches.",
                  file=sys.stderr)
            continue

        # If adding this component would exceed budget, start new batch
        if current_batch_tokens + comp_tokens > budget and current_batch_files:
            batches.append(current_batch_files[:])
            current_batch_files = []
            current_batch_tokens = 0

        # Add component to current batch
        current_batch_files.extend(component)
        current_batch_tokens += comp_tokens

    # Flush remaining
    if current_batch_files:
        batches.append(current_batch_files[:])

    return batches


def create_scan_plan(manifest_path, budget):
    """Main planning logic. Returns scan-plan dict."""
    files = load_manifest(manifest_path)

    if not files:
        return {
            'version': '1.10',
            'total_files': 0,
            'total_tokens': 0,
            'budget_per_batch': budget,
            'batches': [],
            'single_batch': True,
        }

    # Build lookup
    file_lookup = {f['path']: f for f in files}
    total_tokens = sum(f.get('tokens', 0) for f in files)

    # Build dependency graph and find components
    adj = build_dependency_graph(files)
    components = find_connected_components(files, adj)

    # Check if everything fits in one batch
    if total_tokens <= budget:
        all_files = sorted(f['path'] for f in files)
        signal_summary = aggregate_signals(all_files, file_lookup)
        modules = sorted(set(f.get('module', 'unknown') for f in files))

        return {
            'version': '1.10',
            'total_files': len(files),
            'total_tokens': total_tokens,
            'budget_per_batch': budget,
            'batches': [{
                'id': 1,
                'files': all_files,
                'tokens': total_tokens,
                'modules': modules,
                'signal_summary': signal_summary,
            }],
            'single_batch': True,
        }

    # Multi-batch assignment
    batch_file_lists = assign_batches(components, file_lookup, budget)

    batches = []
    for idx, batch_files in enumerate(batch_file_lists, 1):
        batch_files_sorted = sorted(batch_files)
        batch_tokens = sum(file_lookup.get(p, {}).get('tokens', 0) for p in batch_files_sorted)
        batch_modules = sorted(set(
            file_lookup.get(p, {}).get('module', 'unknown') for p in batch_files_sorted
        ))
        signal_summary = aggregate_signals(batch_files_sorted, file_lookup)

        batches.append({
            'id': idx,
            'files': batch_files_sorted,
            'tokens': batch_tokens,
            'modules': batch_modules,
            'signal_summary': signal_summary,
        })

    return {
        'version': '1.10',
        'total_files': len(files),
        'total_tokens': total_tokens,
        'budget_per_batch': budget,
        'batches': batches,
        'single_batch': len(batches) == 1,
    }


def print_summary(plan):
    """Print human-readable summary."""
    print("=" * 60)
    print("  SCAN PLAN (v1.10)")
    print("=" * 60)
    print(f"  Total files: {plan['total_files']}")
    print(f"  Total tokens: {plan['total_tokens']:,}")
    print(f"  Budget per batch: {plan['budget_per_batch']:,}")
    print(f"  Batches: {len(plan['batches'])}")
    print(f"  Single batch mode: {'Yes' if plan['single_batch'] else 'No'}")
    print()

    for batch in plan['batches']:
        print(f"  Batch {batch['id']}:")
        print(f"    Files: {len(batch['files'])}")
        print(f"    Tokens: {batch['tokens']:,}")
        print(f"    Modules: {', '.join(batch['modules'])}")
        if batch['signal_summary']:
            print(f"    Signals: {batch['signal_summary']}")
        print()

    print("=" * 60)


def main():
    # Parse arguments
    manifest_path = None
    budget = DEFAULT_BUDGET
    output_path = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--manifest' and i + 1 < len(args):
            manifest_path = args[i + 1]
            i += 2
        elif args[i] == '--budget' and i + 1 < len(args):
            budget = int(args[i + 1])
            i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        else:
            i += 1

    if not manifest_path:
        print("Usage: python3 scan-planner.py --manifest <file-manifest.json> "
              "[--budget 800000] [--output scan-plan.json]")
        sys.exit(2)

    if not os.path.exists(manifest_path):
        print(f"ERROR: Manifest not found: {manifest_path}")
        sys.exit(2)

    # Default output path
    if not output_path:
        manifest_dir = os.path.dirname(manifest_path)
        parent_dir = os.path.dirname(manifest_dir) if manifest_dir else '.'
        output_path = os.path.join(parent_dir, 'scan-plan.json')

    # Generate plan
    plan = create_scan_plan(manifest_path, budget)

    # Write output
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print_summary(plan)
    print(f"\n  Scan plan written to: {output_path}")


if __name__ == '__main__':
    main()
