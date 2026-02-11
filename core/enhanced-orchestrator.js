#!/usr/bin/env node
/**
 * MR.VERMA Enhanced Orchestrator v2.0
 * Full-stack development with chat, vibecoding, and local LLM integration
 */

const fs = require('fs');
const path = require('path');

// Import core components
const AgentRegistry = require('./agent-registry');
const WorkflowEngine = require('./workflow-engine');
const SkillsLoader = require('./skills-loader');
const VermaChatInterface = require('./chat-interface');
const LocalLLMManager = require('./local-llm');
const VibecodingAgent = require('./vibecoding-agent');
const ApplicationBuilder = require('./application-builder');
const CodeExecutionSandbox = require('./sandbox');

// HPIE - High-Performance Intelligence Engine
const {
  HighPerformanceIntelligenceEngine,
  ZeroHallucinationFramework,
  SecurityHardeningModule,
  AgentSwarm,
  PlatformBridge,
  AntiBloatProtocol,
  CodeQualityEngine
} = require('./hpie');

class EnhancedVermaOrchestrator {
  constructor() {
    this.config = null;
    this.agents = new Map();
    this.skills = new Map();
    this.workflows = new Map();
    this.platform = null;
    this.status = 'initializing';
    
    // New components
    this.chat = null;
    this.llm = null;
    this.vibecoder = null;
    this.builder = null;
    this.sandbox = null;

    // HPIE subsystems
    this.hpie = null;
  }

  async initialize() {
    console.log('🕸️  Initializing MR.VERMA Enhanced Orchestrator v2.0...');
    console.log('   🤖 12 Specialized Agents');
    console.log('   💬 Conversational Interface');
    console.log('   🎨 Vibecoding Agent');
    console.log('   🏗️  Application Builder');
    console.log('   🧠 Local LLM Integration');
    console.log('   🔒 Code Sandbox');
    console.log();
    
    // Detect platform
    this.platform = this.detectPlatform();
    console.log(`✓ Platform: ${this.platform}`);
    
    // Initialize core systems
    await this.initializeCore();
    
    // Initialize new capabilities
    await this.initializeEnhancedFeatures();
    
    // Load workflows
    await this.loadEnhancedWorkflows();
    
    this.status = 'ready';
    console.log('\n✅ MR.VERMA Enhanced is ready!');
    console.log('   Type \x1b[36m/verma chat\x1b[0m to start chatting');
    console.log('   Type \x1b[36m/verma build [description]\x1b[0m to build an app');
    console.log('   Type \x1b[36m/verma status\x1b[0m for system status');
    
    return this;
  }

  detectPlatform() {
    if (process.env.OPENCODE_ENV) return 'opencode';
    if (process.env.TRAE_AI_ENV) return 'traeai';
    if (process.env.VERCEL_ENV) return 'vercel';
    if (fs.existsSync('.opencode')) return 'opencode';
    if (fs.existsSync('.trae')) return 'traeai';
    if (fs.existsSync('docker-compose.yml')) return 'docker';
    return 'local';
  }

  async initializeCore() {
    // Agent Registry
    this.registry = new AgentRegistry();
    this.agents = this.registry.agents;
    console.log(`✓ ${this.agents.size} agents ready`);
    
    // Skills Loader
    this.skillsLoader = new SkillsLoader();
    await this.skillsLoader.loadAllSkills();
    this.skills = this.skillsLoader.skills;
    
    // Workflow Engine
    this.workflowEngine = new WorkflowEngine(this);
    this.workflows = this.workflowEngine.workflows;
    
    // Activate auto-start agents
    for (const agent of this.registry.getAutoStartAgents()) {
      this.registry.activateAgent(agent.id);
    }
  }

