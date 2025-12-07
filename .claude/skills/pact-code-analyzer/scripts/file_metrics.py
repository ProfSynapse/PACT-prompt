#!/usr/bin/env python3
"""
File Metrics Analyzer

Calculates basic file statistics including lines of code, functions, classes,
and comment density. Flags files exceeding PACT 600-line limit.

Security: Path validation, file size limits, timeout handling
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

# Import shared utilities
from utils import (
    TimeoutError,
    SecurityError,
    timeout_handler,
    validate_file_path,
    MAX_FILE_SIZE,
    TIMEOUT_SECONDS
)

# Constants
PACT_LINE_LIMIT = 600


def count_python_elements(file_path: Path, source: str) -> Dict[str, int]:
    """Count functions, classes, and imports in Python file using AST."""
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return {'functions': 0, 'classes': 0, 'imports': 0}

    functions = 0
    classes = 0
    imports = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1
        elif isinstance(node, ast.ClassDef):
            classes += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports += 1

    return {
        'functions': functions,
        'classes': classes,
        'imports': imports
    }


def count_javascript_elements(source: str) -> Dict[str, int]:
    """Count functions, classes, and imports in JavaScript/TypeScript using regex."""
    # Function declarations (including arrow functions and async)
    function_patterns = [
        r'\bfunction\s+\w+',  # function name() {}
        r'\b\w+\s*:\s*function',  # name: function() {}
        r'\b(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?function',  # const name = function() {}
        r'\b(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',  # const name = () => {}
        r'\basync\s+\w+\s*\(',  # async name() {}
    ]

    functions = 0
    for pattern in function_patterns:
        functions += len(re.findall(pattern, source))

    # Class declarations
    class_pattern = r'\bclass\s+\w+'
    classes = len(re.findall(class_pattern, source))

    # Import statements
    import_patterns = [
        r'\bimport\s+.*?from\s+[\'"]',  # import ... from '...'
        r'\bimport\s+[\'"]',  # import '...'
        r'\brequire\([\'"]',  # require('...')
    ]

    imports = 0
    for pattern in import_patterns:
        imports += len(re.findall(pattern, source))

    return {
        'functions': functions,
        'classes': classes,
        'imports': imports
    }


def analyze_line_types(source: str, language: str) -> Dict[str, int]:
    """
    Analyze lines by type: code, comments, blank.

    Args:
        source: File content
        language: Programming language (python, javascript, typescript)

    Returns:
        Dict with counts for each line type
    """
    lines = source.split('\n')
    total_lines = len(lines)
    blank_lines = 0
    comment_lines = 0
    code_lines = 0

    in_multiline_comment = False

    for line in lines:
        stripped = line.strip()

        # Blank line
        if not stripped:
            blank_lines += 1
            continue

        # Language-specific comment detection
        if language == 'python':
            # Python comments
            if stripped.startswith('#'):
                comment_lines += 1
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                comment_lines += 1
                # Check if docstring ends on same line
                if not (stripped.count('"""') == 2 or stripped.count("'''") == 2):
                    in_multiline_comment = not in_multiline_comment
            elif in_multiline_comment:
                comment_lines += 1
                if '"""' in stripped or "'''" in stripped:
                    in_multiline_comment = False
            else:
                code_lines += 1

        elif language in ('javascript', 'typescript'):
            # JavaScript/TypeScript comments
            if stripped.startswith('//'):
                comment_lines += 1
            elif stripped.startswith('/*'):
                comment_lines += 1
                if '*/' not in stripped:
                    in_multiline_comment = True
            elif in_multiline_comment:
                comment_lines += 1
                if '*/' in stripped:
                    in_multiline_comment = False
            else:
                code_lines += 1
        else:
            # Unknown language, count as code
            code_lines += 1

    return {
        'total_lines': total_lines,
        'code_lines': code_lines,
        'comment_lines': comment_lines,
        'blank_lines': blank_lines
    }


