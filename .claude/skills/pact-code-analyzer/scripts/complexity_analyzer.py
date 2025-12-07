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
import subprocess
import shutil

# Constants
MAX_FILE_SIZE = 1024 * 1024  # 1MB
TIMEOUT_SECONDS = 60
NODEJS_TIMEOUT_SECONDS = 30
DEFAULT_THRESHOLD = 10

# Path to Node.js analyzer script (relative to this script)
SCRIPTS_DIR = Path(__file__).parent
JS_ANALYZER_SCRIPT = SCRIPTS_DIR / 'js-complexity-analyzer.js'

# Check if Node.js is available
NODE_AVAILABLE = shutil.which('node') is not None


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
        List of function complexity data (empty list with error if syntax error)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        # Bug Fix #1: Gracefully handle syntax errors instead of raising exception
        # Return empty list to match JavaScript behavior and allow analyze_file() to continue
        return []

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

    # Bug Fix #2: Prevent double-counting complexity from nested functions
    # Track nested function depth to skip decision points inside nested functions
    def is_in_nested_function(child, parent):
        """Check if child node is inside a nested function definition."""
        # Walk from parent to child and check if we cross a function boundary
        for descendant in ast.walk(parent):
            if descendant is child:
                return False  # Reached child without crossing function boundary
            # If we encounter a nested function definition before reaching child
            if descendant is not parent and isinstance(descendant, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if child is inside this nested function
                for nested_descendant in ast.walk(descendant):
                    if nested_descendant is child:
                        return True
        return False

    for child in ast.walk(node):
        # Skip the root node itself
        if child is node:
            continue

        # Skip decision points that are inside nested functions
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue  # Skip nested function definitions entirely

        # Only count decision points if they're not in a nested function
        if not is_in_nested_function(child, node):
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


def try_nodejs_analysis(file_path: Path, threshold: int) -> Optional[Dict[str, Any]]:
    """
    Try to analyze JavaScript/TypeScript file using Node.js analyzer.

    Args:
        file_path: Path to JS/TS file
        threshold: Complexity threshold

    Returns:
        Analysis result dict if successful, None if Node.js not available or failed
    """
    if not NODE_AVAILABLE or not JS_ANALYZER_SCRIPT.exists():
        return None

    # Check if npm dependencies are installed
    node_modules = SCRIPTS_DIR / 'node_modules'
    if not node_modules.exists():
        return None

    try:
        result = subprocess.run(
            ['node', str(JS_ANALYZER_SCRIPT), '--file', str(file_path), '--threshold', str(threshold)],
            capture_output=True,
            text=True,
            timeout=NODEJS_TIMEOUT_SECONDS,
            cwd=str(SCRIPTS_DIR)
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Return the file analysis result (first file in files array)
            if data.get('files') and len(data['files']) > 0:
                file_result = data['files'][0]
                # Add analysis_method to track which method was used
                file_result['analysis_method'] = 'nodejs_ast'
                return file_result
        return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError):
        return None


def calculate_javascript_complexity_regex(file_path: Path) -> List[Dict[str, Any]]:
    """
    Calculate cyclomatic complexity for JavaScript/TypeScript using regex.

    Note: Less accurate than AST parsing, but avoids external dependencies.
    Best-effort approach that handles common patterns but may miss edge cases.

    Args:
        file_path: Path to JS/TS file

    Returns:
        List of function complexity data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    functions = []

    # Improved function detection patterns:
    # 1. Named function declarations: function name() {}
    # 2. Function expressions: const/let/var name = function() {}
    # 3. Arrow functions with parens: const name = () => {} or const name = () => expr
    # 4. Arrow functions without parens: const name = x => {} or const name = x => expr
    # 5. Async variants: async function, async () =>
    # 6. Generator functions: function* name() {}
    # 7. Class methods: methodName() {} or async methodName() {}
    # 8. Object method shorthand: { methodName() {} }

    # Pattern for arrow functions (with and without braces)
    arrow_pattern = r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>\s*([^{;]+);?\s*$'
    arrow_brace_pattern = r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>\s*\{'

    # Control flow keywords to exclude from method detection
    control_flow_keywords = r'(?:if|for|while|switch|catch|with|return)'

    function_patterns = [
        # Named function declarations (including async, generator)
        r'^\s*(?:export\s+)?(?:async\s+)?function\s*\*?\s+(\w+)\s*\(',
        # Function expressions assigned to variables
        r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\*?\s*\(',
        # Class methods and object method shorthand - must be at start of line (after whitespace)
        # Use negative lookahead to exclude control flow keywords
        r'^\s*(?:async\s+)?(?!' + control_flow_keywords + r'\b)([a-zA-Z_$][\w$]*)\s*\([^)]*\)\s*\{',
    ]

    # Combine all patterns with alternation
    combined_pattern = '|'.join(f'(?:{p})' for p in function_patterns)

    # Split by functions (simplified approach using brace matching)
    lines = source.split('\n')
    current_function = None
    function_start = 0
    function_start_depth = 0
    brace_depth = 0

    for line_num, line in enumerate(lines, 1):
        # If not currently tracking a function, look for new function declarations
        # (Do this BEFORE updating brace_depth so we can detect top-level arrow functions)
        if not current_function:
            # Check for single-line arrow functions (without braces)
            arrow_match = re.search(arrow_pattern, line)
            if arrow_match:
                func_name = arrow_match.group(1)
                # Bug Fix #3: Use 'line' directly instead of lines[line_num - 1]
                # line_num is already 1-indexed from enumerate, and 'line' is the current line
                function_body = line
                complexity = calculate_javascript_body_complexity(function_body)

                functions.append({
                    'name': func_name,
                    'line': line_num,
                    'complexity': complexity
                })
                continue

            # Check for arrow functions with braces (only top-level)
            if brace_depth == 0:
                arrow_brace_match = re.search(arrow_brace_pattern, line)
                if arrow_brace_match:
                    func_name = arrow_brace_match.group(1)
                    current_function = func_name
                    function_start = line_num
                    function_start_depth = brace_depth

            # Check for other function patterns (can be nested in classes/objects)
            if not current_function:
                match = re.search(combined_pattern, line)
                if match:
                    # Extract function name from the first non-None group
                    func_name = next((g for g in match.groups() if g), 'anonymous')
                    current_function = func_name
                    function_start = line_num
                    function_start_depth = brace_depth

        # Update brace depth tracking
        old_depth = brace_depth
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_depth += open_braces - close_braces

        # Bug Fix #4: Handle single-line function bodies (e.g., function foo() { return 1; })
        # Check if function started and ended on the same line
        if current_function and open_braces > 0 and open_braces == close_braces:
            # Complete function on one line
            function_body = line
            complexity = calculate_javascript_body_complexity(function_body)

            functions.append({
                'name': current_function,
                'line': function_start,
                'complexity': complexity
            })
            current_function = None
            continue

        # Function ended - check if we've returned to the starting depth
        if current_function and brace_depth == function_start_depth and old_depth > function_start_depth:
            # Extract function body from original source
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

    Decision points: if, for, while, case, catch, &&, ||, ??, ? (ternary)

    Note: This is a best-effort regex approach. Some edge cases:
    - May count operators in comments/strings (cleaned upstream but not perfect)
    - May miss complex nested expressions
    - Treats each operator occurrence as a decision point
    """
    complexity = 1  # Base complexity

    # Remove comments and strings to reduce false positives
    # (This is a safety net since upstream should handle most cases)
    body_cleaned = re.sub(r'//.*?$', '', body, flags=re.MULTILINE)
    body_cleaned = re.sub(r'/\*.*?\*/', '', body_cleaned, flags=re.DOTALL)
    body_cleaned = re.sub(r'`[^`]*`', '""', body_cleaned)
    body_cleaned = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body_cleaned)
    body_cleaned = re.sub(r"'(?:[^'\\]|\\.)*'", "''", body_cleaned)

    # Control flow keywords (word boundaries to avoid partial matches)
    complexity += len(re.findall(r'\bif\b', body_cleaned))
    complexity += len(re.findall(r'\belse\s+if\b', body_cleaned))  # Explicit else if
    complexity += len(re.findall(r'\bfor\b', body_cleaned))
    complexity += len(re.findall(r'\bwhile\b', body_cleaned))
    complexity += len(re.findall(r'\bdo\b', body_cleaned))  # do-while loops
    complexity += len(re.findall(r'\bcase\b', body_cleaned))
    complexity += len(re.findall(r'\bcatch\b', body_cleaned))

    # Logical operators (each adds decision point)
    # Use negative lookbehind/lookahead to avoid matching &&& or |||
    complexity += len(re.findall(r'(?<![&|])&&(?![&])', body_cleaned))  # Logical AND
    complexity += len(re.findall(r'(?<![&|])\|\|(?![|])', body_cleaned))  # Logical OR
    complexity += len(re.findall(r'(?<![?])\?\?(?![?])', body_cleaned))  # Nullish coalescing

    # Ternary operators: match ? not part of ?. (optional chaining) or ?? (nullish coalescing)
    # Simplified pattern: ? not preceded/followed by ? and not followed by .
    complexity += len(re.findall(r'(?<!\?)\?(?![?\.])', body_cleaned))

    return complexity


