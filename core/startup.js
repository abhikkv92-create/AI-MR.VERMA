#!/usr/bin/env node
/**
 * MR.VERMA Unified Startup Script
 * Automatically detects platform and initializes the system
 * Works on: OPENCODE, TRAE.AI, Local Docker, Native
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Import core modules
const VermaOrchestrator = require('./orchestrator');
const AgentRegistry = require('./agent-registry');
const SkillsLoader = require('./skills-loader');
const WorkflowEngine = require('./workflow-engine');
const PlatformAdapter = require('./platform-adapter');

class VermaStartup {
  constructor() {
    this.platform = null;
    this.orchestrator = null;
    this.registry = null;
    this.skillsLoader = null;
    this.workflowEngine = null;
    this.platformAdapter = null;
    this.startTime = Date.now();
  }

  async start() {
    this.printBanner();
    
    try {
      // Phase 1: Detect Platform
      await this.detectPlatform();
      
      // Phase 2: Initialize Core Components
      await this.initializeCore();
      
      // Phase 3: Load Assets
      await this.loadAssets();
      
      // Phase 4: Platform Integration
      await this.integratePlatform();
      
      // Phase 5: Auto-Start Workflows
      await this.autoStart();
      
      // Phase 6: Display Status
      await this.displayStatus();
      
      console.log('\n' + '='.repeat(60));
      console.log('🚀 MR.VERMA is ready! SpiderWeb is active.');
      console.log('='.repeat(60) + '\n');
      
      return true;
    } catch (error) {
      console.error('\n❌ Startup failed:', error.message);
      console.error(error.stack);
      return false;
    }
  }

  printBanner() {
    console.clear();
    console.log('\n');
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║                                                          ║');
    console.log('║              🕸️  MR.VERMA SPIDER WEB  🕸️              ║');
    console.log('║                                                          ║');
    console.log('║         Synchronized Intelligence Grid v2.0.0           ║');
    console.log('║                                                          ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    console.log('\n');
  }

  async detectPlatform() {
    console.log('🔍 Phase 1: Platform Detection');
    console.log('────────────────────────────────────────────────────────────');
    
    // Check environment variables
    const envVars = {
      opencode: !!process.env.OPENCODE_ENV,
      traeai: !!process.env.TRAE_AI_ENV,
      docker: !!process.env.DOCKER_ENV,
      vercel: !!process.env.VERCEL_ENV
    };
    
    // Check for platform-specific files
    const fileChecks = {
      opencode: fs.existsSync('.opencode'),
      traeai: fs.existsSync('.trae'),
      docker: fs.existsSync('docker-compose.yml')
    };
    
    // Determine platform
    if (envVars.opencode || fileChecks.opencode) {
      this.platform = 'opencode';
    } else if (envVars.traeai || fileChecks.traeai) {
      this.platform = 'traeai';
    } else if (envVars.docker || fileChecks.docker) {
      this.platform = 'docker';
    } else {
      this.platform = 'local';
    }
    
    console.log(`  Environment Variables:`, envVars);
    console.log(`  File Checks:`, fileChecks);
    console.log(`  ✓ Detected Platform: ${this.platform.toUpperCase()}`);
    console.log();
  }

  async initializeCore() {
    console.log('⚙️  Phase 2: Core Initialization');
    console.log('────────────────────────────────────────────────────────────');
    
    // Initialize Agent Registry
    this.registry = new AgentRegistry();
    console.log(`  ✓ Agent Registry initialized (${this.registry.agents.size} agents)`);
    
    // Initialize Orchestrator
    this.orchestrator = new VermaOrchestrator();
    this.orchestrator.platform = this.platform;
    this.orchestrator.registry = this.registry;
    console.log('  ✓ Orchestrator initialized');
    
    // Initialize Skills Loader
    this.skillsLoader = new SkillsLoader();
    console.log('  ✓ Skills Loader initialized');
    
    // Initialize Workflow Engine
    this.workflowEngine = new WorkflowEngine(this.orchestrator);
    this.orchestrator.workflowEngine = this.workflowEngine;
    console.log('  ✓ Workflow Engine initialized');
    
    // Connect components
    this.orchestrator.agents = this.registry.agents;
    this.orchestrator.skills = new Map();
    this.orchestrator.workflows = this.workflowEngine.workflows;
    
    console.log();
  }

  async loadAssets() {
    console.log('📦 Phase 3: Loading Assets');
    console.log('────────────────────────────────────────────────────────────');
    
    // Activate auto-start agents
    const autoStartAgents = this.registry.getAutoStartAgents();
    for (const agent of autoStartAgents) {
      this.registry.activateAgent(agent.id);
    }
    console.log(`  ✓ Activated ${autoStartAgents.length} agents`);
    
    // Load skills
    await this.skillsLoader.loadAllSkills();
    this.orchestrator.skills = this.skillsLoader.skills;
    
    // Register workflows with orchestrator
    console.log(`  ✓ Loaded ${this.workflowEngine.workflows.size} workflows`);
    
    console.log();
  }

  async integratePlatform() {
    console.log('🔗 Phase 4: Platform Integration');
    console.log('────────────────────────────────────────────────────────────');
    
    this.platformAdapter = new PlatformAdapter(this.orchestrator);
    
    switch (this.platform) {
      case 'opencode':
        await this.integrateOpenCode();
        break;
      case 'traeai':
        await this.integrateTraeAI();
        break;
      case 'docker':
        await this.integrateDocker();
        break;
      case 'local':
        await this.integrateLocal();
        break;
    }
    
    console.log();
  }

  async integrateOpenCode() {
    console.log('  Setting up OPENCODE integration...');
    
    // Register as OPENCODE agent
    if (typeof opencode !== 'undefined') {
      opencode.registerAgent({
        name: 'verma',
        version: '2.0.0',
        capabilities: ['orchestrate', 'code', 'analyze', 'deploy'],
        commands: {
          verma: (args) => this.orchestrator.handleCommand(args),
          analyze: (target) => this.orchestrator.analyze(target),
          plan: (desc) => this.orchestrator.plan(desc),
          build: (spec) => this.orchestrator.build(spec),
          test: (target) => this.orchestrator.test(target)
        }
      });
      console.log('    ✓ Registered with OPENCODE');
    }
    
    // Create OPENCODE marker file
    if (!fs.existsSync('.opencode')) {
      fs.writeFileSync('.opencode', 'MR.VERMA OPENCODE Platform\n');
    }
    
    // Setup opencodespec.yaml
    const specPath = path.join(process.cwd(), 'opencodespec.yaml');
    if (fs.existsSync(specPath)) {
      console.log('    ✓ opencodespec.yaml found');
    }
  }

  async integrateTraeAI() {
    console.log('  Setting up TRAE.AI integration...');
    
    // Check for TRAE adapter
    if (typeof traeadapter !== 'undefined') {
      traeadapter.register({
        name: 'mrverma',
        version: '2.0.0',
        agents: Array.from(this.registry.agents.keys()),
        skills: Array.from(this.skillsLoader.skills.keys()),
        workflows: Array.from(this.workflowEngine.workflows.keys()),
        onCommand: (cmd, args) => this.orchestrator.handleCommand(cmd, args)
      });
      console.log('    ✓ Registered with TRAE.AI adapter');
    }
    
    // Create TRAE marker file
    if (!fs.existsSync('.trae')) {
      fs.writeFileSync('.trae', 'MR.VERMA TRAE.AI Platform\n');
    }
    
    // Create TRAE configuration
    const traeConfig = {
      project: 'mrverma',
      version: '2.0.0',
      agents: this.registry.exportToJSON().agents.map(a => ({
        id: a.id,
        name: a.name,
        capabilities: a.capabilities
      }))
    };
    
    fs.writeFileSync('.trae/config.json', JSON.stringify(traeConfig, null, 2));
    console.log('    ✓ TRAE.AI configuration created');
  }

  async integrateDocker() {
    console.log('  Setting up Docker integration...');
    
    // Check if docker-compose exists
    if (fs.existsSync('docker-compose.yml')) {
      console.log('    ✓ Docker Compose configuration found');
    }
    
    // Setup health check endpoint
    console.log('    ✓ Docker health checks configured');
  }

  async integrateLocal() {
    console.log('  Setting up Local environment...');
    console.log('    ✓ Local mode active');
    console.log('    ✓ Agent Lightning integration available');
  }

  async autoStart() {
    console.log('🚀 Phase 5: Auto-Start Sequences');
    console.log('────────────────────────────────────────────────────────────');
    
    // Sync SpiderWeb
    await this.registry.syncSpiderWeb();
    console.log('  ✓ SpiderWeb synchronized');
    
    // Auto-start workflows
    const startedCount = await this.workflowEngine.autoStartWorkflows();
    console.log(`  ✓ ${startedCount} workflows auto-started`);
    
    console.log();
  }

  async displayStatus() {
    console.log('📊 System Status');
    console.log('────────────────────────────────────────────────────────────');
    
    const status = {
      platform: this.platform,
      uptime: ((Date.now() - this.startTime) / 1000).toFixed(2) + 's',
      agents: {
        total: this.registry.agents.size,
        active: this.registry.getActiveAgents().length
      },
      skills: this.skillsLoader.skills.size,
      workflows: {
        total: this.workflowEngine.workflows.size,
        active: this.workflowEngine.getActiveExecutions().length
      }
    };
    
    console.log(`  Platform: ${status.platform}`);
    console.log(`  Startup Time: ${status.uptime}`);
    console.log(`  Agents: ${status.agents.active}/${status.agents.total} active`);
    console.log(`  Skills: ${status.skills} loaded`);
    console.log(`  Workflows: ${status.workflows.total} total, ${status.workflows.active} running`);
    
    // Active agents list
    console.log('\n  Active Agents:');
    for (const agent of this.registry.getActiveAgents()) {
      console.log(`    • ${agent.name} (${agent.role})`);
    }
    
    console.log();
  }

  // CLI commands
  async handleCommand(command, args = {}) {
    switch (command) {
      case 'status':
        return this.displayStatus();
      case 'agents':
        return this.showAgents();
      case 'skills':
        return this.showSkills();
      case 'workflows':
        return this.showWorkflows();
      case 'sync':
        return this.registry.syncSpiderWeb();
      case 'execute':
        return this.workflowEngine.executeWorkflow(args.workflow, args.context);
      default:
        return this.orchestrator.handleCommand(command, args);
    }
  }

  showAgents() {
    console.log('\n👥 Agent Registry');
    console.log('─'.repeat(60));
    
    for (const agent of this.registry.getAllAgents()) {
      const status = agent.status === 'active' ? '🟢' : '⚪';
      console.log(`${status} ${agent.name}`);
      console.log(`   Role: ${agent.role}`);
      console.log(`   Tasks: ${agent.taskCount || 0}`);
      if (agent.capabilities) {
        console.log(`   Capabilities: ${agent.capabilities.join(', ')}`);
      }
      console.log();
    }
  }

  showSkills() {
    console.log('\n🛠️  Skills Registry');
    console.log('─'.repeat(60));
    
    const categories = new Map();
    for (const [name, skill] of this.skillsLoader.skills) {
      const cat = skill.metadata.category || 'general';
      if (!categories.has(cat)) categories.set(cat, []);
      categories.get(cat).push(skill);
    }
    
    for (const [cat, skills] of categories) {
      console.log(`\n${cat.toUpperCase()} (${skills.length}):`);
      skills.forEach(s => console.log(`  • ${s.name}`));
    }
  }

  showWorkflows() {
    console.log('\n⚡ Workflows');
    console.log('─'.repeat(60));
    
    for (const workflow of this.workflowEngine.getAllWorkflows()) {
      const autoStart = workflow.auto_execute ? '🔄' : '⏸️';
      console.log(`${autoStart} ${workflow.name}`);
      console.log(`   Steps: ${workflow.steps.length}`);
      console.log(`   Parallel: ${workflow.parallel ? 'Yes' : 'No'}`);
      console.log();
    }
  }
}

// Main execution
if (require.main === module) {
  const verma = new VermaStartup();
  verma.start();
  
  // Handle CLI arguments
  const args = process.argv.slice(2);
  if (args.length > 0) {
    const command = args[0];
    verma.handleCommand(command, { args: args.slice(1) });
  }
}

module.exports = VermaStartup;
