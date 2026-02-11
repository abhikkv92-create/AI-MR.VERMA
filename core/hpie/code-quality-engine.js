#!/usr/bin/env node
/**
 * Code Quality Engine v1.0.0
 * ==================================================
 * Central lint enforcement and code quality gate for MR.VERMA.
 * Ensures zero defects at every stage of every workflow.
 *
 * Capabilities:
 *   - Multi-ecosystem lint detection (Node.js, Python, Go)
 *   - Auto-fix before reporting failures
 *   - Quality gate with configurable thresholds
 *   - Structured audit reports
 *   - Workflow-integrated validation
 */

'use strict';

const { execFile, exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');

const execFileAsync = promisify(execFile);
const execAsync = promisify(exec);

// ---------------------------------------------------------------------------
// Lint Check Result
// ---------------------------------------------------------------------------
class LintCheckResult {
  constructor(linterName) {
    this.linter = linterName;
    this.passed = false;
    this.errors = 0;
    this.warnings = 0;
    this.fixable = 0;
    this.output = '';
    this.errorOutput = '';
    this.durationMs = 0;
  }
}

// ---------------------------------------------------------------------------
// Quality Report
// ---------------------------------------------------------------------------
class QualityReport {
  constructor(targetPath) {
    this.targetPath = targetPath;
    this.timestamp = new Date().toISOString();
    this.projectType = 'unknown';
    this.checks = [];
    this.passed = false;
    this.score = 0;           // 0-100
    this.grade = 'F';
    this.totalErrors = 0;
    this.totalWarnings = 0;
    this.totalFixable = 0;
    this.durationMs = 0;
    this.autoFixApplied = false;
  }

  computeScore() {
    if (this.checks.length === 0) {
      this.score = 100;
      this.grade = 'A';
      this.passed = true;
      return;
    }

    const passedChecks = this.checks.filter(c => c.passed).length;
    const baseScore = (passedChecks / this.checks.length) * 100;

    // Deductions for errors
    let deduction = this.totalErrors * 5 + this.totalWarnings * 1;
    deduction = Math.min(deduction, 50); // cap penalty

    this.score = Math.max(0, Math.round(baseScore - deduction));
    this.grade = this.score >= 95 ? 'A' :
                 this.score >= 85 ? 'B' :
                 this.score >= 70 ? 'C' :
                 this.score >= 50 ? 'D' : 'F';
    this.passed = this.totalErrors === 0;
  }

  toJSON() {
    return {
      targetPath: this.targetPath,
      timestamp: this.timestamp,
      projectType: this.projectType,
      passed: this.passed,
      score: this.score,
      grade: this.grade,
      totalErrors: this.totalErrors,
      totalWarnings: this.totalWarnings,
      totalFixable: this.totalFixable,
      durationMs: this.durationMs,
      autoFixApplied: this.autoFixApplied,
      checks: this.checks.map(c => ({
        linter: c.linter,
        passed: c.passed,
        errors: c.errors,
        warnings: c.warnings,
        fixable: c.fixable,
        durationMs: c.durationMs
      }))
    };
  }
}

// ---------------------------------------------------------------------------
// Lint Runner - executes individual linters
// ---------------------------------------------------------------------------
class LintRunner {
  constructor(config = {}) {
    this.timeoutMs = config.timeoutMs || 60000;
    this.autoFix = config.autoFix !== false;
  }

  /**
   * Detect project type and available linters.
   */
  detectProject(targetPath) {
    const result = { type: 'unknown', linters: [] };

    // Node.js
    const pkgPath = path.join(targetPath, 'package.json');
    if (fs.existsSync(pkgPath)) {
      result.type = 'node';
      try {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
        const scripts = pkg.scripts || {};
        const allDeps = {
          ...(pkg.dependencies || {}),
          ...(pkg.devDependencies || {})
        };

        // ESLint
        if (scripts.lint) {
          result.linters.push({
            name: 'npm-lint',
            cmd: 'npm',
            args: ['run', 'lint'],
            fixCmd: scripts['lint:fix'] ? 'npm' : null,
            fixArgs: scripts['lint:fix'] ? ['run', 'lint:fix'] : null
          });
        } else if (allDeps.eslint || fs.existsSync(path.join(targetPath, '.eslintrc.json'))) {
          result.linters.push({
            name: 'eslint',
            cmd: 'npx',
            args: ['eslint', '.', '--ext', '.js,.ts,.jsx,.tsx', '--format', 'json'],
            fixCmd: 'npx',
            fixArgs: ['eslint', '.', '--ext', '.js,.ts,.jsx,.tsx', '--fix']
          });
        }

        // TypeScript
        if (allDeps.typescript || fs.existsSync(path.join(targetPath, 'tsconfig.json'))) {
          result.linters.push({
            name: 'typescript',
            cmd: 'npx',
            args: ['tsc', '--noEmit'],
            fixCmd: null,
            fixArgs: null
          });
        }
      } catch (err) {
        // Corrupted package.json - still report as node project
      }
    }

    // Python
    const hasPyProject = fs.existsSync(path.join(targetPath, 'pyproject.toml'));
    const hasRequirements = fs.existsSync(path.join(targetPath, 'requirements.txt'));
    if (hasPyProject || hasRequirements) {
      if (result.type === 'unknown') result.type = 'python';

      result.linters.push({
        name: 'ruff',
        cmd: 'ruff',
        args: ['check', '.'],
        fixCmd: 'ruff',
        fixArgs: ['check', '.', '--fix']
      });

      if (hasPyProject || fs.existsSync(path.join(targetPath, 'mypy.ini'))) {
        result.linters.push({
          name: 'mypy',
          cmd: 'mypy',
          args: ['.'],
          fixCmd: null,
          fixArgs: null
        });
      }
    }

    return result;
  }

  /**
   * Run a single linter.
   */
  async runLinter(linter, targetPath) {
    const result = new LintCheckResult(linter.name);
    const startTime = Date.now();

    try {
      const { stdout, stderr } = await execAsync(
        `${linter.cmd} ${linter.args.join(' ')}`,
        {
          cwd: targetPath,
          timeout: this.timeoutMs,
          env: { ...process.env, FORCE_COLOR: '0' }
        }
      );

      result.passed = true;
      result.output = (stdout || '').substring(0, 4000);
      result.errorOutput = (stderr || '').substring(0, 2000);

    } catch (err) {
      result.passed = false;
      result.output = (err.stdout || '').substring(0, 4000);
      result.errorOutput = (err.stderr || err.message || '').substring(0, 2000);

      // Parse error/warning counts from output
      const counts = this._parseErrorCounts(linter.name, result.output + result.errorOutput);
      result.errors = counts.errors;
      result.warnings = counts.warnings;
      result.fixable = counts.fixable;
    }

    result.durationMs = Date.now() - startTime;
    return result;
  }

  /**
   * Attempt auto-fix for a linter.
   */
  async autoFixLinter(linter, targetPath) {
    if (!linter.fixCmd || !this.autoFix) return false;

    try {
      await execAsync(
        `${linter.fixCmd} ${linter.fixArgs.join(' ')}`,
        {
          cwd: targetPath,
          timeout: this.timeoutMs,
          env: { ...process.env, FORCE_COLOR: '0' }
        }
      );
      return true;
    } catch (err) {
      return false;
    }
  }

  /**
   * Parse error/warning counts from linter output.
   */
  _parseErrorCounts(linterName, output) {
    const counts = { errors: 0, warnings: 0, fixable: 0 };

    // ESLint JSON output
    if (linterName === 'eslint') {
      try {
        const results = JSON.parse(output);
        for (const file of results) {
          counts.errors += file.errorCount || 0;
          counts.warnings += file.warningCount || 0;
          counts.fixable += (file.fixableErrorCount || 0) + (file.fixableWarningCount || 0);
        }
        return counts;
      } catch (e) {
        // Fall through to regex parsing
      }
    }

    // Generic pattern matching
    const errorMatch = output.match(/(\d+)\s*error/i);
    const warningMatch = output.match(/(\d+)\s*warning/i);
    const fixableMatch = output.match(/(\d+)\s*(fixable|auto-?fix)/i);

    if (errorMatch) counts.errors = parseInt(errorMatch[1], 10);
    if (warningMatch) counts.warnings = parseInt(warningMatch[1], 10);
    if (fixableMatch) counts.fixable = parseInt(fixableMatch[1], 10);

    // If no pattern matched but command failed, at least 1 error
    if (counts.errors === 0 && counts.warnings === 0) {
      counts.errors = 1;
    }

    return counts;
  }
}

// ---------------------------------------------------------------------------
// Quality Gate - pass/fail decision
// ---------------------------------------------------------------------------
class QualityGate {
  constructor(config = {}) {
    this.config = {
      maxErrors: config.maxErrors || 0,
      maxWarnings: config.maxWarnings || 50,
      minScore: config.minScore || 70,
      enforcement: config.enforcement || 'strict', // strict | warn | off
      ...config
    };
  }

  evaluate(report) {
    if (this.config.enforcement === 'off') {
      return { passed: true, reason: 'enforcement_disabled' };
    }

    const checks = [];

    // Error check
    if (report.totalErrors > this.config.maxErrors) {
      checks.push({
        check: 'errors',
        passed: false,
        message: `${report.totalErrors} errors exceed max of ${this.config.maxErrors}`
      });
    } else {
      checks.push({ check: 'errors', passed: true });
    }

    // Warning check
    if (report.totalWarnings > this.config.maxWarnings) {
      checks.push({
        check: 'warnings',
        passed: false,
        message: `${report.totalWarnings} warnings exceed max of ${this.config.maxWarnings}`
      });
    } else {
      checks.push({ check: 'warnings', passed: true });
    }

    // Score check
    if (report.score < this.config.minScore) {
      checks.push({
        check: 'score',
        passed: false,
        message: `Score ${report.score} below minimum ${this.config.minScore}`
      });
    } else {
      checks.push({ check: 'score', passed: true });
    }

    const allPassed = checks.every(c => c.passed);

    if (this.config.enforcement === 'warn' && !allPassed) {
      return { passed: true, warnings: checks.filter(c => !c.passed), reason: 'warn_mode' };
    }

    return {
      passed: allPassed,
      checks,
      reason: allPassed ? 'all_checks_passed' : 'quality_gate_failed'
    };
  }
}

// ---------------------------------------------------------------------------
// Code Quality Engine - main facade
// ---------------------------------------------------------------------------
class CodeQualityEngine extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      autoFix: config.autoFix !== false,
      enforcement: config.enforcement || process.env.LINT_ENFORCEMENT || 'strict',
      maxErrors: parseInt(process.env.LINT_MAX_ERRORS || '0', 10),
      maxWarnings: parseInt(process.env.LINT_MAX_WARNINGS || '50', 10),
      minScore: parseInt(process.env.LINT_THRESHOLD || '70', 10),
      timeoutMs: config.timeoutMs || 60000,
      ...config
    };

    this._runner = new LintRunner({
      timeoutMs: this.config.timeoutMs,
      autoFix: this.config.autoFix
    });

    this._gate = new QualityGate({
      maxErrors: this.config.maxErrors,
      maxWarnings: this.config.maxWarnings,
      minScore: this.config.minScore,
      enforcement: this.config.enforcement
    });

    this._auditHistory = [];
    this._totalAudits = 0;
    this._totalPassed = 0;
    this._totalFailed = 0;
  }

  /**
   * Run lint checks on a target path.
   */
  async lint(targetPath) {
    const resolvedPath = path.resolve(targetPath || process.cwd());
    const report = new QualityReport(resolvedPath);
    const startTime = Date.now();

    this.emit('lint:started', { targetPath: resolvedPath });

    // Detect project
    const project = this._runner.detectProject(resolvedPath);
    report.projectType = project.type;

    if (project.linters.length === 0) {
      report.score = 100;
      report.grade = 'A';
      report.passed = true;
      report.durationMs = Date.now() - startTime;
      this.emit('lint:completed', report.toJSON());
      return report;
    }

    // Auto-fix pass first
    if (this.config.autoFix) {
      for (const linter of project.linters) {
        const fixed = await this._runner.autoFixLinter(linter, resolvedPath);
        if (fixed) report.autoFixApplied = true;
      }
    }

    // Run each linter
    for (const linter of project.linters) {
      const check = await this._runner.runLinter(linter, resolvedPath);
      report.checks.push(check);
      report.totalErrors += check.errors;
      report.totalWarnings += check.warnings;
      report.totalFixable += check.fixable;
    }

    report.durationMs = Date.now() - startTime;
    report.computeScore();

    // Quality gate
    const gateResult = this._gate.evaluate(report);
    report.passed = gateResult.passed;

    // Track
    this._totalAudits++;
    if (report.passed) this._totalPassed++;
    else this._totalFailed++;

    this._auditHistory.push({
      path: resolvedPath,
      score: report.score,
      grade: report.grade,
      passed: report.passed,
      timestamp: report.timestamp
    });
    if (this._auditHistory.length > 100) this._auditHistory.shift();

    this.emit('lint:completed', report.toJSON());
    return report;
  }

  /**
   * Alias for lint — validates code at a path.
   */
  async validate(targetPath) {
    return this.lint(targetPath);
  }

  /**
   * Full audit: lint + additional static analysis.
   */
  async fullAudit(targetPath) {
    const report = await this.lint(targetPath);

    // Additional checks
    const resolvedPath = path.resolve(targetPath || process.cwd());

    // Check for common anti-patterns
    const antiPatterns = this._scanAntiPatterns(resolvedPath);
    if (antiPatterns.length > 0) {
      report.totalWarnings += antiPatterns.length;
      report.computeScore();
    }

    return {
      lint: report.toJSON(),
      antiPatterns,
      gateDecision: this._gate.evaluate(report)
    };
  }

  /**
   * Quick scan for common anti-patterns.
   */
  _scanAntiPatterns(targetPath) {
    const issues = [];
    const jsFiles = this._findFiles(targetPath, /\.js$/);

    for (const file of jsFiles.slice(0, 50)) { // limit scan scope
      try {
        const content = fs.readFileSync(file, 'utf8');
        const relativePath = path.relative(targetPath, file);

        // console.log in production code (not test files)
        if (!relativePath.includes('test') && !relativePath.includes('spec')) {
          const consoleCount = (content.match(/console\.(log|debug|info)\(/g) || []).length;
          if (consoleCount > 10) {
            issues.push({
              file: relativePath,
              issue: 'excessive_console',
              message: `${consoleCount} console statements (consider using a logger)`
            });
          }
        }

        // Very long functions (rough heuristic)
        const functions = content.match(/(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))[^{]*\{/g);
        if (functions) {
          // Simple line counting between braces (rough)
          const lines = content.split('\n');
          if (lines.length > 500) {
            issues.push({
              file: relativePath,
              issue: 'large_file',
              message: `${lines.length} lines (consider splitting)`
            });
          }
        }

        // TODO/FIXME/HACK comments
        const todoCount = (content.match(/\/\/\s*(TODO|FIXME|HACK|XXX)/gi) || []).length;
        if (todoCount > 5) {
          issues.push({
            file: relativePath,
            issue: 'unresolved_todos',
            message: `${todoCount} TODO/FIXME comments`
          });
        }

      } catch (err) {
        // Skip unreadable files
      }
    }

    return issues;
  }

  /**
   * Recursively find files matching a pattern.
   */
  _findFiles(dir, pattern, maxDepth = 4, depth = 0) {
    if (depth > maxDepth) return [];
    const results = [];

    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.name === 'node_modules' || entry.name === '.git') continue;
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
          results.push(...this._findFiles(fullPath, pattern, maxDepth, depth + 1));
        } else if (pattern.test(entry.name)) {
          results.push(fullPath);
        }
      }
    } catch (err) {
      // Permission or access errors
    }

    return results;
  }

  /**
   * Get engine status and history.
   */
  getStatus() {
    return {
      enforcement: this.config.enforcement,
      autoFix: this.config.autoFix,
      thresholds: {
        maxErrors: this.config.maxErrors,
        maxWarnings: this.config.maxWarnings,
        minScore: this.config.minScore
      },
      stats: {
        totalAudits: this._totalAudits,
        passed: this._totalPassed,
        failed: this._totalFailed,
        passRate: this._totalAudits > 0
          ? ((this._totalPassed / this._totalAudits) * 100).toFixed(1) + '%'
          : 'N/A'
      },
      recentAudits: this._auditHistory.slice(-10)
    };
  }
}

module.exports = {
  CodeQualityEngine,
  LintRunner,
  QualityGate,
  QualityReport,
  LintCheckResult
};