def analyze_file(file_path: Path, language: str) -> Dict[str, Any]:
    """
    Analyze a single file and return metrics.

    Args:
        file_path: Path to file
        language: Programming language

    Returns:
        File metrics dict
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # Line analysis
    line_metrics = analyze_line_types(source, language)

    # Element counting
    if language == 'python':
        elements = count_python_elements(file_path, source)
    elif language in ('javascript', 'typescript'):
        elements = count_javascript_elements(source)
    else:
        elements = {'functions': 0, 'classes': 0, 'imports': 0}

    # PACT compliance check
    exceeds_limit = line_metrics['total_lines'] > PACT_LINE_LIMIT

    recommendation = (
        f"File exceeds PACT {PACT_LINE_LIMIT}-line limit. Consider splitting into smaller modules."
        if exceeds_limit
        else "File size is acceptable"
    )

    return {
        'path': str(file_path),
        'language': language,
        **line_metrics,
        **elements,
        'exceeds_size_limit': exceeds_limit,
        'size_limit': PACT_LINE_LIMIT,
        'recommendation': recommendation
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


def analyze_directory(directory: Path, language: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyze all supported files in directory recursively.

    Args:
        directory: Directory to analyze
        language: Optional language filter (analyze only this language)

    Returns:
        List of file analysis results and errors
    """
    results = []
    errors = []

    # Determine patterns based on language filter
    if language == 'python':
        patterns = ['**/*.py']
    elif language == 'javascript':
        patterns = ['**/*.js']
    elif language == 'typescript':
        patterns = ['**/*.ts', '**/*.tsx']
    else:
        # All supported languages
        patterns = ['**/*.py', '**/*.js', '**/*.ts', '**/*.tsx']

    for pattern in patterns:
        for file_path in directory.glob(pattern):
            try:
                detected_lang = detect_language(file_path)
                result = analyze_file(file_path, detected_lang)
                results.append(result)
            except Exception as e:
                errors.append({
                    'file': str(file_path),
                    'error': str(e),
                    'severity': 'warning',
                    'action': 'Skipped file, continuing with analysis'
                })

    return results, errors


def generate_summary(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from file analysis results."""
    if not files:
        return {
            'total_files': 0,
            'total_lines': 0,
            'total_code_lines': 0,
            'total_comment_lines': 0,
            'total_blank_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'average_file_size': 0,
            'files_exceeding_limit': 0
        }

    total_files = len(files)
    total_lines = sum(f['total_lines'] for f in files)
    total_code = sum(f['code_lines'] for f in files)
    total_comments = sum(f['comment_lines'] for f in files)
    total_blank = sum(f['blank_lines'] for f in files)
    total_functions = sum(f['functions'] for f in files)
    total_classes = sum(f['classes'] for f in files)
    files_exceeding = sum(1 for f in files if f['exceeds_size_limit'])

    avg_file_size = total_lines / total_files if total_files else 0

    return {
        'total_files': total_files,
        'total_lines': total_lines,
        'total_code_lines': total_code,
        'total_comment_lines': total_comments,
        'total_blank_lines': total_blank,
        'total_functions': total_functions,
        'total_classes': total_classes,
        'average_file_size': round(avg_file_size, 1),
        'files_exceeding_limit': files_exceeding
    }


def main():
    """Main entry point."""
    start_time = time.perf_counter()

    if sys.version_info < (3, 11):
        print("Error: Python 3.11+ required", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description='Calculate file statistics (LOC, functions, classes, comments)'
    )
    parser.add_argument('--file', type=str, help='Analyze single file')
    parser.add_argument('--directory', type=str, help='Analyze all files in directory')
    parser.add_argument('--language', choices=['python', 'javascript', 'typescript'],
                        help='Filter by language (optional)')

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
            language = args.language or detect_language(file_path)
            files = [analyze_file(file_path, language)]
        else:
            # Directory analysis
            dir_path = validate_file_path(args.directory)
            if not dir_path.is_dir():
                raise ValueError(f"Not a directory: {args.directory}")
            files, errors = analyze_directory(dir_path, args.language)

        # Generate summary
        summary = generate_summary(files)

        # Calculate execution duration
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Output results
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
