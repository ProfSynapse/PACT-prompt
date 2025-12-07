#!/usr/bin/env python3
"""
Dependency Mapper

Maps import/require dependencies between files to detect circular dependencies
and orphan modules. Supports Python, JavaScript, and TypeScript.

Security: Path validation, file size limits (1MB), timeout handling (60s)
Dependencies: Python 3.11+ standard library only
"""

import ast
import json
import argparse
import re
import sys
import signal
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict

# Constants
MAX_FILE_SIZE = 1024 * 1024  # 1MB
TIMEOUT_SECONDS = 60


class TimeoutError(Exception):
    """Raised when script execution exceeds timeout."""
    pass


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutError("Script execution exceeded timeout")


def validate_file_path(file_path: str, allowed_root: Optional[str] = None) -> Path:
    """Validate file path meets security requirements."""
    if allowed_root is None:
        allowed_root = Path.cwd()
    else:
        allowed_root = Path(allowed_root).resolve()

    path = Path(file_path).resolve()

    try:
        path.relative_to(allowed_root)
    except ValueError:
        raise SecurityError(f"Path {file_path} is outside allowed directory {allowed_root}")

    if path.is_symlink():
        raise SecurityError(f"Symbolic links not allowed: {file_path}")

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.is_file() and path.stat().st_size > MAX_FILE_SIZE:
        raise SecurityError(f"File too large (max {MAX_FILE_SIZE} bytes): {file_path}")

    return path


def extract_python_imports(file_path: Path) -> List[str]:
    """
    Extract import statements from Python file using AST.

    Returns list of imported module names (not resolved to file paths yet).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def extract_javascript_imports(file_path: Path) -> List[str]:
    """
    Extract import/require statements from JavaScript/TypeScript using regex.

    Returns list of imported module names.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    imports = []

    # ES6 imports: import ... from '...'
    es6_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
    imports.extend(re.findall(es6_pattern, source))

    # CommonJS require: require('...')
    require_pattern = r'require\([\'"]([^\'"]+)[\'"]\)'
    imports.extend(re.findall(require_pattern, source))

    # Dynamic imports: import('...')
    dynamic_pattern = r'import\([\'"]([^\'"]+)[\'"]\)'
    imports.extend(re.findall(dynamic_pattern, source))

    return imports


def resolve_import_to_file(
    import_name: str,
    source_file: Path,
    root_dir: Path,
    language: str
) -> Optional[Path]:
    """
    Resolve import statement to actual file path.

    Args:
        import_name: Module name from import statement
        source_file: File containing the import
        root_dir: Project root directory
        language: Source language (python, javascript, typescript)

    Returns:
        Resolved file path or None if not found
    """
    # Skip external/stdlib modules
    if language == 'python':
        # Skip standard library and installed packages (simple heuristic)
        if '.' not in import_name or import_name.split('.')[0] in [
            'os', 'sys', 'json', 'ast', 're', 'pathlib', 'typing', 'collections',
            'argparse', 'signal', 'datetime', 'math', 'random', 'subprocess'
        ]:
            return None

        # Try to resolve as relative path from root
        module_path = Path(import_name.replace('.', '/'))

        # Try with .py extension
        resolved = root_dir / f"{module_path}.py"
        if resolved.exists():
            return resolved

        # Try as package (__init__.py)
        resolved = root_dir / module_path / "__init__.py"
        if resolved.exists():
            return resolved

    elif language in ('javascript', 'typescript'):
        # Skip node_modules and built-in modules
        if not import_name.startswith('.'):
            return None

        # Resolve relative import
        source_dir = source_file.parent
        import_path = (source_dir / import_name).resolve()

        # Try various extensions
        extensions = ['.js', '.ts', '.tsx', '.jsx'] if language == 'typescript' else ['.js', '.jsx']

        for ext in extensions:
            resolved = import_path.with_suffix(ext)
            if resolved.exists() and resolved.is_relative_to(root_dir):
                return resolved

        # Try as directory with index file
        for ext in extensions:
            resolved = import_path / f"index{ext}"
            if resolved.exists() and resolved.is_relative_to(root_dir):
                return resolved

    return None


