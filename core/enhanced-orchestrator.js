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
    
    console.log('\n✅ All enhanced features loaded');
  }

  async loadEnhancedWorkflows() {
    // Add vibecoding workflow
    this.workflowEngine.registerWorkflow('vibecoding', {
      name: 'Vibecoding Workflow',
      description: 'Natural language to application development',
      steps: [
        { id: 'analyze', type: 'action', action: 'analyze_requirements' },
        { id: 'design', type: 'action', action: 'design_architecture' },
        { id: 'generate', type: 'action', action: 'generate_code' },
        { id: 'assemble', type: 'action', action: 'assemble_project' },
        { id: 'validate', type: 'validation', action: 'validate_project' }
      ],
      auto_execute: false,
      parallel: false
    });

    // Add build workflow
    this.workflowEngine.registerWorkflow('build_app', {
      name: 'Application Build',
      description: 'Complete application build process',
      steps: [
        { id: 'plan', type: 'agent_task', agent: 'architect', action: 'create_plan' },
        { id: 'vibe', type: 'action', action: 'vibecoding' },
        { id: 'code', type: 'agent_task', agent: 'vibecoder', action: 'generate' },
        { id: 'review', type: 'agent_task', agent: 'security_auditor', action: 'review' },
        { id: 'test', type: 'agent_task', agent: 'test_engineer', action: 'test' }
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
        sandbox: this.sandbox ? this.sandbox.getStatus() : 'offline'
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
  /verma sync                 Sync SpiderWeb
  /verma help                 Show this help

QUICK START:
  Just type what you want to build:
  "Build me a React dashboard with charts"
  "Create a Python API for user management"
  "Make a mobile app for tracking expenses"
`);
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
