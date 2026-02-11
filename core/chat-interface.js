#!/usr/bin/env node
/**
 * MR.VERMA Chat Interface System
 * Enables conversational interactions with the SpiderWeb orchestrator
 * Version: 2.0.0
 */

const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

class VermaChatInterface extends EventEmitter {
  constructor(orchestrator) {
    super();
    this.orchestrator = orchestrator;
    this.conversations = new Map();
    this.activeConversation = null;
    this.context = {
      currentProject: null,
      lastIntent: null,
      pendingActions: [],
      memory: new Map()
    };
  }

  async initialize() {
    console.log('💬 Initializing MR.VERMA Chat Interface...');
    
    // Create conversations directory
    const convDir = path.join(process.cwd(), '.verma', 'conversations');
    if (!fs.existsSync(convDir)) {
      fs.mkdirSync(convDir, { recursive: true });
    }
    
    // Load existing conversations
    await this.loadConversations();
    
    console.log('✅ Chat interface ready');
    return this;
  }

  async loadConversations() {
    const convDir = path.join(process.cwd(), '.verma', 'conversations');
    if (fs.existsSync(convDir)) {
      const files = fs.readdirSync(convDir).filter(f => f.endsWith('.json'));
      for (const file of files) {
        const convPath = path.join(convDir, file);
        const data = JSON.parse(fs.readFileSync(convPath, 'utf8'));
        this.conversations.set(data.id, data);
      }
    }
  }

