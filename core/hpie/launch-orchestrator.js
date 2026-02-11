#!/usr/bin/env node
/**
 * Intelligent Launch Orchestrator v1.0.0
 * ==================================================
 * Advanced automation framework for system initialization and deployment.
 *
 * Capabilities:
 *   - Phased startup with dependency resolution
 *   - Self-correcting health checks
 *   - Zero-touch environment configuration
 *   - Graceful degradation on subsystem failure
 *   - Rollback-safe deployments
 */

'use strict';

const { EventEmitter } = require('events');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Health Check System
// ---------------------------------------------------------------------------
class HealthChecker {
  constructor() {
    this._checks = new Map();
    this._results = new Map();
    this._history = [];
  }

  register(name, checkFn, opts = {}) {
    this._checks.set(name, {
      fn: checkFn,
      critical: opts.critical !== false,
      timeoutMs: opts.timeoutMs || 5000,
      retries: opts.retries || 2,
      intervalMs: opts.intervalMs || 30000
    });
  }

  async runAll() {
    const results = {};
    const promises = [];

    for (const [name, check] of this._checks) {
      promises.push(this._runCheck(name, check).then(result => {
        results[name] = result;
      }));
    }

    await Promise.allSettled(promises);

    const snapshot = {
      timestamp: Date.now(),
      results,
      healthy: Object.values(results).every(r => r.status === 'healthy'),
      criticalFailures: Object.entries(results)
        .filter(([name, r]) => r.status !== 'healthy' && this._checks.get(name)?.critical)
        .map(([name]) => name)
    };

    this._history.push(snapshot);
    if (this._history.length > 100) this._history.shift();

    return snapshot;
  }

  async _runCheck(name, check) {
    let lastError = null;

    for (let attempt = 0; attempt <= check.retries; attempt++) {
      try {
        const result = await Promise.race([
          check.fn(),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Health check timeout')), check.timeoutMs)
          )
        ]);

        const status = {
          status: 'healthy',
          latencyMs: 0,
          attempt: attempt + 1,
          details: result
        };

        this._results.set(name, status);
        return status;

      } catch (err) {
        lastError = err;
        if (attempt < check.retries) {
          await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
        }
      }
    }

    const status = {
      status: 'unhealthy',
      error: lastError?.message || 'Unknown error',
      critical: check.critical,
      attempt: check.retries + 1
    };

    this._results.set(name, status);
    return status;
  }

  getStatus() {
    return Object.fromEntries(this._results);
  }
}

// ---------------------------------------------------------------------------
// Environment Configurator
// ---------------------------------------------------------------------------
class EnvironmentConfigurator {
  constructor(basePath) {
    this._basePath = basePath;
    this._resolved = {};
    this._requiredDirs = [];
  }

  /**
   * Auto-detect and configure the execution environment.
   */
  async configure() {
    const env = this._detectEnvironment();

    // Ensure required directories exist
    this._requiredDirs = [
      path.join(this._basePath, '.verma'),
      path.join(this._basePath, '.verma', 'cache'),
      path.join(this._basePath, '.verma', 'logs'),
      path.join(this._basePath, '.verma', 'sandbox'),
      path.join(this._basePath, '.verma', 'checkpoints')
    ];

    for (const dir of this._requiredDirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }

    // Merge environment variables with defaults
    this._resolved = {
      platform: env.platform,
      nodeVersion: process.version,
      pid: process.pid,
      basePath: this._basePath,
      logLevel: process.env.LOG_LEVEL || 'info',
      maxConcurrentAgents: parseInt(process.env.AGENTS_MAX_CONCURRENT || '10', 10),
      agentTimeout: parseInt(process.env.AGENT_TIMEOUT || '300', 10),
      parallelExecution: process.env.WORKFLOWS_PARALLEL_EXECUTION !== 'false',
      memoryOptimization: process.env.MEMORY_OPTIMIZATION !== 'false',
      securityAudit: process.env.SECURITY_AUDIT_ENABLED !== 'false',
      ports: {
        dashboard: parseInt(process.env.PORT_DASHBOARD || '8551', 10),
        assistant: parseInt(process.env.PORT_ASSISTANT || '8550', 10),
        api: parseInt(process.env.PORT_API || '8552', 10)
      },
      ...env
    };

    return this._resolved;
  }

  _detectEnvironment() {
    const checks = {
      opencode: !!process.env.OPENCODE_ENV || fs.existsSync(path.join(this._basePath, '.opencode')),
      traeai: !!process.env.TRAE_AI_ENV || fs.existsSync(path.join(this._basePath, '.trae')),
      docker: !!process.env.DOCKER_ENV || fs.existsSync(path.join(this._basePath, 'docker-compose.yml')),
      antigravity: !!process.env.GOOGLE_ANTIGRAVITY_ENV
    };

    let platform = 'local';
    if (checks.opencode) platform = 'opencode';
    else if (checks.traeai) platform = 'traeai';
    else if (checks.antigravity) platform = 'antigravity';
    else if (checks.docker) platform = 'docker';

    return { platform, checks };
  }

  getResolved() {
    return { ...this._resolved };
  }
}

// ---------------------------------------------------------------------------
// Launch Phase
// ---------------------------------------------------------------------------
class LaunchPhase {
  constructor(name, executeFn, opts = {}) {
    this.name = name;
    this.executeFn = executeFn;
    this.critical = opts.critical !== false;
    this.dependencies = opts.dependencies || [];
    this.timeoutMs = opts.timeoutMs || 30000;
    this.retryable = opts.retryable || false;
    this.maxRetries = opts.maxRetries || 2;
    this.rollbackFn = opts.rollbackFn || null;

    this.status = 'pending';
    this.result = null;
    this.error = null;
    this.startedAt = null;
    this.completedAt = null;
    this.durationMs = 0;
  }
}

