#!/usr/bin/env node
/**
 * Multi-Agent Autonomous Orchestration System v1.0.0
 * ==================================================
 * Transitions linear tasks into autonomous multi-agent workflows
 * with specialized roles: Critic, Optimizer, Executor.
 *
 * Architecture:
 *   - AgentRole: defines behavioral contract for each role
 *   - AgentSwarm: manages a pool of role-assigned agents
 *   - TaskDecomposer: breaks complex tasks into subtasks
 *   - ConsensusEngine: aggregates results from parallel agents
 *   - SkillAcquisitionManager: dynamic module integration
 */

'use strict';

const { EventEmitter } = require('events');
const crypto = require('crypto');

// ---------------------------------------------------------------------------
// Agent Roles
// ---------------------------------------------------------------------------
const AGENT_ROLES = {
  EXECUTOR: {
    name: 'Executor',
    description: 'Performs the primary task execution',
    permissions: ['workflow:execute', 'skill:execute', 'data:read', 'data:write'],
    priority: 80
  },
  CRITIC: {
    name: 'Critic',
    description: 'Reviews and validates executor output for quality and correctness',
    permissions: ['data:read', 'audit:read'],
    priority: 90
  },
  OPTIMIZER: {
    name: 'Optimizer',
    description: 'Analyzes output for performance and suggests improvements',
    permissions: ['data:read', 'data:write', 'system:monitor'],
    priority: 85
  },
  PLANNER: {
    name: 'Planner',
    description: 'Decomposes complex tasks into executable subtasks',
    permissions: ['workflow:create', 'data:read'],
    priority: 95
  },
  SENTINEL: {
    name: 'Sentinel',
    description: 'Monitors execution for security violations and anomalies',
    permissions: ['audit:read', 'system:monitor', 'data:read'],
    priority: 100
  }
};

// ---------------------------------------------------------------------------
// Task Decomposer
// ---------------------------------------------------------------------------
class TaskDecomposer {
  /**
   * Break a complex task into subtasks with dependency graph.
   */
  decompose(task) {
    const subtasks = [];
    const complexity = this._assessComplexity(task);

    if (complexity === 'simple') {
      subtasks.push({
        id: this._generateId(),
        type: 'execute',
        description: task.description || task,
        dependencies: [],
        assignedRole: 'EXECUTOR',
        priority: task.priority || 50,
        status: 'pending'
      });
    } else if (complexity === 'moderate') {
      const planId = this._generateId();
      const execId = this._generateId();
      const reviewId = this._generateId();

      subtasks.push(
        { id: planId, type: 'plan', description: `Plan: ${task.description}`, dependencies: [], assignedRole: 'PLANNER', priority: 90, status: 'pending' },
        { id: execId, type: 'execute', description: `Execute: ${task.description}`, dependencies: [planId], assignedRole: 'EXECUTOR', priority: 80, status: 'pending' },
        { id: reviewId, type: 'review', description: `Review: ${task.description}`, dependencies: [execId], assignedRole: 'CRITIC', priority: 85, status: 'pending' }
      );
    } else {
      // Complex: full pipeline
      const planId = this._generateId();
      const execId = this._generateId();
      const criticId = this._generateId();
      const optimizeId = this._generateId();
      const sentinelId = this._generateId();

      subtasks.push(
        { id: planId, type: 'plan', description: `Plan: ${task.description}`, dependencies: [], assignedRole: 'PLANNER', priority: 95, status: 'pending' },
        { id: execId, type: 'execute', description: `Execute: ${task.description}`, dependencies: [planId], assignedRole: 'EXECUTOR', priority: 80, status: 'pending' },
        { id: criticId, type: 'review', description: `Critique: ${task.description}`, dependencies: [execId], assignedRole: 'CRITIC', priority: 90, status: 'pending' },
        { id: optimizeId, type: 'optimize', description: `Optimize: ${task.description}`, dependencies: [execId], assignedRole: 'OPTIMIZER', priority: 85, status: 'pending' },
        { id: sentinelId, type: 'security_scan', description: `Security: ${task.description}`, dependencies: [execId], assignedRole: 'SENTINEL', priority: 100, status: 'pending' }
      );
    }

    return {
      originalTask: task,
      complexity,
      subtasks,
      graph: this._buildDependencyGraph(subtasks)
    };
  }

  _assessComplexity(task) {
    const desc = typeof task === 'string' ? task : (task.description || '');
    const wordCount = desc.split(/\s+/).length;
    const hasMultipleGoals = /\b(and|then|also|additionally|plus)\b/i.test(desc);
    const isSecuritySensitive = /\b(security|encrypt|auth|credential|secret)\b/i.test(desc);
    const isArchitectural = /\b(architect|design|migrate|refactor|scale)\b/i.test(desc);

    if (isSecuritySensitive || isArchitectural || (hasMultipleGoals && wordCount > 20)) {
      return 'complex';
    }
    if (hasMultipleGoals || wordCount > 15) {
      return 'moderate';
    }
    return 'simple';
  }

