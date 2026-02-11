#!/usr/bin/env node
/**
 * MR.VERMA Agent Registry
 * Manages agent definitions, capabilities, and interconnections
 */

const fs = require('fs');
const path = require('path');

class AgentRegistry {
  constructor() {
    this.agents = new Map();
    this.agentConnections = new Map();
    this.capabilities = new Map();
    this.initializeCoreAgents();
  }

  initializeCoreAgents() {
    const coreAgents = [
      {
        id: 'orchestrator',
        name: 'SpiderWeb Orchestrator',
        role: 'central_brain',
        description: 'Central coordination hub for all agents',
        capabilities: ['route', 'sync', 'orchestrate', 'coordinate'],
        connections: ['all'],
        priority: 100,
        auto_start: true
      },
      {
        id: 'frontend_specialist',
        name: 'Frontend Specialist',
        role: 'developer',
        description: 'Expert in React, Vue, Angular, and modern frontend frameworks',
        capabilities: ['react', 'vue', 'angular', 'typescript', 'css', 'html', 'ui', 'ux'],
        connections: ['backend_specialist', 'test_engineer', 'security_auditor'],
        priority: 80,
        auto_start: true
      },
      {
        id: 'backend_specialist',
        name: 'Backend Specialist',
        role: 'developer',
        description: 'Expert in Node.js, Python, Go, and backend architecture',
        capabilities: ['nodejs', 'python', 'go', 'api', 'database', 'server'],
        connections: ['frontend_specialist', 'architect', 'security_auditor'],
        priority: 80,
        auto_start: true
      },
      {
        id: 'security_auditor',
        name: 'Security Auditor',
        role: 'auditor',
        description: 'Security analysis and vulnerability scanning expert',
        capabilities: ['security', 'vulnerability_scan', 'audit', 'penetration_test'],
        connections: ['all'],
        priority: 90,
        auto_start: true
      },
      {
        id: 'architect',
        name: 'Senior Architect',
        role: 'planner',
        description: 'System design and architecture planning',
        capabilities: ['design', 'architecture', 'planning', 'c4_diagrams'],
        connections: ['frontend_specialist', 'backend_specialist', 'devops_engineer'],
        priority: 85,
        auto_start: true
      },
      {
        id: 'test_engineer',
        name: 'Test Engineer',
        role: 'qa',
        description: 'Testing strategies and quality assurance',
        capabilities: ['testing', 'qa', 'automation', 'unit_test', 'integration_test'],
        connections: ['frontend_specialist', 'backend_specialist'],
        priority: 75,
        auto_start: true
      },
      {
        id: 'devops_engineer',
        name: 'DevOps Engineer',
        role: 'operations',
        description: 'CI/CD, deployment, and infrastructure',
        capabilities: ['deployment', 'ci_cd', 'docker', 'kubernetes', 'aws', 'gcp'],
        connections: ['architect', 'backend_specialist'],
        priority: 70,
        auto_start: true
      },
      {
        id: 'product_manager',
        name: 'Product Manager',
        role: 'management',
        description: 'Product strategy and requirement analysis',
        capabilities: ['requirements', 'roadmap', 'prioritization', 'user_stories'],
        connections: ['architect', 'orchestrator'],
        priority: 60,
        auto_start: false
      },
      {
        id: 'performance_optimizer',
        name: 'Performance Optimizer',
        role: 'optimizer',
        description: 'Performance tuning and optimization',
        capabilities: ['performance', 'optimization', 'memory', 'profiling', 'token_efficiency'],
        connections: ['frontend_specialist', 'backend_specialist'],
        priority: 75,
        auto_start: true
      },
      {
        id: 'documentation_writer',
        name: 'Documentation Writer',
        role: 'writer',
        description: 'Technical documentation and guides',
        capabilities: ['docs', 'readme', 'guides', 'api_docs'],
        connections: ['all'],
        priority: 50,
        auto_start: false
      },
      {
        id: 'ai_specialist',
        name: 'AI Specialist',
        role: 'ai_expert',
        description: 'Machine learning and AI integration',
        capabilities: ['ml', 'ai', 'models', 'neural_networks', 'nlp'],
        connections: ['backend_specialist', 'architect'],
        priority: 70,
        auto_start: false
      },
      {
        id: 'mobile_developer',
        name: 'Mobile Developer',
        role: 'mobile_dev',
        description: 'iOS and Android development',
        capabilities: ['ios', 'android', 'react_native', 'flutter', 'swift', 'kotlin'],
        connections: ['frontend_specialist', 'backend_specialist'],
        priority: 70,
        auto_start: false
      }
    ];

    for (const agent of coreAgents) {
      this.registerAgent(agent);
    }

    console.log(`✅ Registered ${this.agents.size} core agents`);
  }