  createConversation(id = null) {
    const convId = id || `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const conversation = {
      id: convId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [],
      context: {},
      project: null
    };
    
    this.conversations.set(convId, conversation);
    this.activeConversation = convId;
    
    // Add welcome message
    this.addMessage(convId, 'assistant', 
      '🕸️ **Welcome to MR.VERMA SpiderWeb**\n\n' +
      'I can help you with:\n' +
      '• **Code generation** - "Create a React component for..."\n' +
      '• **Development** - "Build a full-stack app with..."\n' +
      '• **Architecture** - "Design a system for..."\n' +
      '• **Debugging** - "Fix this error..."\n' +
      '• **Optimization** - "Make this faster..."\n\n' +
      'Just describe what you want to build, and I\'ll handle the rest!'
    );
    
    return convId;
  }

  addMessage(convId, role, content, metadata = {}) {
    const conversation = this.conversations.get(convId);
    if (!conversation) return null;
    
    const message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role,
      content,
      timestamp: new Date().toISOString(),
      metadata
    };
    
    conversation.messages.push(message);
    conversation.updatedAt = new Date().toISOString();
    
    // Save conversation
    this.saveConversation(convId);
    
    // Emit event
    this.emit('message', { convId, message });
    
    return message;
  }

  async processMessage(userMessage, convId = null) {
    const conversationId = convId || this.activeConversation || this.createConversation();
    
    // Add user message
    this.addMessage(conversationId, 'user', userMessage);
    
    // Analyze intent
    const intent = this.analyzeIntent(userMessage);
    console.log(`🎯 Detected intent: ${intent.type} (${intent.confidence}%)`);
    
    // Process based on intent
    let response;
    switch (intent.type) {
      case 'code_generation':
        response = await this.handleCodeGeneration(userMessage, intent);
        break;
      case 'vibecoding':
        response = await this.handleVibecoding(userMessage, intent);
        break;
      case 'architecture':
        response = await this.handleArchitecture(userMessage, intent);
        break;
      case 'debugging':
        response = await this.handleDebugging(userMessage, intent);
        break;
      case 'optimization':
        response = await this.handleOptimization(userMessage, intent);
        break;
      case 'general':
      default:
        response = await this.handleGeneral(userMessage, intent);
    }
    
    // Add assistant response
    this.addMessage(conversationId, 'assistant', response.content, {
      intent: intent.type,
      actions: response.actions || [],
      workflow: response.workflow
    });
    
    return {
      conversationId,
      message: response.content,
      actions: response.actions,
      workflow: response.workflow
    };
  }

  analyzeIntent(message) {
    const lowerMsg = message.toLowerCase();
    
    // Vibecoding patterns
    const vibecodingPatterns = [
      /build (me |us )?(a |an )?/i,
      /create (me |us )?(a |an )?/i,
      /make (me |us )?(a |an )?/i,
      /i want (to |a |an )?/i,
      /help me (build|create|make)/i,
      /can you (build|create|make)/i
    ];
    
    // Code generation patterns
    const codeGenPatterns = [
      /write (code|function|component)/i,
      /generate (code|function|component)/i,
      /implement/i,
      /code for/i
    ];
    
    // Architecture patterns
    const architecturePatterns = [
      /design (a |an )?system/i,
      /architecture/i,
      /blueprint/i,
      /plan (for |out )?/i
    ];
    
    // Debugging patterns
    const debuggingPatterns = [
      /fix/i,
      /debug/i,
      /error/i,
      /bug/i,
      /not working/i,
      /broken/i
    ];
    
    // Optimization patterns
    const optimizationPatterns = [
      /optimize/i,
      /improve/i,
      /make (it )?faster/i,
      /performance/i,
      /slow/i
    ];
    
    // Check patterns and calculate confidence
    const checkPatterns = (patterns) => {
      let matches = 0;
      for (const pattern of patterns) {
        if (pattern.test(message)) matches++;
      }
      return (matches / patterns.length) * 100;
    };
    
    const intents = {
      vibecoding: checkPatterns(vibecodingPatterns),
      code_generation: checkPatterns(codeGenPatterns),
      architecture: checkPatterns(architecturePatterns),
      debugging: checkPatterns(debuggingPatterns),
      optimization: checkPatterns(optimizationPatterns)
    };
    
    // Find highest confidence intent
    let bestIntent = 'general';
    let bestConfidence = 0;
    
    for (const [intent, confidence] of Object.entries(intents)) {
      if (confidence > bestConfidence && confidence > 25) {
        bestIntent = intent;
        bestConfidence = confidence;
      }
    }
    
    return {
      type: bestIntent,
      confidence: Math.round(bestConfidence),
      allIntents: intents
    };
  }

  async handleVibecoding(message, intent) {
    console.log('🎨 Entering vibecoding mode...');
    
    // Extract project requirements from message
    const requirements = this.extractRequirements(message);
    
    // Generate response
    const response = {
      content: `🎨 **Vibecoding Mode Activated**\n\n` +
        `I've understood your vision:\n` +
        `• **Project**: ${requirements.project || 'Application'}\n` +
        `• **Type**: ${requirements.type || 'Web Application'}\n` +
        `• **Stack**: ${requirements.stack || 'Modern full-stack'}\n\n` +
        `Let me orchestrate the SpiderWeb to build this for you...\n\n` +
        `**Agents activating:**\n` +
        `🤖 Architect → Designing system\n` +
        `🤖 Frontend Specialist → UI/UX\n` +
        `🤖 Backend Specialist → API & Database\n` +
        `🤖 DevOps Engineer → Deployment\n\n` +
        `⏳ Building your application...`,
      actions: [{
        type: 'execute_workflow',
        workflow: 'vibecoding',
        params: { message, requirements }
      }],
      workflow: 'vibecoding'
    };
    
    // Execute workflow asynchronously
    this.executeVibecodingWorkflow(message, requirements);
    