  _buildDependencyGraph(subtasks) {
    const graph = {};
    for (const st of subtasks) {
      graph[st.id] = {
        role: st.assignedRole,
        type: st.type,
        dependsOn: st.dependencies,
        enabledBy: []
      };
    }
    // Compute reverse edges
    for (const st of subtasks) {
      for (const dep of st.dependencies) {
        if (graph[dep]) {
          graph[dep].enabledBy.push(st.id);
        }
      }
    }
    return graph;
  }

  _generateId() {
    return 'st_' + crypto.randomBytes(4).toString('hex');
  }
}

// ---------------------------------------------------------------------------
// Consensus Engine
// ---------------------------------------------------------------------------
class ConsensusEngine {
  /**
   * Aggregate results from multiple agents into a single outcome.
   */
  aggregate(results) {
    if (results.length === 0) {
      return { consensus: false, reason: 'no_results' };
    }

    if (results.length === 1) {
      return { consensus: true, result: results[0], method: 'single_agent' };
    }

    // Majority vote on success/failure
    const successes = results.filter(r => r.success);
    const failures = results.filter(r => !r.success);

    if (successes.length > failures.length) {
      // Merge successful results
      const merged = this._mergeResults(successes);
      return {
        consensus: true,
        result: merged,
        method: 'majority_vote',
        votes: { success: successes.length, failure: failures.length }
      };
    }

    return {
      consensus: false,
      reason: 'majority_failed',
      votes: { success: successes.length, failure: failures.length },
      errors: failures.map(f => f.error)
    };
  }

  _mergeResults(results) {
    // Take the result with highest confidence or most data
    let best = results[0];
    for (const r of results) {
      if ((r.confidence || 0) > (best.confidence || 0)) {
        best = r;
      }
    }
    return best;
  }
}

// ---------------------------------------------------------------------------
// Skill Acquisition Manager
// ---------------------------------------------------------------------------
class SkillAcquisitionManager {
  constructor() {
    this._registry = new Map();     // skillName -> module info
    this._loadHistory = [];
    this._maxModules = 500;
  }

  /**
   * Register a new skill module dynamically.
   */
  register(name, module) {
    if (this._registry.size >= this._maxModules) {
      // Evict least-used
      this._evictLeastUsed();
    }

    this._registry.set(name, {
      module,
      registeredAt: Date.now(),
      invocations: 0,
      lastUsed: null
    });

    this._loadHistory.push({
      event: 'registered',
      skill: name,
      timestamp: Date.now()
    });

    return true;
  }

  /**
   * Execute a skill by name.
   */
  async execute(name, params = {}) {
    const entry = this._registry.get(name);
    if (!entry) {
      throw new Error(`Skill "${name}" not found in acquisition registry`);
    }

    entry.invocations++;
    entry.lastUsed = Date.now();

    if (typeof entry.module === 'function') {
      return await entry.module(params);
    }
    if (typeof entry.module.execute === 'function') {
      return await entry.module.execute(params);
    }

    throw new Error(`Skill "${name}" does not expose an executable interface`);
  }

  /**
   * Get recommended skills for a task description.
   */
  recommend(taskDescription) {
    const desc = taskDescription.toLowerCase();
    const matches = [];

    for (const [name, entry] of this._registry) {
      if (desc.includes(name.toLowerCase().replace(/-/g, ' '))) {
        matches.push({ name, invocations: entry.invocations });
      }
    }

    return matches.sort((a, b) => b.invocations - a.invocations);
  }

  _evictLeastUsed() {
    let leastKey = null;
    let leastUsed = Infinity;

    for (const [name, entry] of this._registry) {
      if (entry.invocations < leastUsed) {
        leastUsed = entry.invocations;
        leastKey = name;
      }
    }

    if (leastKey) {
      this._registry.delete(leastKey);
      this._loadHistory.push({
        event: 'evicted',
        skill: leastKey,
        timestamp: Date.now()
      });
    }
  }

  getStats() {
    return {
      registered: this._registry.size,
      maxModules: this._maxModules,
      totalInvocations: [...this._registry.values()].reduce((s, e) => s + e.invocations, 0),
      recentHistory: this._loadHistory.slice(-20)
    };
  }
}

