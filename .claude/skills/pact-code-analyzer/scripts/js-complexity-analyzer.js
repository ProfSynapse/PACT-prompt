#!/usr/bin/env node
/**
 * Location: /Users/mj/Sites/collab/PACT-prompt/skills/pact-code-analyzer/scripts/js-complexity-analyzer.js
 *
 * Analyzes cyclomatic complexity of JavaScript files using acorn for AST parsing.
 * Supports .js files (ES6+ modules and CommonJS).
 *
 * Used by: Python complexity analyzer (complexity_analyzer.py) for JavaScript files
 * Dependencies: acorn, acorn-walk
 *
 * Usage:
 *   node js-complexity-analyzer.js --file <path> [--threshold <n>]
 *   node js-complexity-analyzer.js --directory <path> [--threshold <n>]
 *
 * Output: JSON to stdout matching Python script format
 * Exit codes: 0 = success, 1 = error
 *
 * Limitations:
 *   - JSX files (.jsx) require acorn-jsx plugin (not currently supported)
 *   - TypeScript files (.ts, .tsx) require different parser (not currently supported)
 *
 * Cyclomatic Complexity Calculation:
 *   Base complexity: 1
 *   Decision points (+1 each):
 *     - if statements
 *     - for, while, do-while loops
 *     - case in switch statements
 *     - catch blocks
 *     - Logical && and || operators
 *     - Ternary ?: operators
 *     - Nullish coalescing ?? operators
 */

import { Parser } from 'acorn';
import * as walk from 'acorn-walk';
import fs from 'fs/promises';
import path from 'path';

// Supported file extensions (.js only - JSX and TypeScript not yet supported)
const SUPPORTED_EXTENSIONS = ['.js'];

// Default complexity threshold
const DEFAULT_THRESHOLD = 10;

// Script version
const SCRIPT_VERSION = '0.1.0';

/**
 * Parse command line arguments
 * @returns {Object} Parsed arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {
    file: null,
    directory: null,
    threshold: DEFAULT_THRESHOLD
  };

  for (let i = 0; i < args.length; i += 2) {
    const flag = args[i];
    const value = args[i + 1];

    switch (flag) {
      case '--file':
        parsed.file = value;
        break;
      case '--directory':
        parsed.directory = value;
        break;
      case '--threshold':
        parsed.threshold = parseInt(value, 10);
        if (isNaN(parsed.threshold)) {
          throw new Error(`Invalid threshold value: ${value}`);
        }
        break;
      default:
        throw new Error(`Unknown argument: ${flag}`);
    }
  }

  if (!parsed.file && !parsed.directory) {
    throw new Error('Either --file or --directory must be specified');
  }

  if (parsed.file && parsed.directory) {
    throw new Error('Cannot specify both --file and --directory');
  }

  return parsed;
}

/**
 * Determine language from file extension
 * @param {string} filePath - Path to file
 * @returns {string} Language identifier (always 'javascript' for .js files)
 */
function getLanguage(filePath) {
  return 'javascript';
}

/**
 * Calculate cyclomatic complexity for a function node
 * Walks the function body and counts decision points
 * Excludes decision points in nested functions (they have their own complexity)
 *
 * @param {Object} node - AST node representing a function
 * @returns {number} Cyclomatic complexity (starts at 1, adds 1 for each decision point)
 */
