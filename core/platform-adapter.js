/**
 * Platform Adapter for MR.VERMA
 * Handles OPENCODE and TRAE.AI platform integrations
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class PlatformAdapter {
  constructor(orchestrator) {
    this.orchestrator = orchestrator;
    this.platform = null;
  }

  async detectAndInitialize() {
    this.platform = this.detectPlatform();
    
    switch (this.platform) {
      case 'opencode':
        return this.initializeOpenCode();
      case 'traeai':
        return this.initializeTraeAI();
      case 'local':
      default:
        return this.initializeLocal();
    }
  }

  detectPlatform() {
    // Check for OPENCODE
    if (process.env.OPENCODE_ENV || fs.existsSync('.opencode')) {
      return 'opencode';
    }
    
    // Check for TRAE.AI
    if (process.env.TRAE_AI_ENV || fs.existsSync('.trae')) {
      return 'traeai';
    }
    
    return 'local';
  }

  async initializeOpenCode() {
    console.log('🚀 Initializing OPENCODE Platform Adapter');
    
    // Load opencodespec.yaml
    const specPath = path.join(process.cwd(), 'opencodespec.yaml');
    if (fs.existsSync(specPath)) {
      const spec = yaml.load(fs.readFileSync(specPath, 'utf8'));
      
      // Register agents
      if (spec.agents) {
        for (const [key, agentConfig] of Object.entries(spec.agents)) {
          await this.registerAgent(key, agentConfig);
        }
      }
      
      // Register skills
      if (spec.skills) {
        for (const skill of spec.skills) {
          await this.registerSkill(skill);
        }
      }
      
      // Register commands
      if (spec.commands) {
        for (const [cmd, config] of Object.entries(spec.commands)) {
          await this.registerCommand(cmd, config);
        }
      }
    }
    
    return { platform: 'opencode', status: 'initialized' };
  }

  async initializeTraeAI() {
    console.log('🚀 Initializing TRAE.AI Platform Adapter');
    
    // Check for TRAE adapter
    if (typeof traeadapter !== 'undefined') {
      traeadapter.register({
        name: 'verma',
        version: '2.0.0',
        agents: this.orchestrator.agents,
        skills: this.orchestrator.skills,
        workflows: this.orchestrator.workflows
      });
    }
    
    return { platform: 'traeai', status: 'initialized' };
  }

  async initializeLocal() {
    console.log('🏠 Initializing Local Platform');
    return { platform: 'local', status: 'initialized' };
  }

  async registerAgent(name, config) {
    console.log(`  📌 Registered agent: ${name}`);
    this.orchestrator.agents.set(name, {
      ...config,
      name,
      platform: this.platform,
      registeredAt: Date.now()
    });
  }

  async registerSkill(skillConfig) {
    console.log(`  🛠️  Registered skill: ${skillConfig.name}`);
    this.orchestrator.skills.set(skillConfig.name, {
      ...skillConfig,
      platform: this.platform,
      registeredAt: Date.now()
    });
  }

  async registerCommand(name, config) {
    console.log(`  ⌨️  Registered command: ${name}`);
  }

  async executeCommand(command, args = {}) {
    console.log(`⚡ Executing on ${this.platform}: ${command}`);
    return this.orchestrator.handleCommand(command, args);
  }
}

module.exports = PlatformAdapter;
