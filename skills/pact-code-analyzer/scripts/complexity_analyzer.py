#!/usr/bin/env python3
"""
Cyclomatic Complexity Analyzer

Calculates cyclomatic complexity for Python, JavaScript, and TypeScript files.
Outputs JSON format with per-function complexity scores and threshold violations.

Security: Path validation, file size limits (1MB), timeout handling (60s)
Dependencies: Python 3.11+ standard library only
"""

import ast
import json
import argparse
import re
import sys
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# Constants
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
    """
    Validate file path is within allowed directory and meets security requirements.

    Args:
        file_path: Path to validate
        allowed_root: Root directory to restrict access to (defaults to CWD)

    Returns:
        Validated Path object

    Raises:
        SecurityError: If path fails validation
        FileNotFoundError: If file doesn't exist
    """
    if allowed_root is None:
        allowed_root = Path.cwd()
    else:
        allowed_root = Path(allowed_root).resolve()

    path = Path(file_path).resolve()

    # Check if path is within allowed root
    try:
        path.relative_to(allowed_root)
    except ValueError:
        raise SecurityError(f"Path {file_path} is outside allowed directory {allowed_root}")

    # Reject symbolic links
    if path.is_symlink():
        raise SecurityError(f"Symbolic links not allowed: {file_path}")

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file size
    if path.stat().st_size > MAX_FILE_SIZE:
        raise SecurityError(f"File too large (max {MAX_FILE_SIZE} bytes): {file_path}")

    return path


def calculate_python_complexity(file_path: Path) -> List[Dict[str, Any]]:
    """
    Calculate cyclomatic complexity for Python file using AST.

    Complexity = 1 + number of decision points (if, for, while, and, or, except, with)

    Args:
        file_path: Path to Python file

    Returns:
        List of function complexity data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        raise SyntaxError(f"Syntax error in {file_path}: {e}")

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = calculate_node_complexity(node)
            functions.append({
                'name': node.name,
                'line': node.lineno,
                'complexity': complexity
            })

    return functions


def calculate_node_complexity(node: ast.AST) -> int:
    """
    Calculate complexity for an AST node (function/method).

    Decision points:
    - if, elif
    - for, while
    - and, or (boolean operators)
    - except handlers
    - with statements
    - lambda expressions
    - list/dict/set comprehensions
    """
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        # Control flow
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            complexity += 1
        # Boolean operators
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        # Comprehensions
        elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            complexity += 1
        # Lambda
        elif isinstance(child, ast.Lambda):
            complexity += 1
        # Context managers
        elif isinstance(child, ast.With):
            complexity += 1

    return complexity


def calculate_javascript_complexity(file_path: Path) -> List[Dict[str, Any]]:
    """
    Calculate cyclomatic complexity for JavaScript/TypeScript using regex.

    Note: Less accurate than AST parsing, but avoids external dependencies.

    Args:
        file_path: Path to JS/TS file

    Returns:
        List of function complexity data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    functions = []

    # Find function declarations (simplified regex, may miss edge cases)
    function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'

    # Split by functions (very simplified approach)
    lines = source.split('\n')
    current_function = None
    function_start = 0
    brace_depth = 0

    for line_num, line in enumerate(lines, 1):
        # Check for function declaration
        match = re.search(function_pattern, line)
        if match and brace_depth == 0:
            func_name = match.group(1) or match.group(2)
            current_function = func_name
            function_start = line_num

        # Track brace depth
        brace_depth += line.count('{') - line.count('}')

        # Function ended
        if current_function and brace_depth == 0 and line.count('}') > 0:
            # Extract function body
            function_body = '\n'.join(lines[function_start-1:line_num])
            complexity = calculate_javascript_body_complexity(function_body)

            functions.append({
                'name': current_function,
                'line': function_start,
                'complexity': complexity
            })
            current_function = None

    return functions


def calculate_javascript_body_complexity(body: str) -> int:
    """
    Calculate complexity for JavaScript function body using regex.

    Decision points: if, for, while, case, catch, &&, ||, ? (ternary)
    """
    complexity = 1  # Base complexity

    # Control flow keywords
    complexity += len(re.findall(r'\bif\b', body))
    complexity += len(re.findall(r'\bfor\b', body))
    complexity += len(re.findall(r'\bwhile\b', body))
    complexity += len(re.findall(r'\bcase\b', body))
    complexity += len(re.findall(r'\bcatch\b', body))

    # Logical operators (each adds decision point)
    complexity += len(re.findall(r'&&', body))
    complexity += len(re.findall(r'\|\|', body))

    # Ternary operators
    complexity += len(re.findall(r'\?', body))

    return complexity


