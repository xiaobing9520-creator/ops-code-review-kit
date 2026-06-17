#!/usr/bin/env python3
"""
generate-manifest.py — Deterministic File Manifest Generator (v1.10.1)

Generates file-manifest.json WITHOUT requiring the LLM to read every file.
Uses filesystem operations and grep for 100% deterministic, complete coverage.

This script solves the v1.10 bootstrap problem: file-manifest.json must cover
ALL source files, but the LLM cannot read 1000+ files in one context window.

What this script provides (deterministic, no LLM needed):
  - path: from filesystem scan
  - module: from directory structure
  - tokens: from character count / 4
  - imports/imported_by: from regex extraction of import/require statements
  - security_signals: from grep patterns
  - quality_signals: from grep patterns

What this script does NOT provide (LLM adds later, optional):
  - description: requires semantic understanding of the file

Usage:
  python3 .kiro/scripts/generate-manifest.py
  python3 .kiro/scripts/generate-manifest.py --root /path/to/project
  python3 .kiro/scripts/generate-manifest.py --root . --output code-review-artifacts/reverse-engineering/file-manifest.json

Output:
  - Writes file-manifest.json with entries for ALL source files
  - Prints summary to stdout
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


# File extensions to include
SOURCE_EXTENSIONS = {
    '.js', '.ts', '.jsx', '.tsx', '.vue', '.mjs', '.cjs',
    '.java', '.kt', '.scala',
    '.py',
    '.go',
    '.rs',
    '.rb',
    '.php',
    '.cs',
    '.swift',
    '.c', '.cpp', '.h', '.hpp',
}

# Directories to exclude
EXCLUDE_DIRS = {
    'node_modules', 'vendor', '.git', 'build', 'dist', 'target', 'out',
    '.gradle', '.idea', '.vscode', '__pycache__', '.next', '.nuxt',
    'coverage', '.nyc_output', 'dist-all',
}

# Signal grep patterns
SECURITY_SIGNALS = {
    'v-html': [r'v-html'],
    'innerHTML': [r'innerHTML', r'dangerouslySetInnerHTML'],
    'eval-usage': [r'\beval\s*\(', r'new\s+Function\s*\('],
    'hardcoded-secret': [
        r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']',
        r'(?:secret|app_secret|APP_SECRET)\s*[=:]\s*["\'][^"\']{4,}["\']',
        r'(?:apiKey|api_key|API_KEY)\s*[=:]\s*["\'][^"\']{4,}["\']',
    ],
    'md5-usage': [r'\bmd5\s*\(', r'\bMD5\s*\(', r'createHash\s*\(\s*["\']md5'],
    'localStorage': [r'localStorage\.setItem', r'localStorage\.getItem', r'localStorage\.removeItem'],
    'console-log': [r'console\.log\s*\('],
    'http-url': [r'http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)'],
}

QUALITY_SIGNALS = {
    'empty-catch': [r'catch\s*\([^)]*\)\s*\{\s*\}', r'catch\s*\([^)]*\)\s*\{\s*//'],
    'var-declaration': [r'\bvar\s+\w'],
}

# Import extraction patterns
IMPORT_PATTERNS = {
    'es6_import': re.compile(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'),
    'require': re.compile(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    'dynamic_import': re.compile(r'import\s*\(\s*["\']([^"\']+)["\']\s*\)'),
    'vue_import': re.compile(r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'),
}

# Path alias patterns (Vue/webpack)
ALIAS_PATTERNS = {
    '@/': 'src/',
    '~/': 'src/',
    '@src/': 'src/',
}


def should_exclude(path):
    """Check if path should be excluded."""
    parts = Path(path).parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def find_source_files(root):
    """Find all source files, sorted alphabetically."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in SOURCE_EXTENSIONS:
                relpath = os.path.relpath(filepath, root)
                if not should_exclude(relpath):
                    files.append(relpath)

    return sorted(files)


def count_tokens(filepath, root):
    """Estimate token count as chars / 4."""
    full_path = os.path.join(root, filepath)
    try:
        size = os.path.getsize(full_path)
        return size // 4
    except OSError:
        return 0


