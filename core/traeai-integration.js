/**
 * TRAE.AI Integration Module
 * Enables MR.VERMA to run natively on TRAE.AI platform
 */

class TraeAIIntegration {
  constructor(orchestrator) {
    this.orchestrator = orchestrator;
    this.initialized = false;
    this.commands = new Map();
  }

  async initialize() {
    console.log('🔌 Initializing TRAE.AI Integration...');

    // Check if we're running in TRAE.AI environment
    if (!this.isTraeEnvironment()) {
      console.log('  ℹ️  Not in TRAE.AI environment, skipping TRAE integration');
      return false;
    }

    try {
      // Register MR.VERMA with TRAE adapter
      await this.registerWithTrae();
      
      // Setup command handlers
      this.setupCommandHandlers();
      
      // Configure workflows for TRAE
      this.configureWorkflows();
      
      this.initialized = true;
      console.log('  ✅ TRAE.AI integration initialized');
      return true;
    } catch (error) {
      console.error('  ❌ TRAE.AI integration failed:', error.message);
      return false;
    }
  }

  isTraeEnvironment() {
    return !!(
      process.env.TRAE_AI_ENV ||
      process.env.TRAE_ENV ||
      (typeof traeadapter !== 'undefined') ||
      fs.existsSync('.trae')
    );
  }

  async registerWithTrae() {
    const registrationData = {
      name: 'mrverma',
      displayName: 'MR.VERMA SpiderWeb',
      version: '2.0.0',
      description: 'Synchronized Intelligence Grid with 12+ specialized agents',
      
      capabilities: [
        'code-generation',
        'code-review',
        'architecture-design',
        'security-audit',
        'testing',
        'deployment',
        'optimization',
        'documentation'
      ],

      agents: this.getAgentsForTrae(),
      
      commands: this.getCommandsForTrae(),
      
      hooks: {
        onProjectOpen: this.onProjectOpen.bind(this),
        onFileChange: this.onFileChange.bind(this),
        onCommand: this.onCommand.bind(this)
      }
    };

    // Register with TRAE adapter if available
    if (typeof traeadapter !== 'undefined') {
      await traeadapter.register(registrationData);
    }

    console.log('  ✓ Registered with TRAE.AI');
  }

  getAgentsForTrae() {
    return [
      {
        id: 'orchestrator',
        name: 'SpiderWeb Orchestrator',
        role: 'central-coordinator',
        description: 'Main coordination hub'
      },
      {
        id: 'frontend_specialist',
        name: 'Frontend Specialist',
        role: 'developer',
        description: 'React, Vue, Angular expert'
      },
      {
        id: 'backend_specialist',
        name: 'Backend Specialist',
        role: 'developer',
        description: 'Node.js, Python, API design'
      },
      {
        id: 'security_auditor',
        name: 'Security Auditor',
        role: 'security',
        description: 'Security analysis and audits'
      },
      {
        id: 'architect',
        name: 'Senior Architect',
        role: 'architect',
        description: 'System design and planning'
      },
      {
        id: 'test_engineer',
        name: 'Test Engineer',
        role: 'qa',
        description: 'Testing and quality assurance'
      }
    ];
  }

  getCommandsForTrae() {
    return [
      {
        name: 'verma.analyze',
        description: 'Analyze code for issues',
        args: ['target'],
        handler: (args) => this.orchestrator.analyze(args.target)
      },
      {
        name: 'verma.plan',
        description: 'Create project plan',
        args: ['description'],
        handler: (args) => this.orchestrator.plan(args.description)
      },
      {
        name: 'verma.build',
        description: 'Build feature or component',
        args: ['specification'],
        handler: (args) => this.orchestrator.build(args.specification)
      },
      {
        name: 'verma.test',
        description: 'Run tests',
        args: ['target'],
        handler: (args) => this.orchestrator.test(args.target)
      },
      {
        name: 'verma.secure',
        description: 'Run security audit',
        args: ['target'],
        handler: (args) => this.runSecurityAudit(args.target)
      },
      {
        name: 'verma.optimize',
        description: 'Optimize performance',
        args: ['target'],
        handler: (args) => this.runOptimization(args.target)
      },
      {
        name: 'verma.status',
        description: 'Show system status',
        args: [],
        handler: () => this.orchestrator.getStatus()
      }
    ];
  }

  setupCommandHandlers() {
    // Register command handlers
    for (const cmd of this.getCommandsForTrae()) {
      this.commands.set(cmd.name, cmd.handler);
    }
  }

  configureWorkflows() {
    // Configure TRAE-specific workflow settings
    this.traeWorkflows = {
      onSave: 'code_review',
      onBuild: 'security_audit',
      onDeploy: 'deployment'
    };
  }

  async onProjectOpen(project) {
    console.log('📂 TRAE Project Opened:', project.name);
    
    // Initialize MR.VERMA for this project
    await this.orchestrator.initialize();
    
    // Sync SpiderWeb
    if (this.orchestrator.registry) {
      await this.orchestrator.registry.syncSpiderWeb();
    }
  }

  async onFileChange(file, changeType) {
    console.log(`📝 File ${changeType}:`, file.path);
    
    // Trigger appropriate workflows based on file type
    if (changeType === 'save') {
      const ext = file.path.split('.').pop();
      
      if (['js', 'ts', 'jsx', 'tsx', 'py', 'go'].includes(ext)) {
        // Code file - run code review
        await this.orchestrator.analyze(file.path);
      }
    }
  }

  async onCommand(command, args) {
    console.log('⚡ TRAE Command:', command);
    
    const handler = this.commands.get(command);
    if (handler) {
      return await handler(args);
    }
    
    // Fallback to orchestrator
    return await this.orchestrator.handleCommand(command, args);
  }

  async runSecurityAudit(target) {
    const workflowEngine = this.orchestrator.workflowEngine;
    if (workflowEngine) {
      return await workflowEngine.executeWorkflow('security_audit', { target });
    }
    return { status: 'error', message: 'Workflow engine not available' };
  }

  async runOptimization(target) {
    const workflowEngine = this.orchestrator.workflowEngine;
    if (workflowEngine) {
      return await workflowEngine.executeWorkflow('optimization', { target });
    }
    return { status: 'error', message: 'Workflow engine not available' };
  }

  // TRAE-specific utilities
  async getTraeContext() {
    if (typeof traeadapter !== 'undefined' && traeadapter.getContext) {
      return await traeadapter.getContext();
    }
    return null;
  }

  async showTraeNotification(message, type = 'info') {
    if (typeof traeadapter !== 'undefined' && traeadapter.showNotification) {
      await traeadapter.showNotification(message, type);
    }
  }

  getStatus() {
    return {
      initialized: this.initialized,
      commands: this.commands.size,
      workflows: Object.keys(this.traeWorkflows || {}).length
    };
  }
}

module.exports = TraeAIIntegration;