// ---------------------------------------------------------------------------
// Agent Swarm
// ---------------------------------------------------------------------------
class AgentSwarm extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      maxConcurrentAgents: config.maxConcurrentAgents || 10,
      taskTimeoutMs: config.taskTimeoutMs || 120000,
      enableConsensus: config.enableConsensus !== false,
      ...config
    };

    this._decomposer = new TaskDecomposer();
    this._consensus = new ConsensusEngine();
    this._skillManager = new SkillAcquisitionManager();

    this._activeAgents = new Map();
    this._completedTasks = [];
    this._totalDispatched = 0;
  }

  get decomposer() { return this._decomposer; }
  get consensus() { return this._consensus; }
  get skillManager() { return this._skillManager; }

  /**
   * Submit a high-level task for autonomous multi-agent execution.
   */
  async dispatch(task) {
    const decomposition = this._decomposer.decompose(task);
    this._totalDispatched++;

    this.emit('task:decomposed', {
      complexity: decomposition.complexity,
      subtaskCount: decomposition.subtasks.length
    });

    // Execute subtask graph respecting dependencies
    const results = await this._executeGraph(decomposition);

    // Aggregate via consensus
    if (this.config.enableConsensus && results.length > 1) {
      return this._consensus.aggregate(results);
    }

    return {
      consensus: true,
      results,
      complexity: decomposition.complexity,
      subtaskCount: decomposition.subtasks.length
    };
  }

  async _executeGraph(decomposition) {
    const { subtasks, graph } = decomposition;
    const completed = new Map(); // subtaskId -> result
    const results = [];

    // Topological execution
    const remaining = [...subtasks];

    while (remaining.length > 0) {
      // Find subtasks whose dependencies are all met
      const ready = remaining.filter(st =>
        st.dependencies.every(dep => completed.has(dep))
      );

      if (ready.length === 0 && remaining.length > 0) {
        // Deadlock detection
        throw new Error('Dependency deadlock detected in subtask graph');
      }

      // Execute ready subtasks in parallel (respecting concurrency limit)
      const batch = ready.slice(0, this.config.maxConcurrentAgents);
      const batchResults = await Promise.allSettled(
        batch.map(st => this._executeSubtask(st, completed))
      );

      for (let i = 0; i < batch.length; i++) {
        const st = batch[i];
        const outcome = batchResults[i];
        const result = outcome.status === 'fulfilled'
          ? outcome.value
          : { success: false, error: outcome.reason?.message || 'Unknown error' };

        completed.set(st.id, result);
        results.push(result);

        // Remove from remaining
        const idx = remaining.indexOf(st);
        if (idx !== -1) remaining.splice(idx, 1);
      }
    }

    return results;
  }

  async _executeSubtask(subtask, priorResults) {
    const role = AGENT_ROLES[subtask.assignedRole] || AGENT_ROLES.EXECUTOR;

    this.emit('subtask:started', {
      id: subtask.id,
      type: subtask.type,
      role: role.name
    });

    // Simulate role-based execution
    const context = {
      subtask,
      role,
      priorResults: Object.fromEntries(priorResults),
      startedAt: Date.now()
    };

    const result = await this._roleDispatch(subtask, role, context);

    this.emit('subtask:completed', {
      id: subtask.id,
      type: subtask.type,
      role: role.name,
      success: result.success
    });

    this._completedTasks.push({
      subtaskId: subtask.id,
      role: role.name,
      result,
      completedAt: Date.now()
    });

    return result;
  }

  async _roleDispatch(subtask, role, context) {
    switch (subtask.type) {
      case 'plan':
        return {
          success: true,
          type: 'plan',
          plan: { steps: [`Planned: ${subtask.description}`] },
          role: role.name
        };

      case 'execute':
        return {
          success: true,
          type: 'execution',
          output: `Executed: ${subtask.description}`,
          role: role.name
        };

      case 'review':
        return {
          success: true,
          type: 'review',
          feedback: `Reviewed: ${subtask.description}`,
          issues: [],
          role: role.name
        };

      case 'optimize':
        return {
          success: true,
          type: 'optimization',
          suggestions: [`Optimized: ${subtask.description}`],
          role: role.name
        };

      case 'security_scan':
        return {
          success: true,
          type: 'security',
          vulnerabilities: [],
          passed: true,
          role: role.name
        };

      default:
        return {
          success: true,
          type: subtask.type,
          output: `Processed: ${subtask.description}`,
          role: role.name
        };
    }
  }

  getStats() {
    return {
      totalDispatched: this._totalDispatched,
      completedTasks: this._completedTasks.length,
      activeAgents: this._activeAgents.size,
      skillModules: this._skillManager.getStats(),
      roles: Object.keys(AGENT_ROLES)
    };
  }
}

module.exports = {
  AgentSwarm,
  TaskDecomposer,
  ConsensusEngine,
  SkillAcquisitionManager,
  AGENT_ROLES
};