def read_file_content(filepath, root):
    """Read file content, return empty string on error."""
    full_path = os.path.join(root, filepath)
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ''


def detect_signals(content, signal_dict):
    """Detect signals in file content using regex patterns."""
    found = []
    for signal_name, patterns in sorted(signal_dict.items()):
        for pattern in patterns:
            if re.search(pattern, content):
                found.append(signal_name)
                break
    return found


def is_test_file(filepath):
    """Check if file is a test file."""
    lower = filepath.lower()
    return ('test' in lower or 'spec' in lower or '__tests__' in lower
            or 'mock' in lower or 'fixture' in lower)


def is_third_party(filepath):
    """Check if file is third-party/vendor code."""
    lower = filepath.lower()
    return ('vendor' in lower or 'vod-js-sdk' in lower or 'polyfill' in lower
            or 'min.js' in lower or '.min.' in lower)


def resolve_import_path(import_path, current_file, root, all_files_set):
    """Resolve an import path to an actual file path."""
    # Apply alias resolution
    resolved = import_path
    for alias, replacement in ALIAS_PATTERNS.items():
        if resolved.startswith(alias):
            resolved = replacement + resolved[len(alias):]
            break

    # Skip external packages (no ./ or ../ and no alias resolved)
    if not resolved.startswith('.') and not resolved.startswith('src/'):
        return None

    # Resolve relative paths
    if resolved.startswith('.'):
        current_dir = os.path.dirname(current_file)
        resolved = os.path.normpath(os.path.join(current_dir, resolved))

    # Try various extensions
    candidates = [resolved]
    if not os.path.splitext(resolved)[1]:
        for ext in ['.js', '.ts', '.vue', '.jsx', '.tsx', '/index.js', '/index.ts', '/index.vue']:
            candidates.append(resolved + ext)

    for candidate in candidates:
        # Normalize path separators
        normalized = candidate.replace('\\', '/')
        if normalized in all_files_set:
            return normalized

    return None


def extract_imports(content, current_file, root, all_files_set):
    """Extract import paths from file content and resolve to project files."""
    imports = set()

    for pattern_name, pattern in IMPORT_PATTERNS.items():
        for match in pattern.finditer(content):
            import_path = match.group(1)
            resolved = resolve_import_path(import_path, current_file, root, all_files_set)
            if resolved and resolved != current_file:
                imports.add(resolved)

    return sorted(imports)