  async initializeEnhancedFeatures() {
    // Chat Interface
    console.log('\n💬 Initializing Chat Interface...');
    this.chat = new VermaChatInterface(this);
    await this.chat.initialize();
    
    // Local LLM Manager
    console.log('\n🧠 Initializing Local LLM...');
    this.llm = new LocalLLMManager({
      provider: 'ollama',
      model: 'codellama:7b-code',
      temperature: 0.7
    });
    await this.llm.initialize();
    
    // Vibecoding Agent
    console.log('\n🎨 Initializing Vibecoding Agent...');
    this.vibecoder = new VibecodingAgent(this);
    await this.vibecoder.initialize();
    
    // Application Builder
    console.log('\n🏗️  Initializing Application Builder...');
    this.builder = new ApplicationBuilder(this);
    await this.builder.initialize();
    
    // Code Sandbox
    console.log('\n🔒 Initializing Code Sandbox...');
    this.sandbox = new CodeExecutionSandbox();
    
    // HPIE - High-Performance Intelligence Engine
    console.log('\n⚡ Initializing HPIE Intelligence Engine...');
    await this.initializeHPIE();

    console.log('\n✅ All enhanced features loaded');
  }

  async loadEnhancedWorkflows() {
    // Add vibecoding workflow (with lint enforcement)
    this.workflowEngine.registerWorkflow('vibecoding', {
      name: 'Vibecoding Workflow',
      description: 'Natural language to application development with lint enforcement',
      steps: [
        { id: 'analyze', type: 'action', action: 'analyze_requirements' },
        { id: 'design', type: 'action', action: 'design_architecture' },
        { id: 'generate', type: 'action', action: 'generate_code' },
        { id: 'assemble', type: 'action', action: 'assemble_project' },
        { id: 'lint_output', type: 'agent_task', agent: 'code_quality_enforcer', action: 'lint_validate' },
        { id: 'validate', type: 'validation', action: 'validate_project' }
      ],
      auto_execute: false,
      parallel: false
    });

    // Add build workflow (with lint enforcement)
    this.workflowEngine.registerWorkflow('build_app', {
      name: 'Application Build',
      description: 'Complete application build process with lint enforcement',
      steps: [
        { id: 'plan', type: 'agent_task', agent: 'architect', action: 'create_plan' },
        { id: 'vibe', type: 'action', action: 'vibecoding' },
        { id: 'code', type: 'agent_task', agent: 'vibecoder', action: 'generate' },
        { id: 'post_gen_lint', type: 'agent_task', agent: 'code_quality_enforcer', action: 'lint_validate' },
        { id: 'review', type: 'agent_task', agent: 'security_auditor', action: 'review' },
        { id: 'test', type: 'agent_task', agent: 'test_engineer', action: 'test' },
        { id: 'final_quality_gate', type: 'agent_task', agent: 'code_quality_enforcer', action: 'enforce_quality_gate' }
      ],
      auto_execute: false,
      parallel: false
    });

    // Add interactive chat workflow
    this.workflowEngine.registerWorkflow('interactive_chat', {
      name: 'Interactive Chat Session',
      description: 'Conversational development session',
      steps: [
        { id: 'chat_init', type: 'action', action: 'initialize_chat' },
        { id: 'process', type: 'action', action: 'process_messages' },
        { id: 'execute', type: 'action', action: 'execute_actions' }
      ],
      auto_execute: false,
      parallel: false
    });
  }

  // Enhanced command handlers
  async handleCommand(command, args = {}) {
    const cmd = command.toLowerCase();
    
    switch (cmd) {
      case 'chat':
        return this.startChat(args);
      case 'build':
      case 'create':
        return this.startBuild(args);
      case 'vibe':
      case 'vibecode':
        return this.startVibecoding(args);
      case 'run':
        return this.runCode(args);
      case 'status':
        return this.getFullStatus();
      case 'agents':
        return this.showAgents();
      case 'skills':
        return this.showSkills();
      case 'workflows':
        return this.showWorkflows();
      case 'sync':
        return this.registry.syncSpiderWeb();
      case 'llm':
        return this.showLLMStatus();
      case 'hpie':
        return this.showHPIEStatus();
      case 'lint':
        return this.runLint(args);
      case 'help':
        return this.showHelp();
      default:
        // Try to process as a vibecoding request
        if (args.text || args.description) {
          return this.startVibecoding({ description: args.text || args.description });
        }
        return { error: `Unknown command: ${command}. Type /verma help for available commands.` };
    }
  }