  registerAgent(agentConfig) {
    if (!agentConfig.id) {
      throw new Error('Agent must have an ID');
    }

    const agent = {
      ...agentConfig,
      registeredAt: new Date().toISOString(),
      status: 'registered',
      lastActive: null,
      taskCount: 0
    };

    this.agents.set(agentConfig.id, agent);
    
    // Register capabilities
    if (agent.capabilities) {
      for (const cap of agent.capabilities) {
        if (!this.capabilities.has(cap)) {
          this.capabilities.set(cap, []);
        }
        this.capabilities.get(cap).push(agent.id);
      }
    }

    // Register connections
    if (agent.connections) {
      this.agentConnections.set(agent.id, agent.connections);
    }

    return agent;
  }

  getAgent(id) {
    return this.agents.get(id);
  }

  getAllAgents() {
    return Array.from(this.agents.values());
  }

  getActiveAgents() {
    return this.getAllAgents().filter(a => a.status === 'active');
  }

  getAutoStartAgents() {
    return this.getAllAgents().filter(a => a.auto_start);
  }

  findAgentsByCapability(capability) {
    const agentIds = this.capabilities.get(capability) || [];
    return agentIds.map(id => this.agents.get(id)).filter(a => a);
  }

  findAgentsByRole(role) {
    return this.getAllAgents().filter(a => a.role === role);
  }

  activateAgent(agentId) {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.status = 'active';
      agent.lastActive = new Date().toISOString();
      console.log(`🟢 Agent activated: ${agent.name}`);
      return true;
    }
    return false;
  }

  deactivateAgent(agentId) {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.status = 'inactive';
      console.log(`🔴 Agent deactivated: ${agent.name}`);
      return true;
    }
    return false;
  }

  getAgentConnections(agentId) {
    const connections = this.agentConnections.get(agentId) || [];
    if (connections.includes('all')) {
      return this.getAllAgents().map(a => a.id).filter(id => id !== agentId);
    }
    return connections;
  }

  async syncSpiderWeb() {
    console.log('🕸️  Synchronizing SpiderWeb connections...');
    
    const activeAgents = this.getActiveAgents();
    const connections = new Map();

    for (const agent of activeAgents) {
      const agentConns = this.getAgentConnections(agent.id);
      connections.set(agent.id, agentConns);
    }

    console.log(`  Active agents: ${activeAgents.length}`);
    console.log(`  Connection map generated`);

    return connections;
  }

  routeTask(task, context = {}) {
    console.log(`🛣️  Routing task: ${task.type}`);

    // Capability-based routing
    const capabilityMap = {
      'frontend': 'frontend_specialist',
      'react': 'frontend_specialist',
      'vue': 'frontend_specialist',
      'ui': 'frontend_specialist',
      'backend': 'backend_specialist',
      'api': 'backend_specialist',
      'security': 'security_auditor',
      'audit': 'security_auditor',
      'architecture': 'architect',
      'design': 'architect',
      'testing': 'test_engineer',
      'qa': 'test_engineer',
      'deploy': 'devops_engineer',
      'infrastructure': 'devops_engineer',
      'performance': 'performance_optimizer',
      'optimize': 'performance_optimizer',
      'mobile': 'mobile_developer',
      'ios': 'mobile_developer',
      'android': 'mobile_developer'
    };

    const targetAgentId = capabilityMap[task.type] || 'orchestrator';
    const targetAgent = this.agents.get(targetAgentId);

    if (targetAgent) {
      targetAgent.taskCount++;
      targetAgent.lastActive = new Date().toISOString();
      
      return {
        success: true,
        agentId: targetAgentId,
        agentName: targetAgent.name,
        task,
        context
      };
    }

    return {
      success: false,
      error: 'No suitable agent found',
      task
    };
  }

  getStatus() {
    return {
      total: this.agents.size,
      active: this.getActiveAgents().length,
      capabilities: this.capabilities.size,
      connections: this.agentConnections.size,
      agents: Array.from(this.agents.values()).map(a => ({
        id: a.id,
        name: a.name,
        status: a.status,
        taskCount: a.taskCount
      }))
    };
  }

  exportToJSON() {
    return {
      agents: Array.from(this.agents.values()),
      connections: Object.fromEntries(this.agentConnections),
      capabilities: Object.fromEntries(this.capabilities),
      exportedAt: new Date().toISOString()
    };
  }

  exportToYAML() {
    const data = this.exportToJSON();
    // Simple YAML formatting (you might want to use a proper YAML library)
    let yaml = '# MR.VERMA Agent Registry\n\n';
    yaml += `agents:\n`;
    for (const agent of data.agents) {
      yaml += `  ${agent.id}:\n`;
      yaml += `    name: ${agent.name}\n`;
      yaml += `    role: ${agent.role}\n`;
      yaml += `    status: ${agent.status}\n`;
      if (agent.capabilities) {
        yaml += `    capabilities: [${agent.capabilities.join(', ')}]\n`;
      }
    }
    return yaml;
  }
}

// CLI usage
if (require.main === module) {
  const registry = new AgentRegistry();
  
  // Activate all auto-start agents
  for (const agent of registry.getAutoStartAgents()) {
    registry.activateAgent(agent.id);
  }
  
  // Sync SpiderWeb
  registry.syncSpiderWeb();
  
  // Print status
  console.log('\n📊 Agent Registry Status:');
  console.log(JSON.stringify(registry.getStatus(), null, 2));
}

module.exports = AgentRegistry;
