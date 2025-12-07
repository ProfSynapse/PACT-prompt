# Code Analyzer Scripts

This directory contains analysis scripts for the PACT code analyzer skill.

## Scripts

### js-complexity-analyzer.js

JavaScript/TypeScript cyclomatic complexity analyzer using `typhonjs-escomplex`.

**Supported file types**: `.js`, `.jsx`, `.ts`, `.tsx`

**Installation**:
```bash
cd scripts
npm install
```

**Usage**:
```bash
# Analyze a single file
node js-complexity-analyzer.js --file <path> [--threshold <n>]

# Analyze a directory recursively
node js-complexity-analyzer.js --directory <path> [--threshold <n>]

# Example
node js-complexity-analyzer.js --file src/index.ts --threshold 10
```

**Output**: JSON to stdout matching the Python complexity analyzer format.

**Exit codes**:
- 0: Success
- 1: Fatal error

### complexity_analyzer.py

Python-based complexity analyzer that delegates to language-specific analyzers.

**Supported languages**: Python (native), JavaScript/TypeScript (via js-complexity-analyzer.js)

**Usage**:
```bash
./complexity_analyzer.py --file <path> [--threshold <n>]
./complexity_analyzer.py --directory <path> [--threshold <n>]
```

### Other Scripts

- `coupling_detector.py`: Detects coupling between modules
- `dependency_mapper.py`: Maps dependency relationships
- `file_metrics.py`: Analyzes file-level metrics

## Output Format

All scripts output JSON with the following schema:

```json
{
  "metadata": {
    "schema_version": "1.0.0",
    "script_version": "0.1.0",
    "timestamp": "2025-12-07T12:00:00.000Z",
    "execution_duration_ms": 123
  },
  "summary": {
    "total_files": 1,
    "total_functions": 5,
    "average_complexity": 3.2,
    "functions_exceeding_threshold": 1
  },
  "files": [
    {
      "path": "src/foo.js",
      "language": "javascript",
      "functions": [
        {
          "name": "functionName",
          "line": 10,
          "complexity": 5,
          "exceeds_threshold": false
        }
      ]
    }
  ],
  "errors": []
}
```

## Error Handling

Scripts continue processing on file-level errors and report them in the `errors` array. Fatal errors (e.g., invalid arguments) cause immediate exit with code 1.