// ---------------------------------------------------------------------------
// Intelligent Launch Orchestrator
// ---------------------------------------------------------------------------
class IntelligentLaunchOrchestrator extends EventEmitter {
  constructor(basePath) {
    super();
    this._basePath = basePath || process.cwd();
    this._phases = new Map();
    this._phaseOrder = [];
    this._healthChecker = new HealthChecker();
    this._envConfigurator = new EnvironmentConfigurator(this._basePath);
    this._state = 'idle'; // idle | launching | running | degraded | failed
    this._startTime = null;
    this._launchReport = null;
  }

  get state() { return this._state; }
  get healthChecker() { return this._healthChecker; }

  /**
   * Register a launch phase.
   */
  registerPhase(name, executeFn, opts = {}) {
    const phase = new LaunchPhase(name, executeFn, opts);
    this._phases.set(name, phase);
    this._phaseOrder.push(name);
    return this;
  }

  /**
   * Execute the full launch sequence.
   */
  async launch() {
    this._state = 'launching';
    this._startTime = Date.now();
    const report = {
      phases: [],
      environment: null,
      health: null,
      totalDurationMs: 0,
      status: 'pending'
    };

    this.emit('launch:started');

    try {
      // Phase 0: Environment configuration
      report.environment = await this._envConfigurator.configure();
      this.emit('launch:phase', { name: 'environment', status: 'completed' });

      // Execute registered phases in order, respecting dependencies
      const completed = new Set();

      for (const phaseName of this._phaseOrder) {
        const phase = this._phases.get(phaseName);

        // Check dependencies
        for (const dep of phase.dependencies) {
          if (!completed.has(dep)) {
            throw new Error(`Phase "${phaseName}" depends on "${dep}" which has not completed`);
          }
        }

        await this._executePhase(phase, report);

        if (phase.status === 'completed') {
          completed.add(phaseName);
        } else if (phase.critical) {
          report.status = 'failed';
          this._state = 'failed';
          this.emit('launch:failed', { phase: phaseName, error: phase.error });
          break;
        } else {
          // Non-critical failure: degrade gracefully
          this._state = 'degraded';
          this.emit('launch:degraded', { phase: phaseName });
        }
      }

      // Post-launch health check
      report.health = await this._healthChecker.runAll();

      if (report.status !== 'failed') {
        report.status = this._state === 'degraded' ? 'degraded' : 'success';
        if (this._state !== 'degraded') this._state = 'running';
      }

    } catch (err) {
      report.status = 'failed';
      report.error = err.message;
      this._state = 'failed';
      this.emit('launch:failed', { error: err.message });
    }

    report.totalDurationMs = Date.now() - this._startTime;
    this._launchReport = report;

    this.emit('launch:completed', report);
    return report;
  }

  async _executePhase(phase, report) {
    phase.status = 'running';
    phase.startedAt = Date.now();

    this.emit('launch:phase', { name: phase.name, status: 'started' });

    let attempts = 0;
    const maxAttempts = phase.retryable ? phase.maxRetries + 1 : 1;

    while (attempts < maxAttempts) {
      attempts++;
      try {
        phase.result = await Promise.race([
          phase.executeFn(),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error(`Phase "${phase.name}" timed out`)), phase.timeoutMs)
          )
        ]);

        phase.status = 'completed';
        phase.completedAt = Date.now();
        phase.durationMs = phase.completedAt - phase.startedAt;

        this.emit('launch:phase', {
          name: phase.name,
          status: 'completed',
          durationMs: phase.durationMs
        });

        break;

      } catch (err) {
        phase.error = err.message;

        if (attempts < maxAttempts) {
          this.emit('launch:phase', {
            name: phase.name,
            status: 'retrying',
            attempt: attempts,
            error: err.message
          });
          await new Promise(r => setTimeout(r, 1000 * attempts));
        } else {
          phase.status = 'failed';
          phase.completedAt = Date.now();
          phase.durationMs = phase.completedAt - phase.startedAt;

          this.emit('launch:phase', {
            name: phase.name,
            status: 'failed',
            error: err.message
          });

          // Attempt rollback
          if (phase.rollbackFn) {
            try {
              await phase.rollbackFn();
              this.emit('launch:rollback', { phase: phase.name, status: 'success' });
            } catch (rbErr) {
              this.emit('launch:rollback', { phase: phase.name, status: 'failed', error: rbErr.message });
            }
          }
        }
      }
    }

    report.phases.push({
      name: phase.name,
      status: phase.status,
      durationMs: phase.durationMs,
      critical: phase.critical,
      error: phase.error
    });
  }

  /**
   * Graceful shutdown.
   */
  async shutdown() {
    this.emit('shutdown:started');
    this._state = 'idle';

    // Run phase rollbacks in reverse order
    for (const phaseName of [...this._phaseOrder].reverse()) {
      const phase = this._phases.get(phaseName);
      if (phase.rollbackFn && phase.status === 'completed') {
        try {
          await phase.rollbackFn();
        } catch (err) {
          // Log but continue shutdown
        }
      }
    }

    this.emit('shutdown:completed');
  }

  getLaunchReport() {
    return this._launchReport;
  }

  getStatus() {
    return {
      state: this._state,
      uptime: this._startTime ? ((Date.now() - this._startTime) / 1000).toFixed(1) + 's' : null,
      phases: [...this._phases.values()].map(p => ({
        name: p.name,
        status: p.status,
        durationMs: p.durationMs,
        critical: p.critical
      })),
      environment: this._envConfigurator.getResolved(),
      health: this._healthChecker.getStatus()
    };
  }
}

module.exports = {
  IntelligentLaunchOrchestrator,
  HealthChecker,
  EnvironmentConfigurator,
  LaunchPhase
};