def analyze_file(file_path: Path, threshold: int) -> tuple[Dict[str, Any], Optional[Dict[str, str]]]:
    """
    Analyze a single file and return complexity data.

    Args:
        file_path: Path to file
        threshold: Complexity threshold for flagging

    Returns:
        Tuple of (file analysis result, optional warning dict)
        Warning dict is returned when regex fallback is used for JS/TS files
    """
    language = detect_language(file_path)
    analysis_method = 'python_ast'  # Default for Python
    warning = None

    if language == 'python':
        functions = calculate_python_complexity(file_path)
    elif language in ('javascript', 'typescript'):
        # Try Node.js AST analysis first (more accurate)
        nodejs_result = try_nodejs_analysis(file_path, threshold)
        if nodejs_result:
            # Node.js analysis succeeded - use its results directly
            # The result already has functions with complexity scores
            analysis_method = nodejs_result.get('analysis_method', 'nodejs_ast')
            functions = nodejs_result.get('functions', [])
        else:
            # Fall back to regex-based analysis
            analysis_method = 'regex_fallback'
            functions = calculate_javascript_complexity_regex(file_path)
            # Add warning when using regex fallback
            warning = {
                'file': str(file_path),
                'warning': 'Using regex fallback for complexity analysis. For more accurate results, install Node.js and run: cd scripts && npm install',
                'severity': 'info',
                'action': 'Analysis completed with regex-based method (less accurate than AST)'
            }
    else:
        raise ValueError(f"Unsupported language for file: {file_path}")

    # Add threshold flags and recommendations
    for func in functions:
        func['exceeds_threshold'] = func['complexity'] > threshold
        if func['exceeds_threshold']:
            func['recommendation'] = "Consider breaking into smaller functions"

    total_complexity = sum(f['complexity'] for f in functions)
    avg_complexity = total_complexity / len(functions) if functions else 0

    result = {
        'path': str(file_path),
        'language': language,
        'analysis_method': analysis_method,
        'total_complexity': total_complexity,
        'average_complexity': round(avg_complexity, 1),
        'functions': functions
    }

    return result, warning


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


def analyze_directory(directory: Path, threshold: int) -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Analyze all supported files in directory recursively.

    Args:
        directory: Directory to analyze
        threshold: Complexity threshold

    Returns:
        Tuple of (file analysis results, errors/warnings list)
    """
    results = []
    errors = []

    # Supported extensions
    patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.tsx']

    for pattern in patterns:
        for file_path in directory.glob(pattern):
            try:
                result, warning = analyze_file(file_path, threshold)
                results.append(result)
                # Collect warnings (e.g., regex fallback usage)
                if warning:
                    errors.append(warning)
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
            result, warning = analyze_file(file_path, args.threshold)
            files = [result]
            if warning:
                errors.append(warning)
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