def discover_modules(root):
    """Discover project modules using the steering.md priority chain.

    Returns a sorted list of module directory names, or empty list if
    the project is a single-module project.
    """
    modules = []

    # Priority 1: Maven — parse <modules> in root pom.xml
    pom_path = os.path.join(root, 'pom.xml')
    if os.path.exists(pom_path):
        try:
            with open(pom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Extract <module>...</module> entries
            module_pattern = re.compile(r'<module>\s*([^<]+?)\s*</module>')
            matches = module_pattern.findall(content)
            if matches:
                modules = sorted(set(matches))
                return modules
        except OSError:
            pass

    # Priority 2: Gradle — parse include in settings.gradle(.kts)
    for gradle_file in ['settings.gradle', 'settings.gradle.kts']:
        gradle_path = os.path.join(root, gradle_file)
        if os.path.exists(gradle_path):
            try:
                with open(gradle_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Match include 'module1', 'module2' or include("module1", "module2")
                include_pattern = re.compile(r"include\s*[\(]?\s*['\"]([^'\"]+)['\"]")
                matches = include_pattern.findall(content)
                if matches:
                    # Gradle modules use : prefix, strip it
                    modules = sorted(set(m.lstrip(':').replace(':', '/') for m in matches))
                    return modules
            except OSError:
                pass

    # Priority 3: npm/pnpm/yarn workspaces
    pkg_path = os.path.join(root, 'package.json')
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r') as f:
                pkg = json.load(f)
            workspaces = pkg.get('workspaces', [])
            if isinstance(workspaces, dict):
                workspaces = workspaces.get('packages', [])
            if workspaces:
                # Resolve globs to actual directories
                resolved = []
                for ws in workspaces:
                    ws_dir = ws.rstrip('/*').rstrip('/')
                    ws_full = os.path.join(root, ws_dir)
                    if os.path.isdir(ws_full):
                        resolved.append(ws_dir)
                    else:
                        # Try glob
                        import glob
                        for match in glob.glob(os.path.join(root, ws)):
                            if os.path.isdir(match):
                                resolved.append(os.path.relpath(match, root))
                if resolved:
                    modules = sorted(set(resolved))
                    return modules
        except (json.JSONDecodeError, OSError):
            pass

    # Priority 4: Go workspace
    go_work_path = os.path.join(root, 'go.work')
    if os.path.exists(go_work_path):
        try:
            with open(go_work_path, 'r', encoding='utf-8') as f:
                content = f.read()
            use_pattern = re.compile(r'use\s*\(\s*([^)]+)\)', re.DOTALL)
            match = use_pattern.search(content)
            if match:
                dirs = [d.strip().strip('./') for d in match.group(1).split('\n') if d.strip()]
                modules = sorted(set(dirs))
                return modules
        except OSError:
            pass

    # Priority 5: Directory heuristic — subdirs with their own build file
    build_files = ['pom.xml', 'build.gradle', 'build.gradle.kts', 'package.json',
                   'go.mod', 'Cargo.toml', 'pyproject.toml']
    for entry in sorted(os.listdir(root)):
        entry_path = os.path.join(root, entry)
        if not os.path.isdir(entry_path):
            continue
        if entry.startswith('.') or entry in EXCLUDE_DIRS:
            continue
        for bf in build_files:
            if os.path.exists(os.path.join(entry_path, bf)):
                modules.append(entry)
                break

    return sorted(set(modules)) if modules else []


def detect_module_for_file(filepath, modules):
    """Determine which module a file belongs to based on discovered modules.

    Returns the module name if the file is under a module directory,
    or 'root' if it's in the project root (not in any module).
    """
    if not modules:
        return None  # Single-module project, will use project name

    parts = Path(filepath).parts
    if len(parts) >= 1:
        # Check if first directory component matches a module
        for module in modules:
            module_parts = Path(module).parts
            if parts[:len(module_parts)] == module_parts:
                return module

    return 'root'


def detect_module(filepath, root):
    """Detect which module a file belongs to.

    NOTE: This function is kept for backward compatibility but the preferred
    approach is to call discover_modules() once and then use
    detect_module_for_file() for each file.
    """
    # Check for module-manifest.md
    manifest_path = os.path.join(root, 'module-manifest.md')
    if os.path.exists(manifest_path):
        pass

    # Check for workspaces in package.json
    pkg_path = os.path.join(root, 'package.json')
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r') as f:
                pkg = json.load(f)
            workspaces = pkg.get('workspaces', [])
            if workspaces:
                parts = Path(filepath).parts
                for ws in workspaces:
                    ws_dir = ws.rstrip('/*').rstrip('/')
                    if parts[0] == ws_dir:
                        return ws_dir
        except (json.JSONDecodeError, OSError):
            pass

    # Default: use project name from package.json or directory name
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r') as f:
                pkg = json.load(f)
            return pkg.get('name', os.path.basename(root))
        except (json.JSONDecodeError, OSError):
            pass

    return os.path.basename(root)


def generate_manifest(root, output_path=None):
    """Generate the complete file manifest."""
    root = os.path.abspath(root)

    # Find all source files
    print(f"Scanning: {root}")
    files = find_source_files(root)
    print(f"Found {len(files)} source files")

    if not files:
        print("ERROR: No source files found.")
        sys.exit(1)

    # Create file set for import resolution
    all_files_set = set(files)

    # Discover project modules (Maven, Gradle, npm workspaces, Go workspace, etc.)
    modules = discover_modules(root)
    if modules:
        print(f"Detected {len(modules)} modules: {', '.join(modules[:10])}{'...' if len(modules) > 10 else ''}")
    else:
        print(f"Single-module project: {os.path.basename(root)}")

    # Fallback project name for single-module projects
    project_name = os.path.basename(root)
    pkg_path = os.path.join(root, 'package.json')
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r') as f:
                pkg = json.load(f)
            project_name = pkg.get('name', project_name)
        except (json.JSONDecodeError, OSError):
            pass

    # Process each file
    manifest = []
    import_map = defaultdict(list)  # file -> list of files it imports

    print(f"Processing files...")
    for i, filepath in enumerate(files):
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(files)}...")

        content = read_file_content(filepath, root)
        tokens = count_tokens(filepath, root)

        # Detect signals (skip test files and third-party for some signals)
        skip_signals = is_test_file(filepath) or is_third_party(filepath)

        security_signals = []
        quality_signals = []
        if not skip_signals:
            security_signals = detect_signals(content, SECURITY_SIGNALS)
            quality_signals = detect_signals(content, QUALITY_SIGNALS)
        elif not is_third_party(filepath):
            # Still detect critical security signals in test files
            security_signals = detect_signals(content, {
                'hardcoded-secret': SECURITY_SIGNALS['hardcoded-secret']
            })

        # Extract imports
        imports = extract_imports(content, filepath, root, all_files_set)
        import_map[filepath] = imports

        # Determine module for this file
        file_module = detect_module_for_file(filepath, modules) if modules else project_name
        if file_module == 'root':
            file_module = project_name

        entry = {
            'path': filepath,
            'module': file_module,
            'tokens': tokens,
            'imports': imports,
            'imported_by': [],  # filled in second pass
        }

        if security_signals:
            entry['security_signals'] = security_signals
        if quality_signals:
            entry['quality_signals'] = quality_signals

        manifest.append(entry)

    # Second pass: compute imported_by (reverse edges)
    print("Computing dependency graph (imported_by)...")
    path_to_entry = {e['path']: e for e in manifest}
    for filepath, imports in import_map.items():
        for imp in imports:
            if imp in path_to_entry:
                path_to_entry[imp]['imported_by'].append(filepath)

    # Sort imported_by for determinism
    for entry in manifest:
        entry['imported_by'] = sorted(entry['imported_by'])

    # Determine output path
    if not output_path:
        output_dir = os.path.join(root, 'code-review-artifacts', 'reverse-engineering')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'file-manifest.json')
    else:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    # Write manifest
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Print summary
    total_tokens = sum(e['tokens'] for e in manifest)
    files_with_security_signals = sum(1 for e in manifest if e.get('security_signals'))
    files_with_quality_signals = sum(1 for e in manifest if e.get('quality_signals'))

    # Aggregate signal counts
    signal_counts = defaultdict(int)
    for entry in manifest:
        for sig in entry.get('security_signals', []):
            signal_counts[sig] += 1
        for sig in entry.get('quality_signals', []):
            signal_counts[sig] += 1

    # Count files per module
    module_file_counts = defaultdict(int)
    for entry in manifest:
        module_file_counts[entry['module']] += 1

    print()
    print("=" * 60)
    print("  FILE MANIFEST GENERATED (v1.10.1)")
    print("=" * 60)
    if modules:
        print(f"  Modules detected: {len(modules)}")
        for mod in sorted(module_file_counts.keys()):
            print(f"    {mod}: {module_file_counts[mod]} files")
    else:
        print(f"  Project: {project_name}")
    print(f"  Total files: {len(manifest)}")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Files with security signals: {files_with_security_signals}")
    print(f"  Files with quality signals: {files_with_quality_signals}")
    print()
    print("  Signal distribution:")
    for sig, count in sorted(signal_counts.items()):
        print(f"    {sig}: {count} files")
    print()
    print(f"  Output: {output_path}")
    print("=" * 60)

    return manifest


def main():
    root = '.'
    output_path = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--root' and i + 1 < len(args):
            root = args[i + 1]
            i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        else:
            i += 1

    generate_manifest(root, output_path)


if __name__ == '__main__':
    main()