function calculateComplexity(node) {
  let complexity = 1; // Base complexity

  // Custom walker that stops at nested function boundaries
  walk.ancestor(node, {
    // if statements (+1)
    IfStatement(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // for loops (+1)
    ForStatement(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // for-in loops (+1)
    ForInStatement(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // for-of loops (+1)
    ForOfStatement(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // while loops (+1)
    WhileStatement(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // do-while loops (+1)
    DoWhileStatement(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // switch case statements (+1 per case)
    SwitchCase(node, ancestors) {
      // Don't count default case as it doesn't add a decision
      if (node.test !== null && !isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // catch blocks (+1)
    CatchClause(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // Ternary operators (+1)
    ConditionalExpression(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        complexity++;
      }
    },

    // Logical operators (&& and ||) (+1 each)
    LogicalExpression(node, ancestors) {
      if (!isInNestedFunction(node, ancestors)) {
        if (node.operator === '&&' || node.operator === '||') {
          complexity++;
        }
        // Note: Nullish coalescing (??) is also a LogicalExpression in acorn
        if (node.operator === '??') {
          complexity++;
        }
      }
    }
  });

  return complexity;
}

/**
 * Check if a node is inside a nested function
 * Used to exclude nested function complexity from parent function
 *
 * @param {Object} node - Current AST node
 * @param {Array} ancestors - Ancestor nodes from walk.ancestor
 * @returns {boolean} True if node is in a nested function
 */
function isInNestedFunction(node, ancestors) {
  // The ancestors array includes the root function node at index 0
  // If we find any function nodes in ancestors (excluding index 0), it's nested
  for (let i = 1; i < ancestors.length; i++) {
    const ancestor = ancestors[i];
    if (
      ancestor.type === 'FunctionDeclaration' ||
      ancestor.type === 'FunctionExpression' ||
      ancestor.type === 'ArrowFunctionExpression'
    ) {
      return true;
    }
  }
  return false;
}

/**
 * Extract function name from AST node
 * Handles various function types: declarations, expressions, arrow functions, methods
 *
 * @param {Object} node - AST node (the function itself)
 * @param {Object} parent - Direct parent AST node
 * @param {Array} ancestors - Full ancestor chain (from walk.ancestor)
 * @returns {string} Function name or '<anonymous>' for unnamed functions
 */
function getFunctionName(node, parent, ancestors) {
  // Function declarations have a direct id
  if (node.type === 'FunctionDeclaration' && node.id) {
    return node.id.name;
  }

  // Function expression with name: const x = function foo() {}
  if (node.id) {
    return node.id.name;
  }

  // Search up the ancestor chain for naming context
  if (ancestors && ancestors.length > 0) {
    // Look through ancestors from most recent to oldest
    for (let i = ancestors.length - 1; i >= 0; i--) {
      const ancestor = ancestors[i];

      // Variable declarator: const foo = () => {}
      if (ancestor.type === 'VariableDeclarator' && ancestor.id && ancestor.id.name) {
        return ancestor.id.name;
      }

      // Assignment expression: foo = () => {}
      if (ancestor.type === 'AssignmentExpression' && ancestor.left && ancestor.left.type === 'Identifier') {
        return ancestor.left.name;
      }

      // Object method shorthand: { foo() {} }
      if (ancestor.type === 'Property' && ancestor.key) {
        return ancestor.key.name || ancestor.key.value;
      }

      // Class method: class { foo() {} }
      if (ancestor.type === 'MethodDefinition' && ancestor.key) {
        return ancestor.key.name || ancestor.key.value;
      }
    }
  }

  // Fallback to direct parent (shouldn't reach here if ancestors work)
  if (parent) {
    if (parent.type === 'VariableDeclarator' && parent.id) {
      return parent.id.name;
    }
    if (parent.type === 'AssignmentExpression' && parent.left && parent.left.type === 'Identifier') {
      return parent.left.name;
    }
    if (parent.type === 'Property' && parent.key) {
      return parent.key.name || parent.key.value;
    }
    if (parent.type === 'MethodDefinition' && parent.key) {
      return parent.key.name || parent.key.value;
    }
  }

  return '<anonymous>';
}

/**
 * Extract all functions from AST with their complexity
 * Uses acorn-walk to traverse the AST and find all function nodes
 *
 * @param {Object} ast - Parsed AST
 * @returns {Array} Array of function analysis results
 */
function extractFunctions(ast, threshold) {
  const functions = [];

  // Use ancestor walker to get full ancestry chain for each function
  walk.ancestor(ast, {
    // Function declarations: function foo() {}
    FunctionDeclaration(node, ancestors) {
      const complexity = calculateComplexity(node);
      const parent = ancestors.length > 0 ? ancestors[ancestors.length - 1] : null;
      functions.push({
        name: getFunctionName(node, parent, ancestors),
        line: node.loc ? node.loc.start.line : 0,
        complexity: complexity,
        exceeds_threshold: complexity > threshold
      });
    },

    // Function expressions: const foo = function() {}
    FunctionExpression(node, ancestors) {
      const complexity = calculateComplexity(node);
      const parent = ancestors.length > 0 ? ancestors[ancestors.length - 1] : null;
      functions.push({
        name: getFunctionName(node, parent, ancestors),
        line: node.loc ? node.loc.start.line : 0,
        complexity: complexity,
        exceeds_threshold: complexity > threshold
      });
    },

    // Arrow functions: const foo = () => {}
    ArrowFunctionExpression(node, ancestors) {
      const complexity = calculateComplexity(node);
      const parent = ancestors.length > 0 ? ancestors[ancestors.length - 1] : null;
      functions.push({
        name: getFunctionName(node, parent, ancestors),
        line: node.loc ? node.loc.start.line : 0,
        complexity: complexity,
        exceeds_threshold: complexity > threshold
      });
    }
  });

  return functions;
}

/**
 * Analyze a single JavaScript file
 * Parses the file with acorn and extracts function complexity
 *
 * @param {string} filePath - Path to file
 * @param {number} threshold - Complexity threshold
 * @returns {Object} Analysis result for the file
 */
async function analyzeFile(filePath, threshold) {
  try {
    const code = await fs.readFile(filePath, 'utf-8');

    // Parse with acorn
    // Using ecmaVersion: 'latest' for ES6+ support
    // sourceType: 'module' for import/export statements
    const ast = Parser.parse(code, {
      ecmaVersion: 'latest',
      sourceType: 'module',
      locations: true // Include line/column info
    });

    // Extract functions and their complexity
    const functions = extractFunctions(ast, threshold);

    return {
      path: filePath,
      language: getLanguage(filePath),
      functions,
      error: null
    };
  } catch (error) {
    return {
      path: filePath,
      language: getLanguage(filePath),
      functions: [],
      error: error.message
    };
  }
}

/**
 * Recursively find all supported files in a directory
 * Skips node_modules, dist, build, .git directories
 *
 * @param {string} dirPath - Directory path
 * @returns {Promise<string[]>} Array of file paths
 */
async function findFiles(dirPath) {
  const files = [];

  async function traverse(currentPath) {
    try {
      const entries = await fs.readdir(currentPath, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(currentPath, entry.name);

        if (entry.isDirectory()) {
          // Skip node_modules and other common build directories
          if (!['node_modules', 'dist', 'build', '.git', 'coverage'].includes(entry.name)) {
            await traverse(fullPath);
          }
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name).toLowerCase();
          if (SUPPORTED_EXTENSIONS.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    } catch (error) {
      // Skip directories we can't read
    }
  }

  await traverse(dirPath);
  return files;
}

/**
 * Calculate summary statistics from file analysis results
 *
 * @param {Array} fileResults - Array of file analysis results
 * @returns {Object} Summary statistics
 */
function calculateSummary(fileResults) {
  let totalFunctions = 0;
  let totalComplexity = 0;
  let functionsExceedingThreshold = 0;

  for (const file of fileResults) {
    for (const func of file.functions) {
      totalFunctions++;
      totalComplexity += func.complexity;
      if (func.exceeds_threshold) {
        functionsExceedingThreshold++;
      }
    }
  }

  return {
    total_files: fileResults.length,
    total_functions: totalFunctions,
    average_complexity: totalFunctions > 0 ? totalComplexity / totalFunctions : 0,
    functions_exceeding_threshold: functionsExceedingThreshold
  };
}

/**
 * Main execution function
 * Parses arguments, analyzes files, outputs JSON results
 */
async function main() {
  const startTime = Date.now();

  try {
    // Parse arguments
    const args = parseArgs();
    const threshold = args.threshold;

    // Get list of files to analyze
    let filePaths;
    if (args.file) {
      filePaths = [args.file];
    } else {
      filePaths = await findFiles(args.directory);
    }

    // Analyze all files
    const fileResults = [];
    const errors = [];

    for (const filePath of filePaths) {
      const result = await analyzeFile(filePath, threshold);

      if (result.error) {
        errors.push({
          file: result.path,
          error: result.error
        });
      }

      // Always include the file result, even if there was an error
      fileResults.push({
        path: result.path,
        language: result.language,
        functions: result.functions
      });
    }

    // Calculate summary
    const summary = calculateSummary(fileResults);

    // Build output
    const output = {
      metadata: {
        schema_version: '1.0.0',
        script_version: SCRIPT_VERSION,
        timestamp: new Date().toISOString(),
        execution_duration_ms: Date.now() - startTime
      },
      summary,
      files: fileResults,
      errors
    };

    // Output JSON to stdout
    console.log(JSON.stringify(output, null, 2));
    process.exit(0);

  } catch (error) {
    // Fatal error - output error JSON and exit with code 1
    const output = {
      metadata: {
        schema_version: '1.0.0',
        script_version: SCRIPT_VERSION,
        timestamp: new Date().toISOString(),
        execution_duration_ms: Date.now() - startTime
      },
      summary: {
        total_files: 0,
        total_functions: 0,
        average_complexity: 0,
        functions_exceeding_threshold: 0
      },
      files: [],
      errors: [
        {
          file: null,
          error: error.message
        }
      ]
    };

    console.error(JSON.stringify(output, null, 2));
    process.exit(1);
  }
}

// Run main function
main();