def build_dependency_graph(
    root_dir: Path,
    language: str
) -> Tuple[Dict[str, List[str]], List[Dict[str, Any]]]:
    """
    Build dependency graph for all files in directory.

    Returns:
        (dependency_graph, errors) where dependency_graph maps file paths to
        lists of imported file paths
    """
    graph = defaultdict(list)
    errors = []

    # Find all source files
    if language == 'python':
        pattern = '**/*.py'
    elif language == 'javascript':
        pattern = '**/*.js'
    elif language == 'typescript':
        patterns = ['**/*.ts', '**/*.tsx']
    else:
        raise ValueError(f"Unsupported language: {language}")

    # Collect files
    files = []
    if language == 'typescript':
        for pattern in patterns:
            files.extend(root_dir.glob(pattern))
    else:
        files = list(root_dir.glob(pattern))

    # Extract imports for each file
    for file_path in files:
        try:
            if language == 'python':
                imports = extract_python_imports(file_path)
            else:
                imports = extract_javascript_imports(file_path)

            # Resolve imports to file paths
            for import_name in imports:
                resolved = resolve_import_to_file(import_name, file_path, root_dir, language)
                if resolved:
                    # Store as relative path from root
                    source_rel = file_path.relative_to(root_dir)
                    target_rel = resolved.relative_to(root_dir)
                    graph[str(source_rel)].append(str(target_rel))

        except Exception as e:
            errors.append({
                'file': str(file_path.relative_to(root_dir)),
                'error': str(e),
                'severity': 'warning',
                'action': 'Skipped file, continuing with analysis'
            })

    return dict(graph), errors


def detect_circular_dependencies(graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Detect circular dependencies using depth-first search.

    Returns list of circular dependency cycles.
    """
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: List[str]):
        """DFS to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path[:])
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]

                # Determine severity based on cycle length
                severity = 'high' if len(cycle) <= 3 else 'medium'

                cycles.append({
                    'cycle': cycle,
                    'severity': severity
                })

        rec_stack.remove(node)

    # Run DFS from each node
    for node in graph:
        if node not in visited:
            dfs(node, [])

    # Deduplicate cycles (same cycle can be found multiple times)
    unique_cycles = []
    seen_sets = []

    for cycle_data in cycles:
        cycle = cycle_data['cycle']
        cycle_set = set(cycle)
        if cycle_set not in seen_sets:
            seen_sets.append(cycle_set)
            unique_cycles.append(cycle_data)

    return unique_cycles


def find_orphan_modules(graph: Dict[str, List[str]], root_dir: Path) -> List[str]:
    """
    Find orphan modules (files not imported by any other file).

    Excludes common entry points (main.py, index.js, app.py, etc.)
    """
    all_files = set(graph.keys())
    imported_files = set()

    for imports in graph.values():
        imported_files.update(imports)

    # Orphans are files that exist but are never imported
    orphans = all_files - imported_files

    # Filter out common entry points
    entry_point_patterns = [
        'main.py', '__main__.py', 'app.py', 'run.py',
        'index.js', 'index.ts', 'main.js', 'app.js',
        'server.js', 'server.ts'
    ]

    filtered_orphans = []
    for orphan in orphans:
        is_entry_point = any(
            orphan.endswith(pattern) or orphan == pattern
            for pattern in entry_point_patterns
        )
        if not is_entry_point:
            filtered_orphans.append(orphan)

    return sorted(filtered_orphans)


def build_module_details(
    graph: Dict[str, List[str]],
    root_dir: Path
) -> List[Dict[str, Any]]:
    """Build detailed module information including fan-in/fan-out."""
    # Build reverse graph (imported_by)
    imported_by = defaultdict(list)
    for source, targets in graph.items():
        for target in targets:
            imported_by[target].append(source)

    # Get all modules (both importers and imported)
    all_modules = set(graph.keys()) | set(imported_by.keys())

    modules = []
    for module in sorted(all_modules):
        modules.append({
            'path': module,
            'imports': sorted(graph.get(module, [])),
            'imported_by': sorted(imported_by.get(module, [])),
            'is_orphan': module not in imported_by and module in graph
        })

    return modules


