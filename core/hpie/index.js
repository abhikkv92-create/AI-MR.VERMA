#!/usr/bin/env node
/**
 * HPIE - High-Performance Intelligence Engine
 * Barrel export for all HPIE subsystems.
 */

'use strict';

const { HighPerformanceIntelligenceEngine, ObjectPool, CircuitBreaker, LRUCache, ResourceMonitor } = require('./intelligence-engine');
const { ZeroHallucinationFramework, ChainOfThoughtDecomposer, ConsistencyGate, ConfidenceScorer, HallucinationDetector } = require('./zero-hallucination');
const { SecurityHardeningModule, AgentIAM, EncryptionEngine, InputSanitizer, RateLimiter, SecretsVault } = require('./security-hardening');
const { AgentSwarm, TaskDecomposer, ConsensusEngine, SkillAcquisitionManager, AGENT_ROLES } = require('./multi-agent-orchestrator');
const { IntelligentLaunchOrchestrator, HealthChecker, EnvironmentConfigurator } = require('./launch-orchestrator');
const { PlatformBridge, PLATFORM_CAPS } = require('./platform-bridge');
const { AntiBloatProtocol, DependencyAnalyzer, ModuleUsageTracker, MemoryFootprintProfiler } = require('./anti-bloat');
const { CodeQualityEngine, LintRunner, QualityGate, QualityReport, LintCheckResult } = require('./code-quality-engine');

module.exports = {
  // Core Engine
  HighPerformanceIntelligenceEngine,
  ObjectPool,
  CircuitBreaker,
  LRUCache,
  ResourceMonitor,

  // Zero-Hallucination
  ZeroHallucinationFramework,
  ChainOfThoughtDecomposer,
  ConsistencyGate,
  ConfidenceScorer,
  HallucinationDetector,

  // Security
  SecurityHardeningModule,
  AgentIAM,
  EncryptionEngine,
  InputSanitizer,
  RateLimiter,
  SecretsVault,

  // Multi-Agent
  AgentSwarm,
  TaskDecomposer,
  ConsensusEngine,
  SkillAcquisitionManager,
  AGENT_ROLES,

  // Launch
  IntelligentLaunchOrchestrator,
  HealthChecker,
  EnvironmentConfigurator,

  // Platform
  PlatformBridge,
  PLATFORM_CAPS,

  // Anti-Bloat
  AntiBloatProtocol,
  DependencyAnalyzer,
  ModuleUsageTracker,
  MemoryFootprintProfiler,

  // Code Quality
  CodeQualityEngine,
  LintRunner,
  QualityGate,
  QualityReport,
  LintCheckResult
};