def analyze_file(file_path: Path, threshold: int) -> Dict[str, Any]:
    """
    Analyze a single file and return complexity data.

    Args:
        file_path: Path to file
        threshold: Complexity threshold for flagging

    Returns:
        File analysis result
    """
    language = detect_language(file_path)

    if language == 'python':
        functions = calculate_python_complexity(file_path)
    elif language in ('javascript', 'typescript'):
        functions = calculate_javascript_complexity(file_path)
    else:
        raise ValueError(f"Unsupported language for file: {file_path}")

    # Add threshold flags and recommendations
    for func in functions:
        func['exceeds_threshold'] = func['complexity'] > threshold
        if func['exceeds_threshold']:
            func['recommendation'] = "Consider breaking into smaller functions"

    total_complexity = sum(f['complexity'] for f in functions)
    avg_complexity = total_complexity / len(functions) if functions else 0

    return {
        'path': str(file_path),
        'language': language,
        'total_complexity': total_complexity,
        'average_complexity': round(avg_complexity, 1),
        'functions': functions
    }


def detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    suffix = file_path.suffix.lower()

    if suffix == '.py':
        return 'python'
    elif suffix == '.js':
        return 'javascript'
    elif suffix in ('.ts', '.tsx'):
        return 'typescript'
    else:
        raise ValueError(f"Unsupported file extension: {suffix}")


def analyze_directory(directory: Path, threshold: int) -> List[Dict[str, Any]]:
    """
    Analyze all supported files in directory recursively.

    Args:
        directory: Directory to analyze
        threshold: Complexity threshold

    Returns:
        List of file analysis results and errors
    """
    results = []
    errors = []

    # Supported extensions
    patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.tsx']

    for pattern in patterns:
        for file_path in directory.glob(pattern):
            try:
                result = analyze_file(file_path, threshold)
                results.append(result)
            except Exception as e:
                errors.append({
                    'file': str(file_path),
                    'error': str(e),
                    'severity': 'warning',
                    'action': 'Skipped file, continuing with analysis'
                })

    return results, errors


def generate_summary(files: List[Dict[str, Any]], threshold: int) -> Dict[str, Any]:
    """Generate summary statistics from file analysis results."""
    total_files = len(files)
    total_functions = sum(len(f['functions']) for f in files)

    all_complexities = []
    for f in files:
        all_complexities.extend(func['complexity'] for func in f['functions'])

    avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0

    files_exceeding = sum(1 for f in files if any(func['exceeds_threshold'] for func in f['functions']))
    functions_exceeding = sum(
        sum(1 for func in f['functions'] if func['exceeds_threshold'])
        for f in files
    )

    return {
        'total_files': total_files,
        'total_functions': total_functions,
        'average_complexity': round(avg_complexity, 1),
        'files_exceeding_threshold': files_exceeding,
        'functions_exceeding_threshold': functions_exceeding
    }


def main():
    """Main entry point."""
    start_time = time.perf_counter()

    # Check Python version
    if sys.version_info < (3, 11):
        print("Error: Python 3.11+ required", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Calculate cyclomatic complexity for Python, JavaScript, and TypeScript files'
    )
    parser.add_argument('--file', type=str, help='Analyze single file')
    parser.add_argument('--directory', type=str, help='Analyze all files in directory recursively')
    parser.add_argument('--threshold', type=int, default=DEFAULT_THRESHOLD,
                        help=f'Flag functions exceeding complexity threshold (default: {DEFAULT_THRESHOLD})')
    parser.add_argument('--output-format', choices=['json', 'summary'], default='json',
                        help='Output format (default: json)')

    args = parser.parse_args()

    if not args.file and not args.directory:
        parser.error('Either --file or --directory must be specified')

    # Set timeout (Unix only)
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT_SECONDS)

    try:
        errors = []

        if args.file:
            # Single file analysis
            file_path = validate_file_path(args.file)
            files = [analyze_file(file_path, args.threshold)]
        else:
            # Directory analysis
            dir_path = validate_file_path(args.directory)
            if not dir_path.is_dir():
                raise ValueError(f"Not a directory: {args.directory}")
            files, errors = analyze_directory(dir_path, args.threshold)

        # Generate summary
        summary = generate_summary(files, args.threshold)

        # Calculate execution duration
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Output results
        if args.output_format == 'json':
            output = {
                'metadata': {
                    'schema_version': '1.0.0',
                    'script_version': '0.1.0',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'execution_duration_ms': duration_ms
                },
                'summary': summary,
                'files': files
            }
            if errors:
                output['errors'] = errors
            print(json.dumps(output, indent=2))
        else:
            # Summary format
            print(f"Total files: {summary['total_files']}")
            print(f"Total functions: {summary['total_functions']}")
            print(f"Average complexity: {summary['average_complexity']}")
            print(f"Files exceeding threshold: {summary['files_exceeding_threshold']}")
            print(f"Functions exceeding threshold: {summary['functions_exceeding_threshold']}")

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
        # Cancel alarm
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)


if __name__ == '__main__':
    main()