def calculate_max_depth(graph: Dict[str, List[str]]) -> int:
    """Calculate maximum dependency depth using BFS."""
    max_depth = 0

    def bfs_depth(start: str) -> int:
        """Calculate depth from starting node."""
        visited = {start}
        queue = [(start, 0)]
        depth = 0

        while queue:
            node, current_depth = queue.pop(0)
            depth = max(depth, current_depth)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, current_depth + 1))

        return depth

    for node in graph:
        max_depth = max(max_depth, bfs_depth(node))

    return max_depth


def generate_summary(
    graph: Dict[str, List[str]],
    circular_deps: List[Dict[str, Any]],
    orphans: List[str]
) -> Dict[str, Any]:
    """Generate summary statistics."""
    total_dependencies = sum(len(imports) for imports in graph.values())
    max_depth = calculate_max_depth(graph)

    return {
        'total_modules': len(set(graph.keys()) | set(dep for deps in graph.values() for dep in deps)),
        'total_dependencies': total_dependencies,
        'circular_dependencies': len(circular_deps),
        'orphan_modules': len(orphans),
        'max_depth': max_depth
    }


def output_dot_format(graph: Dict[str, List[str]]):
    """Output dependency graph in DOT format for Graphviz."""
    print("digraph dependencies {")
    print("  rankdir=LR;")
    print("  node [shape=box];")

    for source, targets in graph.items():
        # Escape quotes in node names
        source_label = source.replace('"', '\\"')
        for target in targets:
            target_label = target.replace('"', '\\"')
            print(f'  "{source_label}" -> "{target_label}";')

    print("}")


def main():
    """Main entry point."""
    if sys.version_info < (3, 11):
        print("Error: Python 3.11+ required", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Map import/require dependencies and detect circular dependencies'
    )
    parser.add_argument('--directory', type=str, required=True,
                        help='Root directory to analyze')
    parser.add_argument('--language', choices=['python', 'javascript', 'typescript'],
                        required=True, help='Language to analyze')
    parser.add_argument('--output-graph', choices=['json', 'dot'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--detect-circular', action='store_true',
                        help='Detect circular dependencies')

    args = parser.parse_args()

    # Set timeout (Unix only)
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT_SECONDS)

    try:
        root_dir = validate_file_path(args.directory)
        if not root_dir.is_dir():
            raise ValueError(f"Not a directory: {args.directory}")

        # Build dependency graph
        graph, errors = build_dependency_graph(root_dir, args.language)

        if args.output_graph == 'dot':
            # Output DOT format
            output_dot_format(graph)
        else:
            # Build detailed module info
            modules = build_module_details(graph, root_dir)

            # Detect circular dependencies if requested
            circular_deps = []
            if args.detect_circular:
                circular_deps = detect_circular_dependencies(graph)

            # Find orphan modules
            orphans = find_orphan_modules(graph, root_dir)

            # Generate summary
            summary = generate_summary(graph, circular_deps, orphans)

            # Output JSON
            output = {
                'summary': summary,
                'modules': modules
            }

            if circular_deps:
                output['circular_dependencies'] = circular_deps

            if orphans:
                output['orphan_modules'] = orphans

            if errors:
                output['errors'] = errors

            print(json.dumps(output, indent=2))

        sys.exit(0)

    except TimeoutError:
        print(json.dumps({'error': 'Script execution exceeded timeout'}), file=sys.stderr)
        sys.exit(1)
    except (SecurityError, FileNotFoundError, ValueError) as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({'error': f'Unexpected error: {e}'}), file=sys.stderr)
        sys.exit(1)
    finally:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)


if __name__ == '__main__':
    main()