  async startChat(args = {}) {
    console.log('\n💬 Starting MR.VERMA Chat...');
    console.log('   Describe what you want to build!\n');
    
    const convId = this.chat.createConversation();
    
    // If there's initial text, process it
    if (args.text) {
      const response = await this.chat.processMessage(args.text, convId);
      console.log('\n🤖 Assistant:\n' + response.message);
    }
    
    return {
      conversationId: convId,
      status: 'active',
      message: 'Chat session started'
    };
  }

  async startBuild(args = {}) {
    const description = args.text || args.description;
    
    if (!description) {
      return {
        error: 'Please provide a description: /verma build [description]'
      };
    }
    
    console.log('\n🏗️  Starting Application Build...');
    console.log(`   Description: ${description.substring(0, 100)}...\n`);
    
    try {
      const result = await this.builder.build(description, args);
      
      return {
        success: true,
        project: result.project,
        summary: result.buildContext,
        message: `✅ Application built successfully!\n   Location: ${result.project.path}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async startVibecoding(args = {}) {
    const description = args.text || args.description || args;
    
    if (typeof description !== 'string') {
      return {
        error: 'Please provide a description of what you want to build'
      };
    }
    
    console.log('\n🎨 Entering Vibecoding Mode...');
    console.log('=' .repeat(60));
    
    try {
      const result = await this.vibecoder.processRequest(description, args);
      
      console.log('\n' + '='.repeat(60));
      console.log('✅ Vibecoding Complete!');
      console.log(`   Files created: ${result.summary.filesCreated}`);
      console.log(`   Stack: ${result.summary.stack.join(', ')}`);
      console.log(`   Location: ${result.summary.location}`);
      
      return {
        success: true,
        project: result.project,
        summary: result.summary,
        plan: result.plan
      };
    } catch (error) {
      console.error('\n❌ Vibecoding failed:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async runCode(args = {}) {
    const { type, code, project } = args;
    
    if (project) {
      // Run a project
      console.log(`🚀 Running project: ${project}`);
      return await this.sandbox.runProject(project);
    }
    
    if (type && code) {
      // Run code snippet
      console.log(`🚀 Running ${type} code...`);
      
      if (type === 'node' || type === 'javascript') {
        return await this.sandbox.executeNode(code);
      } else if (type === 'python') {
        return await this.sandbox.executePython(code);
      }
    }
    
    return {
      error: 'Usage: /verma run --project [path] OR /verma run --type [node|python] --code [code]'
    };
  }

  getFullStatus() {
    const status = {
      platform: this.platform,
      status: this.status,
      agents: {
        total: this.agents.size,
        active: this.registry.getActiveAgents().length
      },
      skills: this.skills.size,
      workflows: this.workflows.size,
      uptime: process.uptime(),
      enhanced: {
        chat: this.chat ? 'ready' : 'offline',
        llm: this.llm ? this.llm.getStatus() : 'offline',
        vibecoder: this.vibecoder ? 'ready' : 'offline',
        builder: this.builder ? 'ready' : 'offline',
        sandbox: this.sandbox ? this.sandbox.getStatus() : 'offline',
        hpie: this.hpie ? 'active' : 'offline'
      }
    };
    
    console.log('\n📊 MR.VERMA System Status');
    console.log('='.repeat(50));
    console.log(`Platform: ${status.platform}`);
    console.log(`Status: ${status.status}`);
    console.log(`Agents: ${status.agents.active}/${status.agents.total} active`);
    console.log(`Skills: ${status.skills} loaded`);
    console.log(`Workflows: ${status.workflows} available`);
    console.log(`\nEnhanced Features:`);
    console.log(`  Chat Interface: ${status.enhanced.chat}`);
    console.log(`  Local LLM: ${status.enhanced.llm.status || 'offline'}`);
    console.log(`  Vibecoder: ${status.enhanced.vibecoder}`);
    console.log(`  Builder: ${status.enhanced.builder}`);
    console.log(`  Sandbox: ${status.enhanced.sandbox.activeProcesses || 0} processes`);
    console.log(`  HPIE Engine: ${status.enhanced.hpie}`);

    return status;
  }

  showAgents() {
    console.log('\n👥 Active Agents');
    console.log('='.repeat(50));
    
    for (const agent of this.registry.getActiveAgents()) {
      console.log(`🟢 ${agent.name}`);
      console.log(`   Role: ${agent.role}`);
      console.log(`   Tasks: ${agent.taskCount || 0}`);
    }
  }

  showSkills() {
    console.log(`\n🛠️  Skills Loaded: ${this.skills.size}`);
    
    const categories = new Map();
    for (const [name, skill] of this.skills) {
      const cat = skill.metadata?.category || 'general';
      if (!categories.has(cat)) categories.set(cat, []);
      categories.get(cat).push(name);
    }
    
    for (const [cat, skills] of categories) {
      console.log(`\n${cat}: ${skills.length} skills`);
    }
  }

  showWorkflows() {
    console.log('\n⚡ Workflows');
    console.log('='.repeat(50));
    
    for (const workflow of this.workflowEngine.getAllWorkflows()) {
      const autoStart = workflow.auto_execute ? '🔄' : '⏸️';
      console.log(`${autoStart} ${workflow.name}`);
      console.log(`   Steps: ${workflow.steps.length}`);
    }
  }

  showLLMStatus() {
    if (!this.llm) {
      console.log('\n❌ Local LLM not initialized');
      return;
    }
    
    const status = this.llm.getStatus();
    console.log('\n🧠 Local LLM Status');
    console.log('='.repeat(50));
    console.log(`Status: ${status.status}`);
    console.log(`Provider: ${status.provider || 'None'}`);
    console.log(`Model: ${status.model}`);
    console.log(`Available Models: ${status.availableModels?.length || 0}`);
    
    if (status.availableModels?.length > 0) {
      console.log('\nAvailable Models:');
      status.availableModels.forEach(m => console.log(`  • ${m}`));
    }
  }

  showHelp() {
    console.log(`
🕸️  MR.VERMA Enhanced - Available Commands
${'='.repeat(60)}

CHAT & INTERACTION:
  /verma chat [text]          Start a chat session
  /verma vibe "description"   Vibecode an application

BUILDING:
  /verma build "description"  Build complete application
  /verma create "description" Alias for build

EXECUTION:
  /verma run --project [path] Run a project
  /verma run --type node --code "console.log('hi')"

INFORMATION:
  /verma status               Show full system status
  /verma agents               List active agents
  /verma skills               List loaded skills
  /verma workflows            List workflows
  /verma llm                  Show LLM status
  /verma hpie                 Show HPIE engine status
  /verma lint [path]          Run code quality audit
  /verma sync                 Sync SpiderWeb
  /verma help                 Show this help

QUICK START:
  Just type what you want to build:
  "Build me a React dashboard with charts"
  "Create a Python API for user management"
  "Make a mobile app for tracking expenses"
`);
  }

  // -----------------------------------------------------------------------
  // HPIE Subsystem
  // -----------------------------------------------------------------------
  async initializeHPIE() {
    try {
      // 1. Core intelligence engine
      const engine = new HighPerformanceIntelligenceEngine({
        maxConcurrentTasks: parseInt(process.env.AGENTS_MAX_CONCURRENT || '10', 10),
        cacheCapacity: parseInt(process.env.HPIE_CACHE_CAPACITY || '256', 10),
        compressionLevel: parseInt(process.env.POWERUSAGE_LEVEL || '3', 10)
      });
      await engine.initialize();

      // 2. Security hardening
      const security = new SecurityHardeningModule();
      await security.initialize();

      // 3. Zero-hallucination verification
      const verification = new ZeroHallucinationFramework({
        confidenceThreshold: parseFloat(process.env.HPIE_CONFIDENCE_THRESHOLD || '0.6')
      });

      // 4. Multi-agent autonomous swarm
      const swarm = new AgentSwarm({
        maxConcurrentAgents: parseInt(process.env.AGENTS_MAX_CONCURRENT || '10', 10)
      });

      // 5. Platform bridge
      const platform = new PlatformBridge();
      const platformResult = await platform.detectAndInitialize(this);

      // 6. Anti-bloat protocol
      const antiBloat = new AntiBloatProtocol(process.cwd());

      // Register existing agents in IAM
      for (const [id, agent] of this.agents) {
        const role = agent.role === 'central_brain' ? 'orchestrator'
          : agent.role === 'auditor' ? 'auditor'
          : 'specialist';
        security.registerAgent(id, role);
      }

      // Register intelligence engine subsystems
      engine.registerSubsystem('verification', async (payload) => {
        return verification.verify(payload.text, payload.context);
      });
      engine.registerSubsystem('security_gate', async (payload) => {
        return security.gate(payload.agentId, payload.permission, payload.input);
      });

      // 7. Code Quality Engine (lint enforcement)
      const quality = new CodeQualityEngine({
        enforcement: process.env.LINT_ENFORCEMENT || 'strict',
        autoFix: process.env.LINT_AUTO_FIX === 'true',
        threshold: parseInt(process.env.LINT_THRESHOLD || '100', 10)
      });

      // Register quality_check subsystem in intelligence engine
      engine.registerSubsystem('quality_check', async (payload) => {
        return quality.lint(payload.targetPath || process.cwd());
      });

      // Register code_quality_enforcer in IAM
      security.registerAgent('code_quality_enforcer', 'orchestrator');

      this.hpie = { engine, security, verification, swarm, platform, antiBloat, quality };

      console.log('  ✓ Intelligence Engine initialized');
      console.log('  ✓ Security Hardening active (AES-256-GCM)');
      console.log('  ✓ Zero-Hallucination Framework active');
      console.log('  ✓ Multi-Agent Swarm ready (Critic/Optimizer/Executor)');
      console.log(`  ✓ Platform Bridge: ${platformResult.platform}`);
      console.log('  ✓ Anti-Bloat Protocol active');
      console.log('  ✓ Code Quality Engine active (lint enforcement)');

    } catch (error) {
      console.error('  ⚠️  HPIE initialization error (non-fatal):', error.message);
      this.hpie = null;
    }
  }

  showHPIEStatus() {
    if (!this.hpie) {
      console.log('\n⚠️  HPIE not initialized');
      return { status: 'offline' };
    }

    const engineReport = this.hpie.engine.getPerformanceReport();
    const securityStatus = this.hpie.security.getStatus();
    const verificationStats = this.hpie.verification.getStats();
    const swarmStats = this.hpie.swarm.getStats();
    const platformStatus = this.hpie.platform.getStatus();
    const bloatAnalysis = this.hpie.antiBloat.analyze();

    console.log('\n⚡ HPIE - High-Performance Intelligence Engine');
    console.log('='.repeat(60));

    console.log('\n  ENGINE:');
    console.log(`    Uptime: ${engineReport.engine.uptime}`);
    console.log(`    Tasks: ${engineReport.tasks.completed} completed, ${engineReport.tasks.failed} failed`);
    console.log(`    Throughput: ${engineReport.tasks.throughput}`);
    console.log(`    Cache hit rate: ${engineReport.cache.hitRate}`);
    console.log(`    Object pool hit rate: ${engineReport.objectPool.hitRate}`);

    console.log('\n  SECURITY:');
    console.log(`    Identities: ${securityStatus.iam.identities}`);
    console.log(`    Active sessions: ${securityStatus.iam.activeSessions}`);
    console.log(`    Encryption: ${securityStatus.encryption.algorithm} (${securityStatus.encryption.keyLength}-bit)`);

    console.log('\n  VERIFICATION:');
    console.log(`    Total: ${verificationStats.totalVerifications}`);
    console.log(`    Pass rate: ${verificationStats.passRate}`);

    console.log('\n  MULTI-AGENT SWARM:');
    console.log(`    Dispatched: ${swarmStats.totalDispatched}`);
    console.log(`    Roles: ${swarmStats.roles.join(', ')}`);

    console.log('\n  PLATFORM:');
    console.log(`    Active: ${platformStatus.activePlatform}`);
    console.log(`    Detected: ${platformStatus.detected.join(', ') || 'local only'}`);

    console.log('\n  ANTI-BLOAT:');
    console.log(`    Score: ${bloatAnalysis.score.value}/100 (${bloatAnalysis.score.grade} - ${bloatAnalysis.score.label})`);
    console.log(`    Memory: ${bloatAnalysis.memoryFootprint.heapUsedMB}MB / ${bloatAnalysis.memoryFootprint.heapTotalMB}MB`);

    const qualityStatus = this.hpie.quality ? this.hpie.quality.getStatus() : null;
    if (qualityStatus) {
      console.log('\n  CODE QUALITY:');
      console.log(`    Enforcement: ${qualityStatus.enforcement}`);
      console.log(`    Auto-fix: ${qualityStatus.autoFix}`);
      console.log(`    Audits run: ${qualityStatus.auditsRun}`);
      console.log(`    Gate threshold: ${qualityStatus.gateThreshold}`);
    }

    return {
      engine: engineReport,
      security: securityStatus,
      verification: verificationStats,
      swarm: swarmStats,
      platform: platformStatus,
      bloat: bloatAnalysis.score,
      quality: qualityStatus
    };
  }

  async runLint(args = {}) {
    if (!this.hpie?.quality) {
      console.log('\n⚠️  Code Quality Engine not initialized');
      return { status: 'offline' };
    }

    const targetPath = args.path || args.text || process.cwd();
    console.log(`\n🔍 Running lint on: ${targetPath}`);

    try {
      const result = await this.hpie.quality.fullAudit(targetPath);
      console.log(`\n📊 Quality Report: ${result.report.grade} (${result.report.score}/100)`);
      console.log(`   Errors: ${result.report.totalErrors} | Warnings: ${result.report.totalWarnings}`);
      console.log(`   Gate: ${result.gate.passed ? '✅ PASSED' : '❌ BLOCKED'}`);

      if (result.report.checks.length > 0) {
        console.log('\n   Checks:');
        for (const check of result.report.checks) {
          const icon = check.passed ? '✓' : '✗';
          console.log(`     ${icon} ${check.tool}: ${check.errors} errors, ${check.warnings} warnings`);
        }
      }

      return result;
    } catch (error) {
      console.error(`\n❌ Lint failed: ${error.message}`);
      return { error: error.message };
    }
  }

  // Legacy compatibility
  async analyze(target) {
    return this.handleCommand('analyze', { target });
  }

  async plan(description) {
    return this.startBuild({ description });
  }

  async build(spec) {
    return this.startVibecoding({ description: spec });
  }

  async test(target) {
    return this.handleCommand('test', { target });
  }
}

// Auto-start
if (require.main === module) {
  const orchestrator = new EnhancedVermaOrchestrator();
  orchestrator.initialize().catch(console.error);
}

module.exports = EnhancedVermaOrchestrator;
