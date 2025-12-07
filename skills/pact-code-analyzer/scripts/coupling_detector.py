#!/usr/bin/env python3
"""
Coupling Detector

Detects tight coupling between modules by analyzing dependency relationships.
Calculates fan-in (incoming dependencies) and fan-out (outgoing dependencies).

Security: Path validation, file size limits, timeout handling
Dependencies: Python 3.11+ standard library only
"""

import json
import argparse
import sys
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Import dependency mapping from dependency_mapper
# Note: In production, these functions would be shared or imported
# For standalone script, we'll duplicate the necessary functions

MAX_FILE_SIZE = 1024 * 1024  # 1MB
TIMEOUT_SECONDS = 60
DEFAULT_THRESHOLD = 10


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


# Note: In production, we would import build_dependency_graph from dependency_mapper
# For this standalone implementation, we'll create a simplified version
def build_simplified_dependency_graph(root_dir: Path) -> Dict[str, List[str]]:
    """
    Build simplified dependency graph by analyzing imports.

    This is a simplified version that detects Python imports only.
    For full functionality, use dependency_mapper.py first and process its output.
    """
    import ast
    import re

    graph = defaultdict(list)

    # Find Python files
    for py_file in root_dir.glob('**/*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Try to resolve imports to files in the project
            source_rel = py_file.relative_to(root_dir)

            for import_name in imports:
                # Simple resolution: convert module.name to module/name.py
                module_path = Path(import_name.replace('.', '/'))
                resolved = root_dir / f"{module_path}.py"

                if resolved.exists():
                    target_rel = resolved.relative_to(root_dir)
                    graph[str(source_rel)].append(str(target_rel))

        except Exception:
            # Skip files with errors
            continue

    return dict(graph)


def calculate_coupling_metrics(graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Calculate coupling metrics for each module.

    Metrics:
    - fan_out: Number of modules this module depends on (outgoing)
    - fan_in: Number of modules that depend on this module (incoming)
    - total_coupling: fan_in + fan_out
    """
    # Build reverse graph for fan-in calculation
    fan_in_map = defaultdict(list)
    for source, targets in graph.items():
        for target in targets:
            fan_in_map[target].append(source)

    # Get all modules (both importers and imported)
    all_modules = set(graph.keys()) | set(fan_in_map.keys())

    modules = []
    for module in sorted(all_modules):
        fan_out = graph.get(module, [])
        fan_in = fan_in_map.get(module, [])

        total_coupling = len(fan_out) + len(fan_in)

        modules.append({
            'path': module,
            'outgoing_dependencies': len(fan_out),
            'incoming_dependencies': len(fan_in),
            'total_coupling': total_coupling,
            'fan_out': sorted(fan_out),
            'fan_in': sorted(fan_in)
        })

    return modules


def add_recommendations(
    modules: List[Dict[str, Any]],
    threshold: int
) -> List[Dict[str, Any]]:
    """Add coupling threshold flags and recommendations."""
    for module in modules:
        module['exceeds_threshold'] = module['total_coupling'] > threshold

        if module['exceeds_threshold']:
            coupling = module['total_coupling']

            if module['incoming_dependencies'] > module['outgoing_dependencies']:
                # High fan-in: Many modules depend on this one
                module['recommendation'] = (
                    f"High fan-in ({module['incoming_dependencies']}). "
                    f"This is a central module. Ensure it's stable and well-tested. "
                    f"Consider extracting commonly used functionality to reduce coupling."
                )
            elif module['outgoing_dependencies'] > module['incoming_dependencies']:
                # High fan-out: This module depends on many others
                module['recommendation'] = (
                    f"High fan-out ({module['outgoing_dependencies']}). "
                    f"This module depends on many others. Consider using dependency injection, "
                    f"events, or facades to reduce direct dependencies."
                )
            else:
                # Balanced but high coupling
                module['recommendation'] = (
                    f"High coupling ({coupling} total dependencies). "
                    f"Consider splitting into smaller modules or using events to decouple."
                )

    return modules


def generate_summary(modules: List[Dict[str, Any]], threshold: int) -> Dict[str, Any]:
    """Generate summary statistics."""
    total_modules = len(modules)

    all_couplings = [m['total_coupling'] for m in modules]
    avg_coupling = sum(all_couplings) / len(all_couplings) if all_couplings else 0

    tightly_coupled = sum(1 for m in modules if m['exceeds_threshold'])

    # Find most coupled modules
    sorted_modules = sorted(modules, key=lambda m: m['total_coupling'], reverse=True)
    top_coupled = sorted_modules[:5] if len(sorted_modules) >= 5 else sorted_modules

    return {
        'total_modules': total_modules,
        'average_coupling': round(avg_coupling, 1),
        'tightly_coupled_modules': tightly_coupled,
        'coupling_threshold': threshold,
        'top_coupled_modules': [
            {
                'path': m['path'],
                'coupling': m['total_coupling']
            }
            for m in top_coupled
        ]
    }


def main():
    """Main entry point."""
    start_time = time.perf_counter()

    if sys.version_info < (3, 11):
        print("Error: Python 3.11+ required", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Detect tight coupling between modules'
    )
    parser.add_argument('--directory', type=str, required=True,
                        help='Root directory to analyze')
    parser.add_argument('--threshold', type=int, default=DEFAULT_THRESHOLD,
                        help=f'Flag modules exceeding dependency count (default: {DEFAULT_THRESHOLD})')
    parser.add_argument('--show-details', action='store_true',
                        help='Show detailed fan-in/fan-out lists')

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
        graph = build_simplified_dependency_graph(root_dir)

        # Calculate execution duration
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        if not graph:
            print(json.dumps({
                'metadata': {
                    'schema_version': '1.0.0',
                    'script_version': '0.1.0',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'execution_duration_ms': duration_ms
                },
                'summary': {
                    'total_modules': 0,
                    'average_coupling': 0,
                    'tightly_coupled_modules': 0,
                    'coupling_threshold': args.threshold
                },
                'modules': [],
                'warning': 'No dependencies found. Ensure the directory contains Python files with import statements.'
            }, indent=2))
            sys.exit(0)

        # Calculate coupling metrics
        modules = calculate_coupling_metrics(graph)

        # Add recommendations
        modules = add_recommendations(modules, args.threshold)

        # Generate summary
        summary = generate_summary(modules, args.threshold)

        # Prepare output
        output = {
            'metadata': {
                'schema_version': '1.0.0',
                'script_version': '0.1.0',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'execution_duration_ms': duration_ms
            },
            'summary': summary,
            'modules': modules if args.show_details else [
                {k: v for k, v in m.items() if k not in ['fan_in', 'fan_out']}
                for m in modules
            ]
        }

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