    return response;
  }

  async executeVibecodingWorkflow(message, requirements) {
    try {
      // Trigger the vibecoding workflow
      if (this.orchestrator && this.orchestrator.workflowEngine) {
        const result = await this.orchestrator.workflowEngine.executeWorkflow(
          'vibecoding',
          { message, requirements }
        );
        
        // Send progress update
        this.emit('progress', {
          type: 'vibecoding_complete',
          result
        });
      }
    } catch (error) {
      console.error('Vibecoding workflow error:', error);
      this.emit('error', { type: 'vibecoding', error });
    }
  }

  extractRequirements(message) {
    const requirements = {
      project: null,
      type: null,
      stack: null,
      features: []
    };
    
    // Extract project name/type
    const projectMatch = message.match(/(?:build|create|make) (?:me |us )?(?:a |an )?(\w+(?:\s+\w+){0,3})/i);
    if (projectMatch) {
      requirements.project = projectMatch[1];
    }
    
    // Detect stack preferences
    if (/react/i.test(message)) requirements.stack = 'React';
    else if (/vue/i.test(message)) requirements.stack = 'Vue';
    else if (/angular/i.test(message)) requirements.stack = 'Angular';
    else if (/next/i.test(message)) requirements.stack = 'Next.js';
    else if (/python/i.test(message)) requirements.stack = 'Python';
    else if (/node/i.test(message)) requirements.stack = 'Node.js';
    
    // Detect app type
    if (/mobile/i.test(message)) requirements.type = 'Mobile App';
    else if (/web/i.test(message)) requirements.type = 'Web App';
    else if (/api/i.test(message)) requirements.type = 'API';
    else if (/dashboard/i.test(message)) requirements.type = 'Dashboard';
    else requirements.type = 'Application';
    
    return requirements;
  }

  async handleCodeGeneration(message, intent) {
    return {
      content: `💻 **Code Generation**\n\n` +
        `I'll generate the code for you. Let me analyze the requirements...\n\n` +
        `Please specify:\n` +
        `1. What language/framework? (React, Python, etc.)\n` +
        `2. What should the code do?\n` +
        `3. Any specific requirements or constraints?`,
      actions: [],
      workflow: null
    };
  }

  async handleArchitecture(message, intent) {
    return {
      content: `🏗️ **Architecture Design**\n\n` +
        `I'll help you design the system architecture.\n\n` +
        `Let me create a comprehensive blueprint with:\n` +
        `• System components\n` +
        `• Data flow\n` +
        `• API design\n` +
        `• Database schema\n\n` +
        `Starting architecture workflow...`,
      actions: [{
        type: 'execute_workflow',
        workflow: 'architecture_design'
      }],
      workflow: 'architecture_design'
    };
  }

  async handleDebugging(message, intent) {
    return {
      content: `🐛 **Debug Mode**\n\n` +
        `I'll help you fix this issue. Let me analyze:\n\n` +
        `1. **Identify** the error\n` +
        `2. **Analyze** root cause\n` +
        `3. **Fix** the problem\n` +
        `4. **Test** the solution\n\n` +
        `Please share the error message or code that's not working.`,
      actions: [],
      workflow: 'debug'
    };
  }

  async handleOptimization(message, intent) {
    return {
      content: `⚡ **Optimization Mode**\n\n` +
        `I'll analyze and optimize your code for better performance.\n\n` +
        `Applying:\n` +
        `• Performance profiling\n` +
        `• Memory optimization\n` +
        `• Token efficiency (powerusage)\n\n` +
        `Share the code or file you'd like to optimize.`,
      actions: [],
      workflow: 'optimization'
    };
  }

  async handleGeneral(message, intent) {
    return {
      content: `🕸️ **SpiderWeb Ready**\n\n` +
        `I can help you with various development tasks:\n\n` +
        `**Available Commands:**\n` +
        `• "/build [description]" - Create an application\n` +
        `• "/code [description]" - Generate code\n` +
        `• "/design [system]" - Architecture blueprint\n` +
        `• "/fix [error]" - Debug issues\n` +
        `• "/optimize [code]" - Improve performance\n` +
        `• "/status" - Show system status\n\n` +
        `Or just describe what you want to build naturally!`,
      actions: [],
      workflow: null
    };
  }

  saveConversation(convId) {
    const conversation = this.conversations.get(convId);
    if (!conversation) return;
    
    const convDir = path.join(process.cwd(), '.verma', 'conversations');
    const convPath = path.join(convDir, `${convId}.json`);
    
    fs.writeFileSync(convPath, JSON.stringify(conversation, null, 2));
  }

  getConversation(convId) {
    return this.conversations.get(convId);
  }

  getAllConversations() {
    return Array.from(this.conversations.values())
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  }

  clearContext() {
    this.context = {
      currentProject: null,
      lastIntent: null,
      pendingActions: [],
      memory: new Map()
    };
  }
}

module.exports = VermaChatInterface;
